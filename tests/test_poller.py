import pytest
from unittest.mock import AsyncMock, MagicMock
from lolnotifier.poller import poll_users

@pytest.mark.asyncio
async def test_poll_users_handles_error(monkeypatch):
    session = MagicMock()
    bot = MagicMock()
    db_path = "test.db"

    async def fake_get_all_users(db_path):
        return [{"user_id": 1, "region": "la2", "summoner_name": "TestUser", "last_match_id": None, "notifications_enabled": True}]
    async def fake_get_summoner(session, region, summoner_name):
        raise Exception("API error")
    monkeypatch.setattr("lolnotifier.poller.get_all_users", fake_get_all_users)
    monkeypatch.setattr("lolnotifier.poller.get_summoner", fake_get_summoner)

    bot.send_message = AsyncMock()
    # Run only one iteration
    async def fake_sleep(x):
        raise Exception("break loop")
    monkeypatch.setattr("asyncio.sleep", fake_sleep)

    try:
        await poll_users(session, bot, db_path)
    except Exception as e:
        assert str(e) == "break loop"
    bot.send_message.assert_called()
