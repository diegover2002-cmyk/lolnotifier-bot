# Future Improvements

## Short Term

### Production Key Features
Once a production Riot API key is obtained, these features activate with no code changes:

- **Summoner level** — `get_summoner_by_puuid()` already implemented, returns `None` on dev key
- **Ranked tier / LP** — needs `league/v4` handler wired to `/rank` command
- **Live game detection** — needs `spectator/v5` handler wired to `/live` command
- **Champion mastery** — needs `champion-mastery/v4` handler wired to `/mastery` command

### Database Integration Tests
`database.py` has no unit tests. Add tests using an in-memory SQLite database:

```python
import aiosqlite
from database import init_db, set_user_summoner, get_user

async def test_set_and_get_user():
    async with aiosqlite.connect(":memory:") as db:
        await init_db(":memory:")
        await set_user_summoner(":memory:", 123, "Caps#EUW", "euw1", ...)
        user = await get_user(":memory:", 123)
        assert user["game_name"] == "Caps"
```

### `/rank` Command
Aggregate stats for all tracked pros and display a ranked leaderboard:

```
/rank → fetch last 5 matches for each pro → aggregate → rank_players() → format_player_ranking()
```

---

## Medium Term

### Persistent PUUID Cache
Currently PUUIDs are stored in the DB after first resolution. If a player changes their Riot ID, the PUUID becomes stale. Add a periodic re-validation job that re-resolves PUUIDs for players not seen in 7 days.

### Multi-language Support
The bot currently sends messages in Spanish. Add a `language` column to `users` and a `locale` parameter to all formatter functions to support English and other languages.

### Webhook Mode
Currently uses long polling (`updater.start_polling()`). For production deployment, switch to webhook mode:

```python
await app.run_webhook(
    listen="0.0.0.0",
    port=8443,
    webhook_url=f"https://{DOMAIN}/{TELEGRAM_TOKEN}",
)
```

### Docker Deployment
A `Dockerfile` and `docker-compose.yml` are already present. Remaining work:
- Mount `.env` as a Docker secret instead of a file
- Add a health check endpoint
- Configure log volume persistence

---

## Long Term

### Conceptual CI/CD Plan

> This section describes a CI/CD pipeline that could be implemented when the project moves to production. No GitHub Actions are currently active.

**Proposed pipeline (GitHub Actions):**

```yaml
# On every push to main:
1. Lint (flake8 / ruff)
2. Type check (mypy)
3. Unit tests (pytest tests/ — 78 tests, no credentials needed)
4. Build Docker image
5. Push to container registry (on tag only)

# On pull requests:
1. Lint + type check
2. Unit tests
3. Block merge if any test fails
```

**Why functional tests are excluded from CI:**
- Require real Riot API key (Dev Key expires every 24h)
- Require real Telegram bot token
- Results depend on live game state (match history changes)
- Run manually before releases: `python functional_test_suite.py`

**Secrets in CI:**
- `TELEGRAM_TOKEN` and `RIOT_API_KEY` would be stored as GitHub Actions secrets
- Never printed in logs (`::add-mask::` annotation)

### Performance Monitoring
Add a simple metrics endpoint (or log-based metrics) tracking:
- Poll cycle duration
- API error rate by endpoint
- Notification delivery success rate
- Cache hit rate for PUUID lookups

### Rate Limit Budget Tracking
Track remaining rate limit budget using Riot API response headers (`X-Rate-Limit-Count`, `X-App-Rate-Limit`) and dynamically adjust `RATE_LIMIT_DELAY` instead of using a fixed value.
