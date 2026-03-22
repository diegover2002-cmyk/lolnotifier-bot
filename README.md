# LoLNotifierBot

Telegram bot that tracks League of Legends players using the Riot Games API.
Notifies you when tracked players finish a match, with full stats.

---

## Features (Dev Key compatible)

| Feature | Status | Endpoint |
|---|---|---|
| Riot ID → PUUID resolution | ✅ | `account/v1` |
| Match history retrieval | ✅ | `match/v5/by-puuid` |
| Match detail parsing (KDA, CS, gold, damage, vision) | ✅ | `match/v5/{id}` |
| New match detection & notification | ✅ | `match/v5` polling |
| Aggregated stats (winrate, avg KDA, CS/min, perf score) | ✅ | `match/v5` |
| Player ranking by performance score | ✅ | Computed locally |
| Rich Telegram messages | ✅ | Telegram Bot API |
| Pro player dataset (28 players, 4 regions) | ✅ | Static |
| Summoner level | ⚠️ Dev key 403 | `summoner/v4` |
| Ranked tier/LP | ⚠️ Dev key 403 | `league/v4` |
| Live game detection | ⚠️ Dev key 403 | `spectator/v5` |
| Champion mastery | ⚠️ Dev key 403 | `champion-mastery/v4` |

All ⚠️ features will activate automatically on production key upgrade — no code changes needed.

---

## Dev Key Rate Limits

- 20 requests / second
- 100 requests / 2 minutes
- Bot polls each player at most once per 60 seconds
- `RATE_LIMIT_DELAY` in `.env` controls per-request delay (default: 0.06s)

---

## Setup

```bash
cd lolnotifier
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env
# Fill in TELEGRAM_TOKEN, RIOT_API_KEY, TELEGRAM_CHAT_ID
python main.py
```

### `.env` variables

```
TELEGRAM_TOKEN=        # BotFather token
RIOT_API_KEY=          # developer.riotgames.com
TELEGRAM_CHAT_ID=      # your Telegram user ID
RIOT_GAME_NAME=        # your GameName (for tests)
RIOT_TAG_LINE=         # your #TAG (for tests)
RIOT_REGION=euw1       # your region (for tests)
POLL_INTERVAL=300      # seconds between poll cycles
RATE_LIMIT_DELAY=0.06  # seconds between API calls
```

---

## Bot Commands

| Command | Description |
|---|---|
| `/set_summoner GameName#TAG region` | Link your LoL account |
| `/status` | Show your linked account and last poll |
| `/stats` | Aggregated stats from your last 5 matches |
| `/toggle` | Enable/pause match notifications |
| `/add_pro GameName#TAG region` | Track a pro player |
| `/list_pros` | List all tracked pros |
| `/remove_pro <id>` | Remove a pro by ID |
| `/load_pros` | Bulk-load the 28-player official dataset |

### Region codes
`na1` · `euw1` · `eun1` · `kr` · `la1` · `la2` · `br1` · `jp1` · `tr1`

---

## Adding Pro Players

### Option 1 — Bot command
```
/add_pro Caps#EUW euw1
```

### Option 2 — Dataset (`pro_players.py`)
Add an entry to `PRO_PLAYERS`:
```python
{"game_name": "PlayerName", "tag_line": "TAG", "region": "euw1", "team": "TeamName", "role": "MID"},
```
Then run `/load_pros` in Telegram to sync the database.

---

## Architecture

```
main.py              — bot entry point, async lifecycle
handlers.py          — Telegram command handlers
poller.py            — background match polling loop
riot_api.py          — Riot API client (account/v1, match/v5)
riot_account.py      — account resolution helpers
stats.py             — pure aggregation engine (no I/O)
formatter.py         — pure message formatting (no I/O)
database.py          — SQLite persistence (aiosqlite)
pro_players.py       — curated pro player dataset
config.py            — env config

tests/functional/
  riot_functional.py      — Riot API functional tests
  stats_test.py           — aggregated stats functional test
  message_generation_test.py
  telegram_delivery_test.py
  telegram_reporting.py

functional_test_suite.py  — test runner (12 tests)
```

---

## Running Tests

```bash
cd lolnotifier
python functional_test_suite.py
```

Expected output:
```
Passed: 10  Failed: 0  Warn: 2
```
The 2 warnings are expected dev key 403s on `summoner/v4` and `league/v4`.

---

## Performance Score Formula

```
score = (winrate% × 0.40) + (avg_kda × 2.0) + (avg_cs_per_min × 0.5) + (avg_vision × 0.2)
```
Capped inputs: KDA max 10, CS/min max 10, vision max 50. Max theoretical score ≈ 100.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
