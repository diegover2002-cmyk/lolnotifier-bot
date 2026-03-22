"""
Functional test: aggregated stats calculation.
Fetches real match data from match/v5 and validates the stats engine output.
Dev key compatible — only uses account/v1 and match/v5.
"""
from __future__ import annotations

from typing import Any

import aiohttp

from riot_api import get_match_history_ids, get_match_info
from stats import aggregate_stats, extract_match_stats
from .telegram_reporting import build_result

ResultDict = dict[str, Any]

_MATCHES_TO_FETCH = 5  # Keep low to respect dev key rate limits


async def test_aggregated_stats(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
) -> ResultDict:
    """
    Fetch up to _MATCHES_TO_FETCH recent matches, extract per-match stats,
    aggregate them, and validate the output structure and value ranges.
    """
    if not puuid:
        return build_result(
            "aggregated_stats",
            "WARN",
            "Skipped: no PUUID available.",
            {},
        )

    match_ids = await get_match_history_ids(session, region, puuid, count=_MATCHES_TO_FETCH)
    if not match_ids:
        return build_result(
            "aggregated_stats",
            "WARN",
            "No recent matches available to aggregate.",
            {"region": region, "puuid": puuid},
        )

    per_match: list[dict[str, Any]] = []
    failed_fetches = 0

    for match_id in match_ids:
        match_info = await get_match_info(session, region, match_id)
        if not match_info:
            failed_fetches += 1
            continue
        stats = extract_match_stats(match_info, puuid)
        if stats:
            per_match.append(stats)

    if not per_match:
        return build_result(
            "aggregated_stats",
            "FAIL",
            f"Could not extract stats from any of {len(match_ids)} fetched matches.",
            {"region": region, "puuid": puuid, "failed_fetches": failed_fetches},
        )

    agg = aggregate_stats(per_match)

    # Validate structure
    required_keys = {
        "games", "wins", "losses", "winrate",
        "avg_kda_ratio", "avg_kills", "avg_deaths", "avg_assists",
        "avg_cs", "avg_cs_per_min", "avg_gold", "avg_damage", "avg_vision",
        "most_played_champion", "performance_score",
    }
    missing = required_keys - set(agg.keys())
    if missing:
        return build_result(
            "aggregated_stats",
            "FAIL",
            f"Aggregated stats missing keys: {missing}",
            {"agg": agg},
        )

    # Validate value sanity
    if not (0 <= agg["winrate"] <= 100):
        return build_result(
            "aggregated_stats",
            "FAIL",
            f"Winrate out of range: {agg['winrate']}",
            {"agg": agg},
        )
    if agg["games"] != len(per_match):
        return build_result(
            "aggregated_stats",
            "FAIL",
            f"Game count mismatch: expected {len(per_match)}, got {agg['games']}",
            {"agg": agg},
        )
    if agg["wins"] + agg["losses"] != agg["games"]:
        return build_result(
            "aggregated_stats",
            "FAIL",
            "wins + losses != games",
            {"agg": agg},
        )

    champ = agg.get("most_played_champion") or "?"
    return build_result(
        "aggregated_stats",
        "PASS",
        (
            f"Aggregated {agg['games']} matches: "
            f"{agg['wins']}W/{agg['losses']}L ({agg['winrate']}% WR), "
            f"avg KDA {agg['avg_kda_ratio']}, "
            f"most played {champ}, "
            f"perf score {agg['performance_score']}."
        ),
        {
            "region": region,
            "puuid": puuid,
            "games_fetched": len(match_ids),
            "games_parsed": len(per_match),
            "failed_fetches": failed_fetches,
            "aggregated": agg,
            "per_match_champions": [s.get("champion") for s in per_match],
        },
    )
