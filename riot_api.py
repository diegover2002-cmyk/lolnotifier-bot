"""
Riot API client — Dev Key compatible endpoints only.

Available endpoints:
  account/v1  — Riot ID → PUUID resolution          ✅
  match/v5    — match history IDs and match details  ✅

Blocked on Dev Key (403):
  summoner/v4, league/v4, spectator/v5, champion-mastery/v4  ⚠️
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import aiohttp
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import (
    ACCOUNT_CLUSTERS,
    CACHE_TTL_SUMMONER,
    RATE_LIMIT_DELAY,
    REGIONS,
    RIOT_API_BASE,
    RIOT_API_KEY,
)
from riot_account import get_puuid_by_game_name

logger = logging.getLogger(__name__)

# Global semaphore — respects Riot Dev Key limit of 20 req/s
_rate_semaphore = asyncio.Semaphore(20)

# In-memory cache: key → (data, timestamp)
_summoner_cache: dict[str, tuple[Any, datetime]] = {}


# ── Internal helpers ──────────────────────────────────────────────────────────


async def _rate_delay() -> None:
    """Enforce per-request delay to stay within rate limits."""
    await asyncio.sleep(RATE_LIMIT_DELAY)


def _cache_valid(timestamp: datetime, ttl: int) -> bool:
    """Return True if the cached entry is still within its TTL."""
    return datetime.now() < timestamp + timedelta(seconds=ttl)


def _riot_headers() -> dict[str, str]:
    return {"X-Riot-Token": RIOT_API_KEY or ""}


# ── Summoner (Dev Key: 403 on most regions, kept for prod-key readiness) ──────


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type(aiohttp.ClientResponseError),
    reraise=True,
)
async def get_summoner_by_puuid(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
) -> Optional[dict[str, Any]]:
    """
    Fetch summoner profile by PUUID via summoner/v4.
    Returns None on 401/403/404 (dev key restriction or not found).
    Will activate fully on production key upgrade.
    """
    cache_key = f"{region}_{puuid}"
    async with _rate_semaphore:
        if cache_key in _summoner_cache:
            data, ts = _summoner_cache[cache_key]
            if _cache_valid(ts, CACHE_TTL_SUMMONER):
                logger.debug("Cache hit: summoner %s", cache_key)
                return data

        url = RIOT_API_BASE.format(region=REGIONS[region]) + f"/summoner/v4/summoners/by-puuid/{puuid}"
        async with session.get(url, headers=_riot_headers()) as resp:
            if resp.status == 429:
                logger.warning("Rate limit hit (429) on summoner lookup — backing off 60s")
                await asyncio.sleep(60)
            if resp.status == 200:
                data = await resp.json()
                _summoner_cache[cache_key] = (data, datetime.now())
                await _rate_delay()
                return data
            if resp.status in (401, 403, 404):
                await _rate_delay()
                return None
            resp.raise_for_status()
    return None


async def get_summoner(
    session: aiohttp.ClientSession,
    region: str,
    game_name: str,
    tag_line: str,
) -> Optional[dict[str, Any]]:
    """
    Convenience wrapper: Riot ID (GameName#TAG) → PUUID → Summoner profile.
    Returns None if PUUID cannot be resolved or summoner lookup fails.
    """
    cluster = ACCOUNT_CLUSTERS[region]
    puuid = await get_puuid_by_game_name(session, cluster, game_name, tag_line)
    if not puuid:
        logger.warning("No PUUID found for %s#%s", game_name, tag_line)
        return None
    return await get_summoner_by_puuid(session, region, puuid)


# ── Match history (Dev Key compatible) ───────────────────────────────────────


async def get_match_history_ids(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
    *,
    start: int = 0,
    count: int = 5,
) -> list[str]:
    """
    Fetch a list of recent match IDs for a player via match/v5.

    Args:
        session: Active aiohttp session.
        region:  Platform region code (e.g. 'euw1', 'kr').
        puuid:   Player PUUID.
        start:   Index of the first match to return (default 0).
        count:   Number of match IDs to return (default 5, max 100).

    Returns:
        List of match ID strings, empty list on error or no matches.
    """
    cluster = ACCOUNT_CLUSTERS.get(region, "europe")
    url = f"https://{cluster}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
    async with _rate_semaphore:
        async with session.get(url, headers=_riot_headers(), timeout=aiohttp.ClientTimeout(total=20)) as resp:
            await _rate_delay()
            if resp.status == 200:
                data = await resp.json()
                return data if isinstance(data, list) else []
            if resp.status in (401, 403, 404):
                logger.debug("match history returned %d for puuid %s", resp.status, puuid[:8])
                return []
            resp.raise_for_status()
    return []


# ── Match detail (Dev Key compatible) ────────────────────────────────────────


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
async def get_match_info(
    session: aiohttp.ClientSession,
    region: str,
    match_id: str,
) -> Optional[dict[str, Any]]:
    """
    Fetch full match details for a given match ID via match/v5.

    Args:
        session:  Active aiohttp session.
        region:   Platform region code (e.g. 'euw1', 'kr').
        match_id: Match ID string (e.g. 'EUW1_7123456789').

    Returns:
        Full match/v5 payload dict, or None on 401/403/404.
    """
    cluster = ACCOUNT_CLUSTERS.get(region, "europe")
    url = f"https://{cluster}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    async with _rate_semaphore:
        async with session.get(url, headers=_riot_headers()) as resp:
            await _rate_delay()
            if resp.status == 200:
                return await resp.json()
            if resp.status in (401, 403, 404):
                logger.debug("match info returned %d for %s", resp.status, match_id)
                return None
            resp.raise_for_status()
    return None


# ── Match parsing ─────────────────────────────────────────────────────────────


def parse_match_for_puuid(
    match_info: dict[str, Any],
    puuid: str,
) -> Optional[dict[str, Any]]:
    """
    Extract a player's core stats from a match/v5 payload.

    Args:
        match_info: Full match/v5 response dict.
        puuid:      Target player's PUUID.

    Returns:
        Dict with champion, KDA, win/loss, queue, duration — or None if
        the player is not found in the participant list.
    """
    info = match_info.get("info", {})
    metadata = match_info.get("metadata", {})
    participants = info.get("participants", [])
    player = next((p for p in participants if p.get("puuid") == puuid), None)
    if not player:
        return None

    kills = int(player.get("kills", 0))
    deaths = int(player.get("deaths", 0))
    assists = int(player.get("assists", 0))

    return {
        "match_id": metadata.get("matchId"),
        "queue_id": info.get("queueId"),
        "game_mode": info.get("gameMode"),
        "champion": player.get("championName"),
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kda": f"{kills}/{deaths}/{assists}",
        "win": bool(player.get("win")),
        "duration_seconds": info.get("gameDuration"),
    }
