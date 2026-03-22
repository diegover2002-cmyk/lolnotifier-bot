# Contributing to LoLNotifierBot

Thanks for your interest in contributing. This guide covers everything you need to add pro players, write tests, follow code style, and submit pull requests.

---

## Table of Contents

1. [Adding Pro Players](#adding-pro-players)
2. [Writing Tests](#writing-tests)
3. [Code Style](#code-style)
4. [Branching and Pull Requests](#branching-and-pull-requests)
5. [Secrets and Security](#secrets-and-security)

---

## Adding Pro Players

### Option A — Via Telegram (runtime, not persisted to dataset)

```
/add_pro GameName#TAG region
```

Example: `/add_pro Faker#KR1 kr`

This adds the player to the database immediately. The entry is lost if the database is reset.

### Option B — Via `pro_players.py` (permanent, recommended)

Open `pro_players.py` and add an entry to `PRO_PLAYERS`:

```python
{"game_name": "PlayerName", "tag_line": "TAG", "region": "euw1", "team": "TeamName", "role": "MID"},
```

Valid roles: `TOP`, `JGL`, `MID`, `BOT`, `SUP`

Valid regions: `na1`, `euw1`, `eun1`, `kr`, `la1`, `la2`, `br1`, `jp1`, `tr1`

After editing, run `/load_pros` in Telegram to sync the database.

**Verification before submitting:**
- Confirm the Riot ID is correct on [op.gg](https://op.gg) or [u.gg](https://u.gg)
- Confirm the account exists via `account/v1` (the functional test suite does this automatically)
- Do not include private or unverified accounts

---

## Writing Tests

### Unit tests (no API calls)

All unit tests live in `tests/`. They use `unittest.mock` — no real network calls.

```bash
python -m pytest tests/ -v
```

**Rules:**
- Pure functions (`stats.py`, `formatter.py`) need no mocks — test them directly
- Functions that call the DB or Riot API must be mocked with `AsyncMock` / `patch`
- Each test function must be independent — no shared mutable state
- Use `pytest.mark.asyncio` for async tests (or rely on `asyncio_mode = auto` in `pytest.ini`)

**Example — pure function test:**

```python
from stats import aggregate_stats

def test_aggregate_stats_empty():
    result = aggregate_stats([])
    assert result["games"] == 0
    assert result["winrate"] == 0.0
```

**Example — mocked async test:**

```python
from unittest.mock import AsyncMock, patch
from handlers import status

async def test_status_no_user():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 123

    with patch("handlers.get_user", new_callable=AsyncMock, return_value=None):
        await status(update, MagicMock())

    update.message.reply_text.assert_called_once()
```

### Functional tests (real API, requires `.env`)

Functional tests live in `tests/functional/` and require valid credentials in `.env`.

```bash
python functional_test_suite.py
```

Do not add functional tests that depend on specific match IDs or account states — they will break as the game state changes.

---

## Code Style

### General

- Follow **PEP 8** — 4-space indentation, max line length 100
- Use **type hints** on all function signatures
- Use `from __future__ import annotations` at the top of every module
- Prefer `logging.getLogger(__name__)` over `print()`
- No hardcoded credentials, tokens, or PUUIDs anywhere in source code

### Naming

| Thing | Convention | Example |
|---|---|---|
| Functions | `snake_case` | `get_match_info` |
| Private helpers | `_snake_case` | `_rate_delay` |
| Constants | `UPPER_SNAKE` | `POLL_INTERVAL` |
| Classes | `PascalCase` | `ProEntry` |
| Test functions | `test_<what>_<condition>` | `test_parse_match_for_puuid_not_found` |

### Docstrings

Every public function must have a docstring. Use this format:

```python
def get_match_info(session, region, match_id):
    """
    Fetch full match details for a given match ID via match/v5.

    Args:
        session:  Active aiohttp session.
        region:   Platform region code (e.g. 'euw1', 'kr').
        match_id: Match ID string (e.g. 'EUW1_7123456789').

    Returns:
        Full match/v5 payload dict, or None on 401/403/404.
    """
```

### Async

- Use `async with session.get(...)` — never `await session.get(...)` without context manager
- Always call `await _rate_delay()` after each Riot API request
- Use `asyncio.Semaphore` for concurrency control, not `asyncio.sleep` alone
- Never block the event loop with synchronous I/O

### Error handling

- Catch specific exceptions, not bare `except:`
- On 401/403/404 from Riot API: return `None` or `[]`, log at `DEBUG` level
- On 429: log at `WARNING`, sleep 60s before retrying
- Use `tenacity` for retry logic on transient network errors

---

## Branching and Pull Requests

### Branch naming

```
feature/<short-description>    # new functionality
fix/<short-description>        # bug fix
docs/<short-description>       # documentation only
chore/<short-description>      # tooling, deps, cleanup
```

Examples: `feature/add-ranked-stats`, `fix/poller-timezone-bug`, `docs/update-readme`

### Commit messages

Use the conventional commits format:

```
feat: add /rank command for pro player leaderboard
fix: handle 429 rate limit in get_match_info
docs: add architecture diagram to docs/
chore: update requirements.txt to aiohttp 3.13.3
test: add unit tests for aggregate_stats edge cases
refactor: move _rate_delay to shared helper
```

### Pull request checklist

Before opening a PR:

- [ ] All 78 unit tests pass: `python -m pytest tests/ -v`
- [ ] No new `print()` statements — use `logger.*`
- [ ] No credentials, tokens, or PUUIDs in code or tests
- [ ] New functions have docstrings and type hints
- [ ] `CHANGELOG.md` updated if adding a feature or fixing a bug
- [ ] PR description explains what changed and why

---

## Secrets and Security

- **Never** commit `.env`, API keys, Telegram tokens, or PUUIDs
- `.gitignore` already excludes `.env` and `*.db`
- Use placeholder values in examples: `<your_token>`, `<your_api_key>`
- If you accidentally commit a secret, rotate it immediately and force-push to remove it from history
- See [SECURITY.md](SECURITY.md) for the full policy
