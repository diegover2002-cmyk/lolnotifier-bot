"""
Telegram command handlers.
All player registration now uses Riot ID format: GameName#TAG region.
"""

from __future__ import annotations

import logging

import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

from config import ACCOUNT_CLUSTERS, DB_PATH
from database import (
    add_pro,
    get_all_pros,
    get_user,
    remove_pro,
    set_user_summoner,
    toggle_notifications,
)
from formatter import format_aggregated_stats, format_help, format_pro_list, format_status
from pro_players import PRO_PLAYERS
from riot_account import get_account_by_riot_id
from riot_api import get_match_history_ids, get_match_info
from stats import aggregate_stats, extract_match_stats

logger = logging.getLogger(__name__)


def _parse_riot_id(args: list[str]) -> tuple[str, str] | None:
    """
    Accept either:
      GameName#TAG  (single arg)
      GameName TAG  (two args, no hash)
    Returns (game_name, tag_line) or None.
    """
    if not args:
        return None
    joined = " ".join(args)
    if "#" in joined:
        parts = joined.split("#", 1)
        return parts[0].strip(), parts[1].strip()
    return None


async def _resolve_account(game_name: str, tag_line: str, region: str) -> dict | None:
    cluster = ACCOUNT_CLUSTERS.get(region)
    if not cluster:
        return None
    async with aiohttp.ClientSession() as session:
        return await get_account_by_riot_id(session, cluster, game_name, tag_line)


# ── Commands ──────────────────────────────────────────────────────────────────


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(format_help())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(format_help())


async def set_summoner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /set_summoner GameName#TAG region
    Example: /set_summoner LaBísica#EUW euw1
    """
    args = list(context.args or [])
    if len(args) < 2:
        await update.message.reply_text("Uso: /set_summoner GameName#TAG region\nEj: /set_summoner LaBísica#EUW euw1")
        return

    region = args[-1].lower()
    riot_id_args = args[:-1]
    parsed = _parse_riot_id(riot_id_args)

    if not parsed:
        await update.message.reply_text("Formato incorrecto. Usa: /set_summoner GameName#TAG region")
        return

    game_name, tag_line = parsed

    await update.message.reply_text(f"🔍 Buscando {game_name}#{tag_line} en {region}...")

    account = await _resolve_account(game_name, tag_line, region)
    if not account:
        await update.message.reply_text(
            f"❌ No encontré la cuenta {game_name}#{tag_line} en {region}.\nVerifica el Riot ID y la región."
        )
        return

    puuid = account.get("puuid")
    summoner_name = f"{game_name}#{tag_line}"

    await set_user_summoner(
        DB_PATH,
        update.effective_user.id,
        summoner_name,
        region,
        game_name=game_name,
        tag_line=tag_line,
        puuid=puuid,
    )
    await update.message.reply_text(
        f"✅ Cuenta ligada: {game_name}#{tag_line} ({region})\n"
        f"PUUID: {puuid[:20]}...\n"
        "Recibirás notificaciones de tus partidas."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(DB_PATH, update.effective_user.id)
    if not user:
        await update.message.reply_text("No tienes cuenta ligada.\nUsa /set_summoner GameName#TAG region")
        return
    await update.message.reply_text(format_status(user))


async def toggle_notifs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(DB_PATH, update.effective_user.id)
    if not user:
        await update.message.reply_text("Liga tu cuenta primero con /set_summoner")
        return
    new_state = not bool(user["notifications_enabled"])
    await toggle_notifications(DB_PATH, update.effective_user.id, new_state)
    state_txt = "✅ activadas" if new_state else "⏸️  pausadas"
    await update.message.reply_text(f"Notificaciones {state_txt}.")


async def add_pro_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /add_pro GameName#TAG region
    Example: /add_pro Caps#EUW euw1
    """
    args = list(context.args or [])
    if len(args) < 2:
        await update.message.reply_text("Uso: /add_pro GameName#TAG region\nEj: /add_pro Caps#EUW euw1")
        return

    region = args[-1].lower()
    parsed = _parse_riot_id(args[:-1])
    if not parsed:
        await update.message.reply_text("Formato: /add_pro GameName#TAG region")
        return

    game_name, tag_line = parsed
    await update.message.reply_text(f"🔍 Verificando {game_name}#{tag_line}...")

    account = await _resolve_account(game_name, tag_line, region)
    if not account:
        await update.message.reply_text(f"❌ No encontré {game_name}#{tag_line} en {region}.")
        return

    puuid = account.get("puuid")
    summoner_name = f"{game_name}#{tag_line}"
    pro_id = await add_pro(
        DB_PATH,
        summoner_name,
        region,
        game_name=game_name,
        tag_line=tag_line,
        puuid=puuid,
    )
    await update.message.reply_text(f"✅ Pro añadido [ID {pro_id}]: {game_name}#{tag_line} ({region})")


async def list_pros(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pros = await get_all_pros(DB_PATH)
    await update.message.reply_text(format_pro_list(pros))


async def remove_pro_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args or []
    if not args:
        await update.message.reply_text("Uso: /remove_pro <id>  (ver IDs con /list_pros)")
        return
    try:
        pro_id = int(args[0])
    except ValueError:
        await update.message.reply_text("ID inválido. Usa /list_pros para ver los IDs.")
        return
    await remove_pro(DB_PATH, pro_id)
    await update.message.reply_text(f"✅ Pro {pro_id} eliminado.")


async def player_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /stats — show aggregated stats for your last 5 matches.
    Uses only match/v5 (dev key compatible).
    """
    user = await get_user(DB_PATH, update.effective_user.id)
    if not user:
        await update.message.reply_text("No tienes cuenta ligada.\nUsa /set_summoner GameName#TAG region")
        return

    puuid = user.get("puuid")
    region = user.get("region", "la2")
    player_label = user.get("game_name") or user.get("summoner_name", "?")
    tag = user.get("tag_line", "")
    if tag:
        player_label = f"{player_label}#{tag}"

    if not puuid:
        await update.message.reply_text("⚠️ PUUID no disponible. Vuelve a registrar tu cuenta con /set_summoner.")
        return

    await update.message.reply_text("⏳ Calculando estadísticas de tus últimas 5 partidas...")

    async with aiohttp.ClientSession() as session:
        match_ids = await get_match_history_ids(session, region, puuid, count=5)
        per_match = []
        for mid in match_ids:
            info = await get_match_info(session, region, mid)
            if info:
                s = extract_match_stats(info, puuid)
                if s:
                    per_match.append(s)

    if not per_match:
        await update.message.reply_text("No se encontraron partidas recientes para calcular estadísticas.")
        return

    agg = aggregate_stats(per_match)
    msg = format_aggregated_stats(player_label, agg)
    await update.message.reply_text(msg)


async def load_pros(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /load_pros — bulk-insert the curated PRO_PLAYERS dataset.
    Skips entries that already exist.
    """
    await update.message.reply_text(f"⏳ Cargando {len(PRO_PLAYERS)} pros del dataset oficial...")
    added = 0
    skipped = 0
    for entry in PRO_PLAYERS:
        summoner_name = f"{entry['game_name']}#{entry['tag_line']}"
        pro_id = await add_pro(
            DB_PATH,
            summoner_name,
            entry["region"],
            game_name=entry["game_name"],
            tag_line=entry["tag_line"],
            team=entry.get("team", ""),
            role=entry.get("role", ""),
        )
        if pro_id > 0:
            added += 1
        else:
            skipped += 1

    await update.message.reply_text(
        f"✅ Dataset cargado.\nAñadidos: {added}  |  Ya existían: {skipped}\nUsa /list_pros para ver la lista."
    )
