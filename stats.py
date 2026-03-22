"""
Stats engine — pure aggregation over match/v5 participant data.
No API calls. All functions take already-fetched data.

Available from match/v5 (dev key compatible):
  kills, deaths, assists, win, champion, queue_id, game_duration,
  totalMinionsKilled, neutralMinionsKilled, goldEarned,
  totalDamageDealtToChampions, visionScore, totalHealsOnTeammates,
  turretKills, firstBloodKill, doubleKills, tripleKills, quadraKills, pentaKills
"""

from __future__ import annotations

from typing import Any


# ── Per-match extraction ──────────────────────────────────────────────────────


def extract_participant(match_info: dict[str, Any], puuid: str) -> dict[str, Any] | None:
    """Return the full participant dict for a given PUUID from a match/v5 payload."""
    participants = match_info.get("info", {}).get("participants", [])
    return next((p for p in participants if p.get("puuid") == puuid), None)


def extract_match_stats(match_info: dict[str, Any], puuid: str) -> dict[str, Any] | None:
    """
    Extract a flat stats dict for one player from a match/v5 payload.
    Returns None if the player is not found in the match.
    """
    info = match_info.get("info", {})
    meta = match_info.get("metadata", {})
    p = extract_participant(match_info, puuid)
    if p is None:
        return None

    kills = int(p.get("kills", 0))
    deaths = int(p.get("deaths", 0))
    assists = int(p.get("assists", 0))
    cs = int(p.get("totalMinionsKilled", 0)) + int(p.get("neutralMinionsKilled", 0))
    duration = int(info.get("gameDuration", 0))
    cs_per_min = round(cs / (duration / 60), 1) if duration > 0 else 0.0

    return {
        "match_id": meta.get("matchId"),
        "queue_id": info.get("queueId"),
        "game_mode": info.get("gameMode"),
        "duration_seconds": duration,
        "champion": p.get("championName"),
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kda_str": f"{kills}/{deaths}/{assists}",
        "kda_ratio": round((kills + assists) / deaths, 2) if deaths > 0 else float(kills + assists),
        "win": bool(p.get("win")),
        "cs": cs,
        "cs_per_min": cs_per_min,
        "gold": int(p.get("goldEarned", 0)),
        "damage": int(p.get("totalDamageDealtToChampions", 0)),
        "vision": int(p.get("visionScore", 0)),
        "first_blood": bool(p.get("firstBloodKill", False)),
        "turret_kills": int(p.get("turretKills", 0)),
        "multikills": {
            "double": int(p.get("doubleKills", 0)),
            "triple": int(p.get("tripleKills", 0)),
            "quadra": int(p.get("quadraKills", 0)),
            "penta": int(p.get("pentaKills", 0)),
        },
    }


# ── Aggregation ───────────────────────────────────────────────────────────────


def aggregate_stats(match_stats_list: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute aggregated stats from a list of extract_match_stats() results.
    Returns a summary dict. Empty list returns zeroed summary.
    """
    n = len(match_stats_list)
    if n == 0:
        return {
            "games": 0,
            "wins": 0,
            "losses": 0,
            "winrate": 0.0,
            "avg_kda_ratio": 0.0,
            "avg_kills": 0.0,
            "avg_deaths": 0.0,
            "avg_assists": 0.0,
            "avg_cs": 0.0,
            "avg_cs_per_min": 0.0,
            "avg_gold": 0.0,
            "avg_damage": 0.0,
            "avg_vision": 0.0,
            "most_played_champion": None,
            "performance_score": 0.0,
            "total_penta_kills": 0,
            "total_first_bloods": 0,
        }

    wins = sum(1 for s in match_stats_list if s.get("win"))
    losses = n - wins

    avg = lambda key: round(sum(s.get(key, 0) for s in match_stats_list) / n, 2)  # noqa: E731

    avg_kda = round(sum(s.get("kda_ratio", 0) for s in match_stats_list) / n, 2)
    avg_cs_per_min = round(sum(s.get("cs_per_min", 0) for s in match_stats_list) / n, 2)

    # Most played champion
    champ_counts: dict[str, int] = {}
    for s in match_stats_list:
        c = s.get("champion") or "Unknown"
        champ_counts[c] = champ_counts.get(c, 0) + 1
    most_played = max(champ_counts, key=lambda k: champ_counts[k]) if champ_counts else None

    # Performance score: weighted composite (higher = better)
    # Formula: winrate*40 + avg_kda*20 + avg_cs_per_min*5 + avg_vision*2 (max ~100)
    winrate = round(wins / n * 100, 1)
    perf = round(
        (winrate * 0.40) + (min(avg_kda, 10) * 2.0) + (min(avg_cs_per_min, 10) * 0.5) + (min(avg("vision"), 50) * 0.2),
        1,
    )

    total_pentas = sum(s.get("multikills", {}).get("penta", 0) for s in match_stats_list)
    total_fb = sum(1 for s in match_stats_list if s.get("first_blood"))

    return {
        "games": n,
        "wins": wins,
        "losses": losses,
        "winrate": winrate,
        "avg_kda_ratio": avg_kda,
        "avg_kills": avg("kills"),
        "avg_deaths": avg("deaths"),
        "avg_assists": avg("assists"),
        "avg_cs": avg("cs"),
        "avg_cs_per_min": avg_cs_per_min,
        "avg_gold": avg("gold"),
        "avg_damage": avg("damage"),
        "avg_vision": avg("vision"),
        "most_played_champion": most_played,
        "performance_score": perf,
        "total_penta_kills": total_pentas,
        "total_first_bloods": total_fb,
    }


# ── Dataset ranking ───────────────────────────────────────────────────────────


def rank_players(
    player_stats: list[tuple[str, dict[str, Any]]],
) -> list[tuple[int, str, float]]:
    """
    Rank a list of (player_label, aggregated_stats) by performance_score descending.
    Returns list of (rank, player_label, score).
    """
    sorted_players = sorted(
        player_stats,
        key=lambda x: x[1].get("performance_score", 0),
        reverse=True,
    )
    return [(i + 1, label, stats.get("performance_score", 0)) for i, (label, stats) in enumerate(sorted_players)]
