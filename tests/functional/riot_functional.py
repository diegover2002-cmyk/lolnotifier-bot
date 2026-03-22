import asyncio
from typing import Any, Dict, List, Optional

import aiohttp

from config import ACCOUNT_CLUSTERS, REGIONS, RIOT_API_KEY
from riot_account import get_account_by_riot_id, get_puuid_by_game_name
from riot_api import get_match_info, get_match_history_ids, parse_match_for_puuid, get_summoner_by_puuid

ResultDict = Dict[str, Any]


def build_result(name: str, status: str, details: str, data: Optional[Dict[str, Any]] = None) -> ResultDict:
    return {
        "name": name,
        "status": status,
        "details": details,
        "data": data or {},
    }


def compare_tracking_state(
    previous_match_id: Optional[str],
    current_match_ids: List[str],
) -> Dict[str, Any]:
    latest_match_id = current_match_ids[0] if current_match_ids else None
    has_history = bool(current_match_ids)
    has_new_match = bool(latest_match_id and latest_match_id != previous_match_id)
    return {
        "previous_match_id": previous_match_id,
        "latest_match_id": latest_match_id,
        "history_count": len(current_match_ids),
        "has_history": has_history,
        "has_new_match": has_new_match,
        "should_notify": has_new_match,
    }


async def _get_ranked_entries(
    session: aiohttp.ClientSession,
    region: str,
    summoner_id: str,
) -> Optional[List[Dict[str, Any]]]:
    """Test-only helper — league/v4 returns 403 on dev key."""
    from config import REGIONS
    url = f"https://{REGIONS[region]}/lol/league/v4/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY or ""}
    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
        await asyncio.sleep(0.1)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            return []
        return None


async def test_account_resolution(
    session: aiohttp.ClientSession,
    region: str,
    game_name: str,
    tag_line: str,
) -> ResultDict:
    cluster = ACCOUNT_CLUSTERS[region]
    account = await get_account_by_riot_id(session, cluster, game_name, tag_line)

    if not account:
        return build_result(
            "account_resolution",
            "FAIL",
            f"Could not resolve Riot ID {game_name}#{tag_line} in cluster {cluster}.",
            {"region": region, "cluster": cluster, "riot_id": f"{game_name}#{tag_line}"},
        )

    puuid = account.get("puuid")
    if not puuid:
        return build_result(
            "account_resolution",
            "FAIL",
            "Account lookup returned no PUUID.",
            {"region": region, "cluster": cluster, "account": account},
        )

    return build_result(
        "account_resolution",
        "PASS",
        f"Resolved Riot ID {game_name}#{tag_line} to a PUUID.",
        {
            "region": region,
            "cluster": cluster,
            "gameName": account.get("gameName"),
            "tagLine": account.get("tagLine"),
            "puuid": puuid,
        },
    )


async def test_summoner_lookup_by_puuid(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
) -> ResultDict:
    if not puuid:
        return build_result(
            "summoner_lookup_by_puuid",
            "WARN",
            "Skipped: no PUUID available from account resolution.",
            {"region": region},
        )

    summoner = await get_summoner_by_puuid(session, region, puuid)

    if not summoner:
        return build_result(
            "summoner_lookup_by_puuid",
            "WARN",
            "Summoner lookup returned no data (dev key 403 restriction expected).",
            {"region": region, "puuid": puuid},
        )

    summoner_id = summoner.get("id")
    level = summoner.get("summonerLevel", 0)
    if not summoner_id:
        return build_result(
            "summoner_lookup_by_puuid",
            "FAIL",
            "Summoner payload is missing the encrypted summoner id.",
            {"region": region, "summoner": summoner},
        )

    return build_result(
        "summoner_lookup_by_puuid",
        "PASS",
        f"Summoner profile resolved successfully at level {level}.",
        {
            "region": region,
            "puuid": puuid,
            "summoner_id": summoner_id,
            "summonerLevel": level,
            "profileIconId": summoner.get("profileIconId"),
        },
    )


