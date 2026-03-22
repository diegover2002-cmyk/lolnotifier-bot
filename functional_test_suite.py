from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Awaitable, Callable

# Force UTF-8 output on Windows so emoji characters don't crash the console
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

import aiohttp
from dotenv import load_dotenv

try:
    from tests.functional.riot_functional import (
        test_account_resolution,
        test_api_error_handling,
        test_empty_history_handling,
        test_invalid_riot_id,
        test_match_detail_parsing,
        test_match_history_retrieval,
        test_ranked_data_retrieval,
        test_summoner_lookup_by_puuid,
        test_tracking_logic_comparison,
    )
except ImportError:
    test_account_resolution = None
    test_api_error_handling = None
    test_empty_history_handling = None
    test_invalid_riot_id = None
    test_match_detail_parsing = None
    test_match_history_retrieval = None
    test_ranked_data_retrieval = None
    test_summoner_lookup_by_puuid = None
    test_tracking_logic_comparison = None

try:
    from tests.functional.message_generation_test import test_match_summary_message_generation
    from tests.functional.telegram_delivery_test import test_telegram_delivery
    from tests.functional.stats_test import test_aggregated_stats
except ImportError:
    test_match_summary_message_generation = None
    test_telegram_delivery = None
    test_aggregated_stats = None

try:
    from tests.functional.telegram_reporting import format_test_report, send_telegram_report
except ImportError:
    format_test_report = None
    send_telegram_report = None

STATUS_EMOJI = {
    "PASS": "✅",
    "FAIL": "❌",
    "WARN": "⚠️",
}


ResultDict = dict[str, Any]
TestFunc = Callable[..., Awaitable[ResultDict]]


def _result(name: str, status: str, details: str, data: dict[str, Any] | None = None) -> ResultDict:
    return {
        "name": name,
        "status": status,
        "details": details,
        "data": data or {},
    }


def _env_user() -> tuple[str | None, str | None]:
    game_name = (
        os.getenv("RIOT_TEST_GAME_NAME")
        or os.getenv("TEST_RIOT_GAME_NAME")
        or os.getenv("RIOT_GAME_NAME")
    )
    tag_line = (
        os.getenv("RIOT_TEST_TAG_LINE")
        or os.getenv("TEST_RIOT_TAG_LINE")
        or os.getenv("RIOT_TAG_LINE")
    )
    return game_name, tag_line


def _print_step(result: ResultDict) -> None:
    emoji = STATUS_EMOJI.get(result["status"], "•")
    print(f"{emoji} {result['name']}: {result['status']} - {result['details']}")


def _missing_test(name: str, module_name: str) -> ResultDict:
    return _result(
        name=name,
        status="WARN",
        details=f"Skipped because required module or function is unavailable: {module_name}",
        data={},
    )


async def _run_test(
    name: str,
    func: TestFunc | None,
    *args: Any,
    **kwargs: Any,
) -> ResultDict:
    if func is None:
        return _missing_test(name, name)

    try:
        result = await func(*args, **kwargs)
    except Exception as exc:
        return _result(name, "FAIL", f"Unhandled exception: {exc}", {"exception": repr(exc)})

    if not isinstance(result, dict):
        return _result(name, "FAIL", "Test did not return a result dictionary", {"raw_result": str(result)})

    normalized = {
        "name": result.get("name", name),
        "status": result.get("status", "FAIL"),
        "details": result.get("details", ""),
        "data": result.get("data", {}) if isinstance(result.get("data", {}), dict) else {},
    }

    if normalized["status"] not in {"PASS", "FAIL", "WARN"}:
        normalized["status"] = "FAIL"
        normalized["details"] = f"Invalid status returned by test: {result.get('status')}"

    return normalized


def _get_nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


