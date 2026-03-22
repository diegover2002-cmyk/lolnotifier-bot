"""
Unit tests for poller.py.
All external calls (DB, Riot API, Telegram) are mocked.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from poller import _last_poll_age, _resolve_puuid, _process_player


# ── _last_poll_age (pure) ─────────────────────────────────────────────────────

def test_last_poll_age_none_returns_infinity():
    assert _last_poll_age(None) == float("inf")


def test_last_poll_age_invalid_returns_infinity():
    assert _last_poll_age("not-a-date") == float("inf")


def test_last_poll_age_recent_is_small():
    import time
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    age = _last_poll_age(now)
    assert 0 <= age < 5  # should be less than 5 seconds old


def test_last_poll_age_old_is_large():
    age = _last_poll_age("2000-01-01 00:00:00")
    assert age > 1_000_000


# ── _resolve_puuid ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_puuid_cached():
    """If record already has a PUUID, return it without any API call."""
    session = MagicMock()
    record = {"puuid": "cached-puuid", "region": "euw1"}
    result = await _resolve_puuid(session, record)
    assert result == "cached-puuid"


@pytest.mark.asyncio
async def test_resolve_puuid_resolves_via_api():
    """If no PUUID cached, call account/v1 to resolve it."""
    session = MagicMock()
    record = {"game_name": "Caps", "tag_line": "EUW", "region": "euw1"}

    fake_account = {"puuid": "resolved-puuid"}
    with patch("poller.get_account_by_riot_id", new_callable=AsyncMock, return_value=fake_account):
        result = await _resolve_puuid(session, record)

    assert result == "resolved-puuid"


@pytest.mark.asyncio
async def test_resolve_puuid_api_returns_none():
    session = MagicMock()
    record = {"game_name": "Unknown", "tag_line": "NOPE", "region": "euw1"}

    with patch("poller.get_account_by_riot_id", new_callable=AsyncMock, return_value=None):
        result = await _resolve_puuid(session, record)

    assert result is None


# ── _process_player ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_process_player_no_new_match():
    """If latest match ID equals stored ID, return None (no notification)."""
    session = MagicMock()
    bot = MagicMock()
    record = {
        "puuid": "test-puuid",
        "region": "euw1",
        "last_match_id": "EUW1_100",
        "game_name": "Caps",
        "tag_line": "EUW",
        "user_id": 1,
    }

    with patch("poller.get_match_history_ids", new_callable=AsyncMock, return_value=["EUW1_100"]):
        result = await _process_player(session, bot, record, notify_ids=[1])

    assert result is None
    bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_process_player_new_match_sends_notification():
    """If a new match is detected, fetch details and send a message."""
    session = MagicMock()
    bot = AsyncMock()
    record = {
        "puuid": "test-puuid",
        "region": "euw1",
        "last_match_id": "EUW1_OLD",
        "game_name": "Caps",
        "tag_line": "EUW",
        "team": "G2",
        "user_id": 1,
    }

    fake_match = {
        "metadata": {"matchId": "EUW1_NEW"},
        "info": {
            "queueId": 420,
            "gameMode": "CLASSIC",
            "gameDuration": 1800,
            "participants": [{
                "puuid": "test-puuid",
                "championName": "Orianna",
                "kills": 5, "deaths": 2, "assists": 10,
                "win": True,
                "totalMinionsKilled": 200, "neutralMinionsKilled": 10,
                "goldEarned": 14000,
                "totalDamageDealtToChampions": 25000,
                "visionScore": 30,
                "firstBloodKill": False,
                "turretKills": 1,
                "doubleKills": 1, "tripleKills": 0,
                "quadraKills": 0, "pentaKills": 0,
            }],
        },
    }

    with patch("poller.get_match_history_ids", new_callable=AsyncMock, return_value=["EUW1_NEW"]), \
         patch("poller.get_match_info", new_callable=AsyncMock, return_value=fake_match), \
         patch("poller.update_pro_puuid", new_callable=AsyncMock), \
         patch("poller.update_user_puuid", new_callable=AsyncMock):
        result = await _process_player(session, bot, record, notify_ids=[999])

    assert result == "EUW1_NEW"
    bot.send_message.assert_called_once_with(999, pytest.approx(bot.send_message.call_args[0][1], abs=0))


@pytest.mark.asyncio
async def test_process_player_no_history_returns_none():
    session = MagicMock()
    bot = MagicMock()
    record = {"puuid": "test-puuid", "region": "euw1", "last_match_id": None}

    with patch("poller.get_match_history_ids", new_callable=AsyncMock, return_value=[]):
        result = await _process_player(session, bot, record, notify_ids=[1])

    assert result is None
