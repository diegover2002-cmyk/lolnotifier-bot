# Dev Key Constraints

## What is a Riot Dev Key?

A Riot Developer Key (`RGAPI-...`) is issued free at [developer.riotgames.com](https://developer.riotgames.com). It expires every 24 hours and has strict rate limits. It is intended for development and testing, not production use.

---

## Rate Limits

| Limit | Value |
|---|---|
| Per second | 20 requests |
| Per 2 minutes | 100 requests |

### How the bot enforces these limits

1. **`asyncio.Semaphore(20)`** in `riot_api.py` — caps concurrent in-flight requests to 20
2. **`await asyncio.sleep(RATE_LIMIT_DELAY)`** after every request — default `0.06s` ≈ 16 req/s
3. **`_MIN_POLL_GAP = 60s`** in `poller.py` — each player is polled at most once per minute
4. **429 handling** — if a 429 is received, the bot sleeps 60 seconds before continuing

With 28 pros + N users, each poll cycle makes at most `(28 + N) × 2` requests (1 for match history, 1 for match detail). At 16 req/s this takes about 4 seconds for 28 pros.

---

## Blocked Endpoints (403 on Dev Key)

These endpoints are implemented in the codebase but return 403 with a Dev Key:

| Endpoint | Function | Behavior on 403 |
|---|---|---|
| `GET /lol/summoner/v4/summoners/by-puuid/{puuid}` | `get_summoner_by_puuid()` | Returns `None`, logs at DEBUG |
| `GET /lol/league/v4/entries/by-summoner/{id}` | Not yet implemented | N/A |
| `GET /lol/spectator/v5/active-games/by-summoner/{id}` | Removed (dead code) | N/A |
| `GET /lol/champion-mastery/v4/...` | Removed (dead code) | N/A |

**No retries are attempted on 401/403.** These are permanent failures on a Dev Key, not transient errors. Retrying would waste rate limit budget and cause long hangs.

---

## Available Endpoints (Dev Key compatible)

| Endpoint | Function | Notes |
|---|---|---|
| `GET /riot/account/v1/accounts/by-riot-id/{name}/{tag}` | `get_account_by_riot_id()` | Returns PUUID, gameName, tagLine |
| `GET /lol/match/v5/matches/by-puuid/{puuid}/ids` | `get_match_history_ids()` | Returns list of match ID strings |
| `GET /lol/match/v5/matches/{matchId}` | `get_match_info()` | Returns full match payload |

---

## Cluster vs Region

Riot uses two different URL patterns:

- **Account API** (`account/v1`): uses regional clusters — `americas`, `europe`, `asia`
- **Match API** (`match/v5`): also uses clusters
- **Summoner/League APIs** (`summoner/v4`, `league/v4`): use platform regions — `euw1`, `kr`, `na1`

The mapping is in `config.py`:

```python
ACCOUNT_CLUSTERS = {
    "euw1": "europe",
    "kr":   "asia",
    "na1":  "americas",
    "la2":  "americas",
    # ...
}
```

---

## Production Key Upgrade Path

When upgrading to a production key:

1. Replace the `RIOT_API_KEY` value in `.env`
2. No code changes needed — all 403-guarded functions already return `None` gracefully
3. `get_summoner_by_puuid()` will start returning real data automatically
4. Ranked tier, live game, and champion mastery features can be wired in as new handlers

---

## Dev Key Expiry

Dev Keys expire every 24 hours. When the key expires:
- All Riot API calls return 401
- The bot logs `401` at DEBUG level and returns `None` / `[]`
- No crashes or infinite retries
- Renew the key at [developer.riotgames.com](https://developer.riotgames.com) and update `.env`
