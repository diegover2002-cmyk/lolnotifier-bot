"""
Riot account/v1 helpers — Dev Key compatible.

Provides Riot ID (GameName#TAG) → PUUID resolution via the
account/v1 endpoint, which is available on all key tiers.

URL-encodes game names to handle accented characters (e.g. LaBísica).
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional
from urllib.parse import quote

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from config import RIOT_API_KEY

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_account_by_riot_id(
    session: aiohttp.ClientSession,
    cluster: str,
    game_name: str,
    tag_line: str,
) -> Optional[dict[str, Any]]:
    """
    Resolve a Riot ID to an account dict via account/v1.

    Args:
        session:   Active aiohttp session.
        cluster:   Regional cluster (e.g. 'europe', 'americas', 'asia').
        game_name: GameName portion of the Riot ID (URL-encoded automatically).
        tag_line:  TAG portion of the Riot ID, without the '#'.

    Returns:
        Dict with 'puuid', 'gameName', 'tagLine' on success.
        None on 404 (account not found) or 403 (key restriction).

    Raises:
        aiohttp.ClientResponseError: On 5xx or unexpected status codes,
            triggering tenacity retry up to 3 attempts.
    """
    url = (
        f"https://{cluster}.api.riotgames.com"
        f"/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    )
    headers = {"X-Riot-Token": RIOT_API_KEY or ""}
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                return await resp.json()
            if resp.status in (403, 404):
                logger.debug("account/v1 returned %d for %s#%s", resp.status, game_name, tag_line)
                return None
            resp.raise_for_status()
    except asyncio.CancelledError:
        logger.warning("CancelledError during account lookup for %s#%s", game_name, tag_line)
        return None
    except asyncio.TimeoutError:
        logger.warning("Timeout during account lookup for %s#%s", game_name, tag_line)
        return None
    except Exception:
        logger.exception("Unexpected error in get_account_by_riot_id for %s#%s", game_name, tag_line)
        return None
    return None


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_puuid_by_game_name(
    session: aiohttp.ClientSession,
    cluster: str,
    game_name: str,
    tag_line: str,
) -> Optional[str]:
    """
    Convenience wrapper: Riot ID → PUUID string.

    Args:
        session:   Active aiohttp session.
        cluster:   Regional cluster (e.g. 'europe', 'americas', 'asia').
        game_name: GameName portion of the Riot ID.
        tag_line:  TAG portion of the Riot ID.

    Returns:
        PUUID string, or None if the account is not found.
    """
    account = await get_account_by_riot_id(session, cluster, game_name, tag_line)
    return account["puuid"] if account else None
