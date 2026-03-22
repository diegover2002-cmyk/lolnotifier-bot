import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from config import RIOT_API_KEY, REGIONS, RIOT_API_BASE, RATE_LIMIT_DELAY, CACHE_TTL_SUMMONER, CACHE_TTL_CHAMPION, ACCOUNT_CLUSTERS

logger = logging.getLogger(__name__)

# Global semaphore for rate limiting (20 concurrent)
rate_semaphore = asyncio.Semaphore(20)

# Simple in-memory caches
summoner_cache = {}
active_game_cache = {}
champion_cache = {}

async def _rate_delay():
    await asyncio.sleep(RATE_LIMIT_DELAY)

async def _is_cache_valid(timestamp: datetime, ttl: int) -> bool:
    return datetime.now() < timestamp + timedelta(seconds=ttl)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type((aiohttp.ClientResponseError,)),
    reraise=True
)
async def get_summoner_by_puuid(session: aiohttp.ClientSession, region: str, puuid: str) -> Optional[Dict[str, Any]]:
    """DEV SAFE: summoner/v4/by-puuid"""
    cache_key = f"{region}_{puuid}"
    async with rate_semaphore:
        if cache_key in summoner_cache:
            data, ts = summoner_cache[cache_key]
            if await _is_cache_valid(ts, CACHE_TTL_SUMMONER):
                logger.debug(f"Cache hit for summoner {cache_key}")
                return data
        url = RIOT_API_BASE.format(region=REGIONS[region]) + f'/summoner/v4/summoners/by-puuid/{puuid}'
        headers = {'X-Riot-Token': RIOT_API_KEY or ''}
        async with session.get(url, headers=headers) as resp:
            if resp.status == 429:
                logger.warning("Riot rate limit hit (429). Backing off...")
                await asyncio.sleep(60)
            if resp.status == 200:
                data = await resp.json()
                summoner_cache[cache_key] = (data, datetime.now())
                await _rate_delay()
                return data
            elif resp.status in (404, 401, 403):
                await _rate_delay()
                return None
            resp.raise_for_status()

from riot_account import get_puuid_by_game_name

async def get_summoner(session: aiohttp.ClientSession, region: str, game_name: str, tag_line: str) -> Optional[Dict[str, Any]]:
    """Wrapper: Riot ID → PUUID → Summoner"""
    cluster = ACCOUNT_CLUSTERS[region]
    puuid = await get_puuid_by_game_name(session, cluster, game_name, tag_line)
    if not puuid:
        logger.warning(f"No PUUID found for {game_name}#{tag_line}")
        return None
    return await get_summoner_by_puuid(session, region, puuid)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type((aiohttp.ClientResponseError,)),
    reraise=True
)
async def get_active_game(session: aiohttp.ClientSession, region: str, summoner_id: str) -> Optional[Dict[str, Any]]:
    cache_key = f"{region}_{summoner_id}"
    async with rate_semaphore:
        if cache_key in active_game_cache:
            data, ts = active_game_cache[cache_key]
            if await _is_cache_valid(ts, CACHE_TTL_SUMMONER):
                logger.debug(f"Cache hit for active_game {cache_key}")
                return data
        url = RIOT_API_BASE.format(region=REGIONS[region]) + f'/spectator/v4/active-games/by-summoner/{summoner_id}'
        headers = {'X-Riot-Token': RIOT_API_KEY or ''}
        async with session.get(url, headers=headers) as resp:
            if resp.status == 429:
                logger.warning("Riot rate limit hit (429). Backing off...")
                await asyncio.sleep(60)
            if resp.status == 200:
                data = await resp.json()
                active_game_cache[cache_key] = (data, datetime.now())
                await _rate_delay()
                return data
            elif resp.status == 404:
                active_game_cache[cache_key] = ({}, datetime.now())  # Cache no game
                await _rate_delay()
                return None
            resp.raise_for_status()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
async def get_match_info(session: aiohttp.ClientSession, region: str, match_id: str) -> Optional[Dict[str, Any]]:
    # No cache for matches (one-off)
    async with rate_semaphore:
        cluster = ACCOUNT_CLUSTERS.get(region, "europe")
        url = f'https://{cluster}.api.riotgames.com/lol/match/v5/matches/{match_id}'
        headers = {'X-Riot-Token': RIOT_API_KEY or ''}
        async with session.get(url, headers=headers) as resp:
            await _rate_delay()
            if resp.status == 200:
                return await resp.json()
            elif resp.status in (401, 403, 404):
                return None
            resp.raise_for_status()

async def get_match_history_ids(
    session: aiohttp.ClientSession,
    region: str,
    puuid: str,
    *,
    start: int = 0,
    count: int = 5,
) -> list[str]:
    """DEV KEY SAFE: match/v5/matches/by-puuid/{puuid}/ids"""
    cluster = ACCOUNT_CLUSTERS.get(region, "europe")
    url = (
        f"https://{cluster}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        f"?start={start}&count={count}"
    )
    headers = {"X-Riot-Token": RIOT_API_KEY or ""}
    async with rate_semaphore:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            await _rate_delay()
            if resp.status == 200:
                data = await resp.json()
                return data if isinstance(data, list) else []
            elif resp.status in (401, 403, 404):
                return []
            resp.raise_for_status()
    return []


def parse_match_for_puuid(
    match_info: dict,
    puuid: str,
) -> Optional[Dict[str, Any]]:
    """Extract a player's core stats from a match/v5 payload."""
    info = match_info.get("info", {})
    metadata = match_info.get("metadata", {})
    participants = info.get("participants", [])
    player = next((p for p in participants if p.get("puuid") == puuid), None)
    if not player:
        return None
    kills = int(player.get("kills", 0))
    deaths = int(player.get("deaths", 0))
    assists = int(player.get("assists", 0))
    return {
        "match_id": metadata.get("matchId"),
        "queue_id": info.get("queueId"),
        "game_mode": info.get("gameMode"),
        "champion": player.get("championName"),
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kda": f"{kills}/{deaths}/{assists}",
        "win": bool(player.get("win")),
        "duration_seconds": info.get("gameDuration"),
    }


async def get_champion_name(champion_id: int, region: str = 'la2') -> str:
    cache_key = region
    if cache_key in champion_cache:
        data, ts = champion_cache[cache_key]
        if asyncio.run(_is_cache_valid(ts, CACHE_TTL_CHAMPION)):
            return data.get(champion_id, f"Champion_{champion_id}")
    # Placeholder - real static fetch requires session, done in poller
    return f"Champion_{champion_id}"

async def get_static_champions(session: aiohttp.ClientSession, region: str) -> Dict[int, str]:
    cache_key = region
    if cache_key in champion_cache:
        data, ts = champion_cache[cache_key]
        if await _is_cache_valid(ts, CACHE_TTL_CHAMPION):
            return data
    async with rate_semaphore:
        url = RIOT_API_BASE.format(region=REGIONS[region]) + '/lol/data/en_US/champion.json'  # Fixed path
        headers = {'X-Riot-Token': RIOT_API_KEY or ''}
        async with session.get(url, headers=headers) as resp:
            await _rate_delay()
            if resp.status == 200:
                data = await resp.json()
                champs = {int(k): v['name'] for k, v in data['data'].items()}
                champion_cache[cache_key] = (champs, datetime.now())
                return champs
            logger.warning(f"Failed to fetch champions for {region}")
            return {}