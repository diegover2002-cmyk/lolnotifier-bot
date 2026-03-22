"""
Telegram message formatter.
Produces clean, emoji-rich messages from Riot API data.
All functions are pure (no I/O).
"""

from __future__ import annotations

from typing import Any

# Queue ID → human label (Riot static data, stable)
QUEUE_LABELS: dict[int, str] = {
    420: "Ranked Solo/Duo",
    440: "Ranked Flex",
    400: "Normal Draft",
    430: "Normal Blind",
    450: "ARAM",
    700: "Clash",
    900: "URF",
    1020: "One for All",
    1300: "Nexus Blitz",
    1400: "Ultimate Spellbook",
    0: "Custom",
}

ROLE_EMOJI: dict[str, str] = {
    "TOP": "🛡️",
    "JGL": "🌲",
    "MID": "⚡",
    "BOT": "🏹",
    "SUP": "💊",
}


def _queue_label(queue_id: int | None) -> str:
    if queue_id is None:
        return "Unknown Queue"
    return QUEUE_LABELS.get(queue_id, f"Queue {queue_id}")


def _duration(seconds: int | None) -> str:
    if not seconds:
        return "?"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s:02d}s"


def _kda_ratio(kills: int, deaths: int, assists: int) -> str:
    if deaths == 0:
        return "Perfect"
    ratio = (kills + assists) / deaths
    return f"{ratio:.2f}"


def format_match_summary(
    player_name: str,
    parsed: dict[str, Any],
    *,
    pro_team: str | None = None,
) -> str:
    """Rich match result message for a single player."""
    result_emoji = "✅" if parsed.get("win") else "❌"
    result_text = "VICTORIA" if parsed.get("win") else "DERROTA"
    champion = parsed.get("champion", "?")
    kills = parsed.get("kills", 0)
    deaths = parsed.get("deaths", 0)
    assists = parsed.get("assists", 0)
    kda = parsed.get("kda", f"{kills}/{deaths}/{assists}")
    kda_r = _kda_ratio(kills, deaths, assists)
    queue = _queue_label(parsed.get("queue_id"))
    duration = _duration(parsed.get("duration_seconds"))
    match_id = parsed.get("match_id", "")

    header = f"🌟 PRO · {pro_team}" if pro_team else "🎮 Partida"

    lines = [
        f"{header}",
        f"{result_emoji} {result_text} — {champion}",
        "",
        f"👤 {player_name}",
        f"⚔️  KDA: {kda}  (ratio {kda_r})",
        f"🎯 Modo: {queue}",
        f"⏱️  Duración: {duration}",
    ]
    if match_id:
        lines.append(f"🔗 ID: {match_id}")

    return "\n".join(lines)


def format_match_summary_with_stats(
    player_name: str,
    parsed: dict[str, Any],
    full_participant: dict[str, Any],
    *,
    pro_team: str | None = None,
) -> str:
    """Extended match result with CS, gold, damage when available."""
    base = format_match_summary(player_name, parsed, pro_team=pro_team)
    cs = full_participant.get("totalMinionsKilled", 0) + full_participant.get("neutralMinionsKilled", 0)
    gold = full_participant.get("goldEarned", 0)
    dmg = full_participant.get("totalDamageDealtToChampions", 0)
    vision = full_participant.get("visionScore", 0)

    extras = [
        "",
        f"🌾 CS: {cs}   💰 Oro: {gold:,}",
        f"💥 Daño: {dmg:,}   👁️  Visión: {vision}",
    ]
    return base + "\n" + "\n".join(extras)


def format_new_match_detected(
    player_name: str,
    match_id: str,
    *,
    pro_team: str | None = None,
) -> str:
    """Notification that a new completed match was detected."""
    header = f"🌟 PRO · {pro_team}" if pro_team else "🎮 Nueva partida"
    return f"{header}\n👤 {player_name}\n📋 Partida detectada: {match_id}\n⏳ Procesando resultados..."