async def main() -> int:
    load_dotenv()

    game_name, tag_line = _env_user()

    print("Riot Bot Functional Test Suite")
    print("=" * 30)

    if not game_name or not tag_line:
        details = (
            "Missing Riot test user configuration. Set RIOT_TEST_GAME_NAME and "
            "RIOT_TEST_TAG_LINE (or TEST_RIOT_GAME_NAME / TEST_RIOT_TAG_LINE)."
        )
        result = _result(
            name="Test User Configuration",
            status="FAIL",
            details=details,
            data={},
        )
        _print_step(result)
        if callable(format_test_report):
            print()
            print(format_test_report("unknown#unknown", [result]))
        return 1

    riot_user = f"{game_name}#{tag_line}"
    print(f"Test user: {riot_user}")
    print()

    results: list[ResultDict] = []
    context: dict[str, Any] = {
        "game_name": game_name,
        "tag_line": tag_line,
    }

    region = (
        os.getenv("RIOT_TEST_REGION")
        or os.getenv("TEST_RIOT_REGION")
        or os.getenv("RIOT_REGION")
        or "la2"
    )
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    async with aiohttp.ClientSession() as session:
        ordered_tests: list[tuple[str, TestFunc | None, Callable[[dict[str, Any]], tuple[list[Any], dict[str, Any]]]]] = [
            (
                "Account Resolution",
                test_account_resolution,
                lambda ctx: ([session, region, ctx["game_name"], ctx["tag_line"]], {}),
            ),
            (
                "Summoner Lookup by PUUID",
                test_summoner_lookup_by_puuid,
                lambda ctx: ([session, region, _get_nested(ctx, "account_resolution", "puuid")], {}),
            ),
            (
                "Match History Retrieval",
                test_match_history_retrieval,
                lambda ctx: ([session, region, _get_nested(ctx, "account_resolution", "puuid")], {}),
            ),
            (
                "Match Detail Parsing",
                test_match_detail_parsing,
                lambda ctx: (
                    [
                        session,
                        region,
                        _get_nested(ctx, "account_resolution", "puuid"),
                        _get_nested(ctx, "match_history", "latest_match_id"),
                    ],
                    {},
                ),
            ),
            (
                "Tracking Logic Comparison",
                test_tracking_logic_comparison,
                lambda ctx: (
                    [
                        session,
                        region,
                        _get_nested(ctx, "account_resolution", "puuid"),
                    ],
                    {"previous_match_id": "OLDER_THAN_LATEST_MATCH"},
                ),
            ),
            (
                "Aggregated Stats",
                test_aggregated_stats,
                lambda ctx: (
                    [
                        session,
                        region,
                        _get_nested(ctx, "account_resolution", "puuid"),
                    ],
                    {},
                ),
            ),
            (
                "Ranked Data Retrieval",
                test_ranked_data_retrieval,
                lambda ctx: ([session, region, _get_nested(ctx, "summoner_lookup", "summoner_id")], {}),
            ),
            (
                "Match Summary Message Generation",
                test_match_summary_message_generation,
                lambda ctx: (
                    [
                        {
                            "info": {
                                "participants": [
                                    {
                                        "puuid": _get_nested(ctx, "account_resolution", "puuid"),
                                        "championName": _get_nested(ctx, "match_details", "champion") or "Unknown Champion",
                                        "kills": _get_nested(ctx, "match_details", "kills") or 0,
                                        "deaths": _get_nested(ctx, "match_details", "deaths") or 0,
                                        "assists": _get_nested(ctx, "match_details", "assists") or 0,
                                        "win": _get_nested(ctx, "match_details", "win") or False,
                                    }
                                ]
                            }
                        },
                        _get_nested(ctx, "account_resolution", "puuid"),
                    ],
                    {},
                ),
            ),
            (
                "Telegram Delivery",
                test_telegram_delivery,
                lambda ctx: (
                    [
                        _get_nested(ctx, "message_generation", "summary")
                        or f"Functional test message for {riot_user}",
                        telegram_chat_id,
                    ],
                    {},
                ),
            ),
            (
                "Invalid Riot ID Edge Case",
                test_invalid_riot_id,
                lambda ctx: ([session, region], {}),
            ),
            (
                "Empty Match History Edge Case",
                test_empty_history_handling,
                lambda ctx: ([session, region, _get_nested(ctx, "account_resolution", "puuid")], {}),
            ),
            (
                "API Error Handling Edge Case",
                test_api_error_handling,
                lambda ctx: ([session, region], {}),
            ),
        ]

        context_keys = {
            "Account Resolution": "account_resolution",
            "Summoner Lookup by PUUID": "summoner_lookup",
            "Match History Retrieval": "match_history",
            "Match Detail Parsing": "match_details",
            "Tracking Logic Comparison": "tracking_logic",
            "Aggregated Stats": "aggregated_stats",
            "Ranked Data Retrieval": "ranked_data",
            "Match Summary Message Generation": "message_generation",
            "Telegram Delivery": "telegram_delivery",
            "Invalid Riot ID Edge Case": "invalid_riot_id",
            "Empty Match History Edge Case": "empty_history",
            "API Error Handling Edge Case": "api_error_handling",
        }

        for test_name, test_func, arg_builder in ordered_tests:
            args, kwargs = arg_builder(context)
            result = await _run_test(test_name, test_func, *args, **kwargs)
            results.append(result)
            context[context_keys[test_name]] = result.get("data", {})
            _print_step(result)

    print()

    if callable(format_test_report):
        report = format_test_report(riot_user, results)
    else:
        passed = sum(1 for item in results if item["status"] == "PASS")
        failed = sum(1 for item in results if item["status"] == "FAIL")
        warned = sum(1 for item in results if item["status"] == "WARN")
        lines = ["Riot Bot Test Report", f"User: {riot_user}", ""]
        for item in results:
            emoji = STATUS_EMOJI.get(item["status"], "•")
            lines.append(f"{emoji} {item['name']} - {item['status']}: {item['details']}")
        lines.extend(
            [
                "",
                "Summary",
                f"Passed: {passed}",
                f"Failed: {failed}",
                f"Warn: {warned}",
            ]
        )
        report = "\n".join(lines)

    print(report)

    if callable(send_telegram_report):
        await send_telegram_report(report)

    return 1 if any(item["status"] == "FAIL" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
