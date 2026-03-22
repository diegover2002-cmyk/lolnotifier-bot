"""
Poller — periodic match tracking via match/v5 history.
Strategy: compare latest match_id from API against stored last_match_id.
If different → new match completed → fetch details → notify.
Works with dev API key (no spectator/summoner endpoints required).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import aiohttp

from config import ACCOUNT_CLUSTERS, DB_PATH, POLL_INTERVAL
from database import (
    get_all_pros,
    get_all_user_ids,
    get_all_users,
    update_last_match_id,
    update_pro_last_match_id,
    update_pro_last_poll_time,
    update_user_last_poll_time,
    update_user_puuid,
    update_pro_puuid,
)
from formatter import format_match_summary, format_match_summary_with_stats
from riot_account import get_account_by_riot_id
from riot_api import get_match_info, get_match_history_ids, parse_match_for_puuid

logger = logging.getLogger(__name__)

# Minimum seconds between polls for the same player
_MIN_POLL_GAP = 60


def _now_str() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def _last_poll_age(last_poll_time: str | None) -> float:
    """Seconds since last poll, or infinity if never polled."""
    if not last_poll_time:
        return float("inf")
    try:
        ts = time.mktime(time.strptime(last_poll_time, "%Y-%m-%d %H:%M:%S"))
        return time.time() - ts
    except ValueError:
        return float("inf")


async def _resolve_puuid(
    session: aiohttp.ClientSession,
    record: dict[str, Any],
) -> str | None:
    """Return cached PUUID or resolve via account/v1."""
    if record.get("puuid"):
        return record["puuid"]

    game_name = record.get("game_name") or record.get("summoner_name")
    tag_line = record.get("tag_line", "")
    region = record.get("region", "la2")

    if not game_name:
        return None

    cluster = ACCOUNT_CLUSTERS.get(region, "americas")
    account = await get_account_by_riot_id(session, cluster, game_name, tag_line)
    return account.get("puuid") if account else None


async def _send_safe(bot: Any, chat_id: int, text: str) -> None:
    try:
        await bot.send_message(chat_id, text)
    except Exception as exc:
        logger.warning("Failed to send message to %s: %s", chat_id, exc)


async def _process_player(
    session: aiohttp.ClientSession,
    bot: Any,
    record: dict[str, Any],
    *,
    notify_ids: list[int],
    is_pro: bool = False,
) -> str | None:
    """
    Poll one player. Returns the new last_match_id to store, or None if unchanged.
    notify_ids: list of Telegram chat_ids to notify.
    """
    region = record.get("region", "la2")
    puuid = await _resolve_puuid(session, record)
    if not puuid:
        logger.warning("Could not resolve PUUID for %s", record.get("summoner_name"))
        return None

    # Persist PUUID if it was just resolved
    if not record.get("puuid"):
        if is_pro:
            await update_pro_puuid(DB_PATH, record["id"], puuid)
        else:
            await update_user_puuid(DB_PATH, record["user_id"], puuid)

    match_ids = await get_match_history_ids(session, region, puuid, count=1)
    if not match_ids:
        return None

    latest_id = match_ids[0]
    stored_id = record.get("last_match_id") or ""

    if latest_id == stored_id:
        return None  # No new match

    # New match detected — fetch and parse
    match_info = await get_match_info(session, region, latest_id)
    if not match_info:
        # Still update the stored ID so we don't re-process
        return latest_id

    parsed = parse_match_for_puuid(match_info, puuid)
    if not parsed:
        return latest_id

    player_label = record.get("game_name") or record.get("summoner_name", "?")
    tag = record.get("tag_line", "")
    if tag:
        player_label = f"{player_label}#{tag}"

    pro_team = record.get("team") if is_pro else None

    # Use extended stats if full participant data available
    info = match_info.get("info", {})
    participants = info.get("participants", [])
    full_p = next((p for p in participants if p.get("puuid") == puuid), None)

    if full_p:
        msg = format_match_summary_with_stats(player_label, parsed, full_p, pro_team=pro_team)
    else:
        msg = format_match_summary(player_label, parsed, pro_team=pro_team)

    for chat_id in notify_ids:
        await _send_safe(bot, chat_id, msg)

    return latest_id


# ── User poller ───────────────────────────────────────────────────────────────


async def poll_users(session: aiohttp.ClientSession, bot: Any, db_path: str) -> None:
    while True:
        users = await get_all_users(db_path)
        for user in users:
            if _last_poll_age(user.get("last_poll_time")) < _MIN_POLL_GAP:
                continue
            try:
                new_match_id = await _process_player(
                    session,
                    bot,
                    user,
                    notify_ids=[user["user_id"]],
                    is_pro=False,
                )
                if new_match_id:
                    await update_last_match_id(db_path, user["user_id"], new_match_id)
            except Exception:
                logger.exception("Error polling user %s", user.get("user_id"))
            finally:
                await update_user_last_poll_time(db_path, user["user_id"], _now_str())

        logger.info("User poll cycle done: %d users", len(users))
        await asyncio.sleep(POLL_INTERVAL)


# ── Pro poller ────────────────────────────────────────────────────────────────


async def poll_pros(session: aiohttp.ClientSession, bot: Any, db_path: str) -> None:
    while True:
        pros = await get_all_pros(db_path)
        user_ids = await get_all_user_ids(db_path)

        for pro in pros:
            if _last_poll_age(pro.get("last_poll_time")) < _MIN_POLL_GAP:
                continue
            try:
                new_match_id = await _process_player(
                    session,
                    bot,
                    pro,
                    notify_ids=user_ids,
                    is_pro=True,
                )
                if new_match_id:
                    await update_pro_last_match_id(db_path, pro["id"], new_match_id)
            except Exception:
                logger.exception("Error polling pro %s", pro.get("id"))
            finally:
                await update_pro_last_poll_time(db_path, pro["id"], _now_str())

        logger.info("Pro poll cycle done: %d pros", len(pros))
        await asyncio.sleep(POLL_INTERVAL)
