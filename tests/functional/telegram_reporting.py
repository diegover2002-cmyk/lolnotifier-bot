from __future__ import annotations

import os
from typing import Any

import aiohttp


STATUS_EMOJIS = {
    "PASS": "✅",
    "FAIL": "❌",
    "WARN": "⚠️",
}


def build_result(
    name: str,
    status: str,
    details: str,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_status = status if status in STATUS_EMOJIS else "WARN"
    return {
        "name": name,
        "status": normalized_status,
        "details": details,
        "data": data or {},
    }


def format_test_report(
    test_user: str,
    results: list[dict[str, Any]],
) -> str:
    passed = sum(1 for result in results if result.get("status") == "PASS")
    failed = sum(1 for result in results if result.get("status") == "FAIL")
    warned = sum(1 for result in results if result.get("status") == "WARN")

    lines = [
        "Riot Bot Test Report",
        f"User: {test_user}",
        "",
    ]

    for result in results:
        status = result.get("status", "WARN")
        emoji = STATUS_EMOJIS.get(status, STATUS_EMOJIS["WARN"])
        name = result.get("name", "Unnamed test")
        details = result.get("details", "")
        lines.append(f"{emoji} {name}: {status} - {details}")

    lines.extend(
        [
            "",
            "Summary",
            f"Passed: {passed}",
            f"Failed: {failed}",
            f"Warn: {warned}",
        ]
    )

    return "\n".join(lines)


async def send_telegram_report(report: str) -> None:
    """Send the final test report to Telegram if token and chat_id are configured."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": report}
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    print(f"[WARN] Telegram report delivery failed with HTTP {resp.status}")
    except Exception as exc:
        print(f"[WARN] Could not send Telegram report: {exc}")