async def test_match_history_retrieval(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
    *,
    count: int = 5,
) -> ResultDict:
    match_ids = await get_match_history_ids(session, region, puuid, count=count)

    if not match_ids:
        return build_result(
            "match_history_retrieval",
            "WARN",
            "No recent matches were returned for this player.",
            {"region": region, "puuid": puuid, "match_ids": []},
        )

    return build_result(
        "match_history_retrieval",
        "PASS",
        f"Retrieved {len(match_ids)} recent match id(s).",
        {
            "region": region,
            "puuid": puuid,
            "count": len(match_ids),
            "latest_match_id": match_ids[0],
            "match_ids": match_ids,
        },
    )


async def test_match_detail_parsing(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
    match_id: str,
) -> ResultDict:
    if not match_id:
        return build_result(
            "match_detail_parsing",
            "WARN",
            "Skipped: no match_id available from match history.",
            {"region": region, "puuid": puuid},
        )

    try:
        match_info = await get_match_info(session, region, match_id)
    except aiohttp.ClientResponseError as exc:
        return build_result(
            "match_detail_parsing",
            "FAIL",
            f"Match detail request failed with status {exc.status}.",
            {"region": region, "match_id": match_id, "error": str(exc)},
        )
    except Exception as exc:
        return build_result(
            "match_detail_parsing",
            "FAIL",
            f"Unexpected error while requesting match details: {exc}",
            {"region": region, "match_id": match_id, "error": str(exc)},
        )

    if not match_info:
        return build_result(
            "match_detail_parsing",
            "FAIL",
            "Match detail endpoint returned no payload.",
            {"region": region, "match_id": match_id},
        )

    parsed = parse_match_for_puuid(match_info, puuid)
    if not parsed:
        return build_result(
            "match_detail_parsing",
            "FAIL",
            "Could not find the target player in the match participant list.",
            {"region": region, "match_id": match_id},
        )

    champion = parsed.get("champion") or "Unknown"
    outcome = "WIN" if parsed.get("win") else "LOSS"
    return build_result(
        "match_detail_parsing",
        "PASS",
        f"Parsed match data successfully: {champion} {parsed['kda']} {outcome}.",
        parsed,
    )


async def test_ranked_data_retrieval(
    session: aiohttp.ClientSession,
    region: str,
    summoner_id: str,
) -> ResultDict:
    if not summoner_id:
        return build_result(
            "ranked_data_retrieval",
            "WARN",
            "Skipped: no summoner_id available (dev key 403 restriction on summoner/v4).",
            {"region": region},
        )

    ranked_entries = await _get_ranked_entries(session, region, summoner_id)

    if ranked_entries is None:
        return build_result(
            "ranked_data_retrieval",
            "FAIL",
            "Ranked endpoint could not be read successfully.",
            {"region": region, "summoner_id": summoner_id},
        )

    if not ranked_entries:
        return build_result(
            "ranked_data_retrieval",
            "WARN",
            "Player has no visible ranked entries.",
            {"region": region, "summoner_id": summoner_id, "queues": []},
        )

    queues = [
        {
            "queueType": entry.get("queueType"),
            "tier": entry.get("tier"),
            "rank": entry.get("rank"),
            "leaguePoints": entry.get("leaguePoints"),
            "wins": entry.get("wins"),
            "losses": entry.get("losses"),
        }
        for entry in ranked_entries
    ]

    return build_result(
        "ranked_data_retrieval",
        "PASS",
        f"Retrieved {len(queues)} ranked queue entry(ies).",
        {"region": region, "summoner_id": summoner_id, "queues": queues},
    )


async def test_tracking_logic_comparison(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
    *,
    previous_match_id: Optional[str] = None,
) -> ResultDict:
    current_match_ids = await get_match_history_ids(session, region, puuid, count=3)
    tracking_state = compare_tracking_state(previous_match_id, current_match_ids)

    if not tracking_state["has_history"]:
        return build_result(
            "tracking_logic_comparison",
            "WARN",
            "Tracking logic could not compare because the player has no recent match history.",
            tracking_state,
        )

    if previous_match_id is None:
        return build_result(
            "tracking_logic_comparison",
            "PASS",
            "Tracking baseline created from the latest available match.",
            tracking_state,
        )

    detail = "Detected a new match since the previous tracking state." if tracking_state["has_new_match"] else "No new match detected since the previous tracking state."
    return build_result(
        "tracking_logic_comparison",
        "PASS",
        detail,
        tracking_state,
    )


