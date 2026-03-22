"""
Unit tests for riot_api.py.
All HTTP calls are mocked — no real API requests are made.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp

from riot_api import get_match_history_ids, get_match_info, parse_match_for_puuid


# ── parse_match_for_puuid (pure, no mocks needed) ────────────────────────────

SAMPLE_MATCH = {
    "metadata": {"matchId": "EUW1_123"},
    "info": {
        "queueId": 420,
        "gameMode": "CLASSIC",
        "gameDuration": 1800,
        "participants": [
            {
                "puuid": "test-puuid",
                "championName": "Graves",
                "kills": 10,
                "deaths": 8,
                "assists": 6,
                "win": False,
            }
        ],
    },
}


def test_parse_match_for_puuid_found():
    result = parse_match_for_puuid(SAMPLE_MATCH, "test-puuid")
    assert result is not None
    assert result["champion"] == "Graves"
    assert result["kills"] == 10
    assert result["deaths"] == 8
    assert result["assists"] == 6
    assert result["kda"] == "10/8/6"
    assert result["win"] is False
    assert result["match_id"] == "EUW1_123"
    assert result["queue_id"] == 420
    assert result["duration_seconds"] == 1800


def test_parse_match_for_puuid_not_found():
    result = parse_match_for_puuid(SAMPLE_MATCH, "unknown-puuid")
    assert result is None


def test_parse_match_for_puuid_empty_match():
    result = parse_match_for_puuid({}, "any-puuid")
    assert result is None


def test_parse_match_for_puuid_zero_deaths():
    match = {
        "metadata": {"matchId": "EUW1_999"},
        "info": {
            "queueId": 420,
            "gameMode": "CLASSIC",
            "gameDuration": 900,
            "participants": [
                {
                    "puuid": "p1",
                    "championName": "Jinx",
                    "kills": 5,
                    "deaths": 0,
                    "assists": 3,
                    "win": True,
                }
            ],
        },
    }
    result = parse_match_for_puuid(match, "p1")
    assert result is not None
    assert result["kda"] == "5/0/3"
    assert result["win"] is True


# ── get_match_history_ids (mocked HTTP) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_match_history_ids_success():
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["EUW1_1", "EUW1_2", "EUW1_3"])
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_resp)

    with patch("riot_api.RIOT_API_KEY", "fake-key"), \
         patch("riot_api._rate_delay", new_callable=AsyncMock):
        result = await get_match_history_ids(mock_session, "euw1", "test-puuid", count=3)

    assert result == ["EUW1_1", "EUW1_2", "EUW1_3"]


@pytest.mark.asyncio
async def test_get_match_history_ids_403_returns_empty():
    mock_resp = AsyncMock()
    mock_resp.status = 403
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_resp)

    with patch("riot_api.RIOT_API_KEY", "fake-key"), \
         patch("riot_api._rate_delay", new_callable=AsyncMock):
        result = await get_match_history_ids(mock_session, "euw1", "test-puuid")

    assert result == []


# ── get_match_info (mocked HTTP) ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_match_info_success():
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=SAMPLE_MATCH)
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_resp)

    with patch("riot_api.RIOT_API_KEY", "fake-key"), \
         patch("riot_api._rate_delay", new_callable=AsyncMock):
        result = await get_match_info(mock_session, "euw1", "EUW1_123")

    assert result == SAMPLE_MATCH


@pytest.mark.asyncio
async def test_get_match_info_404_returns_none():
    mock_resp = AsyncMock()
    mock_resp.status = 404
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_resp)

    with patch("riot_api.RIOT_API_KEY", "fake-key"), \
         patch("riot_api._rate_delay", new_callable=AsyncMock):
        result = await get_match_info(mock_session, "euw1", "EUW1_NOTFOUND")

    assert result is None
