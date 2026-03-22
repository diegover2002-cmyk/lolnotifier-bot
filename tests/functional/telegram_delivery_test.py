from __future__ import annotations

from typing import Any

import aiohttp

from config import TELEGRAM_TOKEN
from .telegram_reporting import build_result


TELEGRAM_API_BASE = "https://api.telegram.org"


async def test_telegram_delivery(
    message_text: str,
    chat_id: str | int | None,
    token: str | None = None,
) -> dict[str, Any]:
    telegram_token = token or TELEGRAM_TOKEN

    if not telegram_token:
        return build_result(
            name="telegram_delivery",
            status="WARN",
            details="TELEGRAM_TOKEN is not configured; Telegram delivery test skipped.",
            data={},
        )

    if not chat_id:
        return build_result(
            name="telegram_delivery",
            status="WARN",
            details="TELEGRAM_CHAT_ID is not configured; Telegram delivery test skipped.",
            data={},
        )

    if not message_text or not str(message_text).strip():
        return build_result(
            name="telegram_delivery",
            status="FAIL",
            details="Message text is empty.",
            data={},
        )

    url = f"{TELEGRAM_API_BASE}/bot{telegram_token}/sendMessage"
    payload = {
        "chat_id": str(chat_id),
        "text": message_text,
    }

    timeout = aiohttp.ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    try:
                        response_json = await response.json(content_type=None)
                    except Exception:
                        response_json = {}
                    message = response_json.get("result", {})
                    return build_result(
                        name="telegram_delivery",
                        status="PASS",
                        details="Telegram message sent successfully.",
                        data={
                            "chat_id": str(chat_id),
                            "message_id": message.get("message_id"),
                            "http_status": response.status,
                        },
                    )

                return build_result(
                    name="telegram_delivery",
                    status="FAIL",
                    details=f"Telegram API returned HTTP {response.status}.",
                    data={
                        "chat_id": str(chat_id),
                        "http_status": response.status,
                    },
                )
    except Exception as exc:
        return build_result(
            name="telegram_delivery",
            status="FAIL",
            details=f"Telegram delivery raised an exception: {exc}",
            data={
                "chat_id": str(chat_id),
                "error_type": type(exc).__name__,
            },
        )