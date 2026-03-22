import pytest
from unittest.mock import AsyncMock, MagicMock
from lolnotifier.handlers import set_summoner, status

@pytest.mark.asyncio
async def test_set_summoner(monkeypatch):
    update = MagicMock()
    update.effective_user.id = 123
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["TestUser", "la2"]

    async def fake_set_user_summoner(db_path, user_id, summoner_name, region):
        assert user_id == 123
        assert summoner_name == "TestUser"
        assert region == "la2"
    monkeypatch.setattr("lolnotifier.handlers.set_user_summoner", fake_set_user_summoner)

    await set_summoner(update, context)
    update.message.reply_text.assert_called_with("¡Cuenta ligada! TestUser en la2. Notifs pronto.")

@pytest.mark.asyncio
async def test_status_no_user(monkeypatch):
    update = MagicMock()
    update.effective_user.id = 123
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    async def fake_get_user(db_path, user_id):
        return None
    monkeypatch.setattr("lolnotifier.handlers.get_user", fake_get_user)

    await status(update, context)
    update.message.reply_text.assert_called_with('No cuenta ligada. /set_lol_summoner')
