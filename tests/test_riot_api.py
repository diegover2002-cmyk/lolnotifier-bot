import pytest
from unittest.mock import AsyncMock, patch
import aiohttp
from lolnotifier.riot_api import get_summoner

@pytest.mark.asyncio
async def test_get_summoner():
    with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status = 200
        mock_get.return_value.json.return_value = {'id': 'test'}
        result = await get_summoner(None, 'la2', 'test')
        assert result is not None

