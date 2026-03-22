"""
Unit tests for handlers.py.
Telegram Update/Context objects are mocked — no real bot connection needed.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from handlers import set_summoner, status, toggle_notifs, list_pros


def _make_update(user_id: int = 123) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = user_id
    update.message.reply_text = AsyncMock()
    return update


def _make_context(*args: str) -> MagicMock:
    ctx = MagicMock()
    ctx.args = list(args)
    return ctx


# ── /set_summoner ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_summoner_missing_args():
    update = _make_update()
    ctx = _make_context()  # no args
    await set_summoner(update, ctx)
    update.message.reply_text.assert_called_once()
    call_text = update.message.reply_text.call_args[0][0]
    assert "Uso:" in call_text


@pytest.mark.asyncio
async def test_set_summoner_bad_format_no_hash():
    update = _make_update()
    ctx = _make_context("PlayerName", "euw1")  # no # in riot id
    await set_summoner(update, ctx)
    update.message.reply_text.assert_called_once()
    call_text = update.message.reply_text.call_args[0][0]
    assert "Formato" in call_text or "Uso:" in call_text


@pytest.mark.asyncio
async def test_set_summoner_account_not_found():
    update = _make_update()
    ctx = _make_context("FakePlayer#EUW", "euw1")

    with patch("handlers._resolve_account", new_callable=AsyncMock, return_value=None):
        await set_summoner(update, ctx)

    calls = [c[0][0] for c in update.message.reply_text.call_args_list]
    assert any("❌" in t or "No encontré" in t for t in calls)


@pytest.mark.asyncio
async def test_set_summoner_success():
    update = _make_update()
    ctx = _make_context("Caps#EUW", "euw1")

    fake_account = {"puuid": "abc-puuid-123", "gameName": "Caps", "tagLine": "EUW"}

    with (
        patch("handlers._resolve_account", new_callable=AsyncMock, return_value=fake_account),
        patch("handlers.set_user_summoner", new_callable=AsyncMock),
    ):
        await set_summoner(update, ctx)

    calls = [c[0][0] for c in update.message.reply_text.call_args_list]
    assert any("✅" in t for t in calls)


# ── /status ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_status_no_user():
    update = _make_update()
    ctx = _make_context()

    with patch("handlers.get_user", new_callable=AsyncMock, return_value=None):
        await status(update, ctx)

    call_text = update.message.reply_text.call_args[0][0]
    assert "No tienes" in call_text or "set_summoner" in call_text


@pytest.mark.asyncio
async def test_status_with_user():
    update = _make_update()
    ctx = _make_context()

    fake_user = {
        "user_id": 123,
        "summoner_name": "Caps#EUW",
        "game_name": "Caps",
        "tag_line": "EUW",
        "region": "euw1",
        "notifications_enabled": True,
        "last_match_id": "EUW1_999",
        "last_poll_time": "2026-03-22 01:00:00",
    }

    with patch("handlers.get_user", new_callable=AsyncMock, return_value=fake_user):
        await status(update, ctx)

    call_text = update.message.reply_text.call_args[0][0]
    assert "Caps" in call_text
    assert "euw1" in call_text


# ── /toggle ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_toggle_no_user():
    update = _make_update()
    ctx = _make_context()

    with patch("handlers.get_user", new_callable=AsyncMock, return_value=None):
        await toggle_notifs(update, ctx)

    call_text = update.message.reply_text.call_args[0][0]
    assert "set_summoner" in call_text or "Liga" in call_text


@pytest.mark.asyncio
async def test_toggle_disables_notifications():
    update = _make_update()
    ctx = _make_context()

    fake_user = {"user_id": 123, "notifications_enabled": True}

    with (
        patch("handlers.get_user", new_callable=AsyncMock, return_value=fake_user),
        patch("handlers.toggle_notifications", new_callable=AsyncMock) as mock_toggle,
    ):
        await toggle_notifs(update, ctx)

    # Should have been called with enabled=False (toggled off)
    mock_toggle.assert_called_once()
    assert mock_toggle.call_args[0][2] is False


# ── /list_pros ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_pros_empty():
    update = _make_update()
    ctx = _make_context()

    with patch("handlers.get_all_pros", new_callable=AsyncMock, return_value=[]):
        await list_pros(update, ctx)

    call_text = update.message.reply_text.call_args[0][0]
    assert "No hay" in call_text or "add_pro" in call_text


@pytest.mark.asyncio
async def test_list_pros_with_data():
    update = _make_update()
    ctx = _make_context()

    fake_pros = [
        {"id": 1, "game_name": "Caps", "tag_line": "EUW", "region": "euw1", "team": "G2", "role": "MID"},
        {"id": 2, "game_name": "Faker", "tag_line": "KR1", "region": "kr", "team": "T1", "role": "MID"},
    ]

    with patch("handlers.get_all_pros", new_callable=AsyncMock, return_value=fake_pros):
        await list_pros(update, ctx)

    call_text = update.message.reply_text.call_args[0][0]
    assert "Caps" in call_text
    assert "Faker" in call_text