def format_pro_list(pros: list[dict[str, Any]]) -> str:
    if not pros:
        return "No hay pros trackeados. Usa /add_pro GameName#TAG region"
    lines = ["🌟 Pros trackeados:\n"]
    for p in pros:
        gn = p.get("game_name") or p.get("summoner_name", "?")
        tl = p.get("tag_line", "")
        region = p.get("region", "?")
        team = p.get("team", "")
        role = p.get("role", "")
        role_e = ROLE_EMOJI.get(role.upper(), "")
        tag = f"#{tl}" if tl else ""
        team_str = f" · {team}" if team else ""
        role_str = f" {role_e}" if role_e else ""
        lines.append(f"  [{p['id']}] {gn}{tag} ({region}){team_str}{role_str}")
    return "\n".join(lines)


def format_status(user: dict[str, Any]) -> str:
    name = user.get("game_name") or user.get("summoner_name", "?")
    tag = user.get("tag_line", "")
    region = user.get("region", "?")
    notifs = "✅ activas" if user.get("notifications_enabled") else "⏸️  pausadas"
    last_poll = user.get("last_poll_time") or "Nunca"
    last_match = user.get("last_match_id") or "Ninguna"
    tag_str = f"#{tag}" if tag else ""
    return (
        f"👤 Cuenta: {name}{tag_str} ({region})\n"
        f"🔔 Notificaciones: {notifs}\n"
        f"🕐 Última poll: {last_poll}\n"
        f"🎮 Última partida: {last_match}"
    )


def format_aggregated_stats(
    player_name: str,
    agg: dict[str, Any],
    *,
    pro_team: str | None = None,
    role: str | None = None,
) -> str:
    """Rich stats summary from aggregate_stats() output."""
    header = f"🌟 PRO · {pro_team}" if pro_team else "📊 Estadísticas"
    role_e = ROLE_EMOJI.get((role or "").upper(), "")
    champ = agg.get("most_played_champion") or "?"
    wr = agg.get("winrate", 0)
    wr_emoji = "🔥" if wr >= 60 else ("✅" if wr >= 50 else "❌")
    perf = agg.get("performance_score", 0)

    lines = [
        f"{header} {role_e}",
        f"👤 {player_name}",
        "",
        f"🎮 Partidas: {agg.get('games', 0)}  ({agg.get('wins', 0)}V / {agg.get('losses', 0)}D)",
        f"{wr_emoji} Winrate: {wr}%",
        f"⚔️  KDA medio: {agg.get('avg_kills', 0)}/{agg.get('avg_deaths', 0)}/{agg.get('avg_assists', 0)}"
        f"  (ratio {agg.get('avg_kda_ratio', 0)})",
        f"🏆 Campeón más jugado: {champ}",
        "",
        f"🌾 CS/min: {agg.get('avg_cs_per_min', 0)}",
        f"💰 Oro medio: {int(agg.get('avg_gold', 0)):,}",
        f"💥 Daño medio: {int(agg.get('avg_damage', 0)):,}",
        f"👁️  Visión media: {agg.get('avg_vision', 0)}",
        "",
        f"⭐ Performance score: {perf}/100",
    ]
    if agg.get("total_penta_kills", 0):
        lines.append(f"🎆 Pentas: {agg['total_penta_kills']}")
    return "\n".join(lines)


def format_player_ranking(
    ranking: list[tuple[int, str, float]],
    title: str = "🏆 Ranking de jugadores",
) -> str:
    """Format a ranked list from stats.rank_players() output."""
    if not ranking:
        return f"{title}\n\nNo hay datos suficientes."
    lines = [title, ""]
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for rank, label, score in ranking:
        medal = medals.get(rank, f"{rank}.")  # type: ignore[arg-type]
        lines.append(f"{medal} {label}  —  score {score}")
    return "\n".join(lines)


def format_help() -> str:
    return (
        "🤖 LoLNotifierBot\n\n"
        "📌 Tu cuenta:\n"
        "  /set_summoner GameName#TAG region\n"
        "    ej: /set_summoner LaBísica#EUW euw1\n"
        "  /status — ver tu configuración\n"
        "  /stats — estadísticas de tus últimas 5 partidas\n"
        "  /toggle — activar/pausar notificaciones\n\n"
        "🌟 Pros:\n"
        "  /add_pro GameName#TAG region\n"
        "    ej: /add_pro Caps#EUW euw1\n"
        "  /list_pros — ver pros trackeados\n"
        "  /remove_pro <id>\n"
        "  /load_pros — cargar dataset oficial\n\n"
        "🗺️  Regiones: na1 · euw1 · kr · la1 · la2\n"
        "              eun1 · br1 · jp1 · tr1"
    )