async def test_invalid_riot_id(
    session: aiohttp.ClientSession,
    region: str,
    game_name: str = "DefinitelyInvalidFunctionalTestUser",
    tag_line: str = "NOPE999",
) -> ResultDict:
    cluster = ACCOUNT_CLUSTERS[region]
    account = await get_account_by_riot_id(session, cluster, game_name, tag_line)

    if account is None:
        return build_result(
            "edge_invalid_riot_id",
            "PASS",
            "Invalid Riot ID was rejected as expected.",
            {"region": region, "cluster": cluster, "riot_id": f"{game_name}#{tag_line}"},
        )

    return build_result(
        "edge_invalid_riot_id",
        "FAIL",
        "Invalid Riot ID unexpectedly returned an account.",
        {"region": region, "cluster": cluster, "account": account},
    )


async def test_empty_history_handling(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
) -> ResultDict:
    if not puuid:
        return build_result(
            "edge_empty_history_handling",
            "WARN",
            "Skipped: no PUUID available.",
            {"region": region},
        )

    match_ids = await get_match_history_ids(session, region, puuid, count=1)
    tracking_state = compare_tracking_state(match_ids[0] if match_ids else None, [])

    if tracking_state["has_history"]:
        return build_result(
            "edge_empty_history_handling",
            "FAIL",
            "Empty history simulation still reported history.",
            tracking_state,
        )

    return build_result(
        "edge_empty_history_handling",
        "PASS",
        "Empty history simulation is handled without crashing the tracking logic.",
        tracking_state,
    )


async def test_api_error_handling(
    session: aiohttp.ClientSession,
    region: str,
) -> ResultDict:
    invalid_puuid = "invalid-puuid-for-functional-test"
    try:
        summoner = await get_summoner_by_puuid(session, region, invalid_puuid)
    except aiohttp.ClientResponseError as exc:
        if exc.status in (400, 403, 404):
            return build_result(
                "edge_api_error_handling",
                "PASS",
                f"API wrapper raised a handled HTTP error status {exc.status} for invalid input.",
                {"region": region, "status": exc.status, "error": str(exc)},
            )
        return build_result(
            "edge_api_error_handling",
            "FAIL",
            f"API wrapper raised an unexpected HTTP status {exc.status}.",
            {"region": region, "status": exc.status, "error": str(exc)},
        )
    except Exception as exc:
        return build_result(
            "edge_api_error_handling",
            "FAIL",
            f"API wrapper raised an unexpected exception type: {exc}",
            {"region": region, "error": str(exc)},
        )

    if summoner is None:
        return build_result(
            "edge_api_error_handling",
            "PASS",
            "API wrapper returned None cleanly for invalid input.",
            {"region": region, "puuid": invalid_puuid},
        )

    return build_result(
        "edge_api_error_handling",
        "WARN",
        "API wrapper returned data for an invalid input value unexpectedly.",
        {"region": region, "puuid": invalid_puuid, "summoner": summoner},
    )


async def resolve_test_subject(
    session: aiohttp.ClientSession,
    region: str,
    game_name: str,
    tag_line: str,
) -> Dict[str, Any]:
    cluster = ACCOUNT_CLUSTERS[region]
    puuid = await get_puuid_by_game_name(session, cluster, game_name, tag_line)
    summoner = await get_summoner_by_puuid(session, region, puuid) if puuid else None
    return {
        "region": region,
        "cluster": cluster,
        "game_name": game_name,
        "tag_line": tag_line,
        "puuid": puuid,
        "summoner": summoner,
        "summoner_id": summoner.get("id") if summoner else None,
    }