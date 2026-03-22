from __future__ import annotations

from typing import Any

from .telegram_reporting import build_result


def _extract_player_data(match_data: dict[str, Any], puuid: str | None = None) -> dict[str, Any] | None:
    info = match_data.get("info", {})
    participants = info.get("participants", [])

    if puuid:
        player = next((participant for participant in participants if participant.get("puuid") == puuid), None)
        if player:
            return player

    return participants[0] if participants else None


def _build_match_summary(player_data: dict[str, Any]) -> str:
    champion = player_data.get("championName", "Unknown Champion")
    kills = player_data.get("kills", 0)
    deaths = player_data.get("deaths", 0)
    assists = player_data.get("assists", 0)
    win = player_data.get("win", False)

    result_text = "Win" if win else "Loss"
    return f"{champion} | KDA {kills}/{deaths}/{assists} | {result_text}"


async def test_match_summary_message_generation(
    match_data: dict[str, Any] | None,
    puuid: str | None = None,
) -> dict[str, Any]:
    if not match_data:
        return build_result(
            name="match_summary_message_generation",
            status="WARN",
            details="No match data provided for message generation test.",
            data={},
        )

    player_data = _extract_player_data(match_data, puuid=puuid)
    if not player_data:
        return build_result(
            name="match_summary_message_generation",
            status="FAIL",
            details="Could not locate participant data in match payload.",
            data={},
        )

    summary = _build_match_summary(player_data)

    champion = str(player_data.get("championName", "")).strip()
    kda_text = f"{player_data.get('kills', 0)}/{player_data.get('deaths', 0)}/{player_data.get('assists', 0)}"
    has_result = "Win" in summary or "Loss" in summary

    if champion and champion in summary and kda_text in summary and has_result:
        return build_result(
            name="match_summary_message_generation",
            status="PASS",
            details="Summary message includes champion, KDA, and win/loss in a readable format.",
            data={
                "summary": summary,
                "champion": champion,
                "kda": kda_text,
                "result": "Win" if player_data.get("win", False) else "Loss",
            },
        )

    return build_result(
        name="match_summary_message_generation",
        status="FAIL",
        details="Summary message is missing champion, KDA, or win/loss information.",
        data={
            "summary": summary,
            "champion_present": bool(champion and champion in summary),
            "kda_present": kda_text in summary,
            "result_present": has_result,
        },
    )