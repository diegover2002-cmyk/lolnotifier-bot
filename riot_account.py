import aiohttp
from urllib.parse import quote
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
from config import RIOT_API_KEY, ACCOUNT_CLUSTERS

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_account_by_riot_id(session: aiohttp.ClientSession, cluster: str, game_name: str, tag_line: str) -> Optional[Dict[str, Any]]:
    """DEV KEY SAFE: GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"""
    url = f"https://{cluster}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    headers = {'X-Riot-Token': RIOT_API_KEY or ''}
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status in (404, 403):
                return None
            resp.raise_for_status()
    except asyncio.CancelledError:
        print(f"[ERROR] CancelledError: La tarea fue cancelada al consultar {url}")
        return None
    except asyncio.TimeoutError:
        print(f"[ERROR] TimeoutError: La consulta a {url} excedió el tiempo límite")
        return None
    except Exception as e:
        print(f"[ERROR] Excepción inesperada en get_account_by_riot_id: {e}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_puuid_by_game_name(session: aiohttp.ClientSession, cluster: str, game_name: str, tag_line: str) -> Optional[str]:
    account = await get_account_by_riot_id(session, cluster, game_name, tag_line)
    return account['puuid'] if account else None