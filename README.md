# LoLNotifierBot

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Tests](https://img.shields.io/badge/tests-78%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Key](https://img.shields.io/badge/Riot%20Dev%20Key-compatible-orange)

Telegram bot that tracks League of Legends players — both personal accounts and pro players — using the Riot Games API. Sends rich match notifications with KDA, CS, gold, damage, and vision stats. Computes aggregated performance scores across multiple matches.

---

## Features

| Feature | Status | Endpoint |
|---|---|---|
| Riot ID → PUUID resolution | ✅ | `account/v1` |
| Match history retrieval | ✅ | `match/v5/by-puuid` |
| Match detail parsing (KDA, CS, gold, damage, vision) | ✅ | `match/v5/{id}` |
| New match detection & Telegram notification | ✅ | `match/v5` polling |
| Aggregated stats (winrate, avg KDA, CS/min, perf score) | ✅ | `match/v5` computed locally |
| Player ranking by performance score | ✅ | Computed locally |
| Rich Telegram messages with emojis | ✅ | Telegram Bot API |
| Pro player dataset (28 players, 4 regions) | ✅ | Static |
| Summoner level | ⚠️ Dev key 403 | `summoner/v4` |
| Ranked tier / LP | ⚠️ Dev key 403 | `league/v4` |
| Live game detection | ⚠️ Dev key 403 | `spectator/v5` |
| Champion mastery | ⚠️ Dev key 403 | `champion-mastery/v4` |

All ⚠️ features are implemented and will activate automatically on production key upgrade — no code changes needed.

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/diegover2002-cmyk/lolnotifier-bot.git
cd lolnotifier-bot
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install python-telegram-bot==20.7
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
TELEGRAM_TOKEN=<your_botfather_token>
RIOT_API_KEY=<your_riot_dev_key>
TELEGRAM_CHAT_ID=<your_telegram_user_id>

# Optional — used by functional tests only
RIOT_GAME_NAME=YourGameName
RIOT_TAG_LINE=EUW
RIOT_REGION=euw1

# Tuning (defaults shown)
POLL_INTERVAL=300
RATE_LIMIT_DELAY=0.06
```

> **Never commit `.env`** — it is excluded by `.gitignore`.

### 4. Run the bot

```bash
python main.py
```

---

## Bot Commands

| Command | Description | Example |
|---|---|---|
| `/set_summoner GameName#TAG region` | Link your LoL account | `/set_summoner LaBísica#EUW euw1` |
| `/status` | Show linked account and last poll time | `/status` |
| `/stats` | Aggregated stats from your last 5 matches | `/stats` |
| `/toggle` | Enable or pause match notifications | `/toggle` |
| `/add_pro GameName#TAG region` | Track a pro player | `/add_pro Caps#EUW euw1` |
| `/list_pros` | List all tracked pros with IDs | `/list_pros` |
| `/remove_pro <id>` | Remove a pro by ID | `/remove_pro 3` |
| `/load_pros` | Bulk-load the 28-player official dataset | `/load_pros` |

### Supported regions

`na1` · `euw1` · `eun1` · `kr` · `la1` · `la2` · `br1` · `jp1` · `tr1`

---

## Example Telegram Output

**Match notification:**
```
🌟 PRO · G2
✅ VICTORIA — Orianna

👤 Caps#EUW
⚔️  KDA: 8/2/12  (ratio 10.00)
🎯 Modo: Ranked Solo/Duo
⏱️  Duración: 32m 14s

🌾 CS: 245   💰 Oro: 16,200
💥 Daño: 31,400   👁️  Visión: 38
🔗 ID: EUW1_7123456789
```

**Stats summary (`/stats`):**
```
📊 Estadísticas
👤 LaBísica#EUW

🎮 Partidas: 5  (3V / 2D)
🔥 Winrate: 60.0%
⚔️  KDA medio: 6.0/3.0/8.0  (ratio 4.67)
🏆 Campeón más jugado: Graves

🌾 CS/min: 6.2
💰 Oro medio: 13,400
💥 Daño medio: 22,800
👁️  Visión media: 28.0

⭐ Performance score: 58.4/100
```

---

## Running Tests

### Unit tests (78 tests, no API calls)

```bash
cd lolnotifier
python -m pytest tests/ -v
```

Expected: `78 passed in ~0.4s`

### Functional tests (requires real API keys in `.env`)

```bash
python functional_test_suite.py
```

Expected: `Passed: 10  Failed: 0  Warn: 2`

The 2 warnings are expected Dev Key 403s on `summoner/v4` and `league/v4`.

---

## Dev Key Rate Limits

- 20 requests / second
- 100 requests / 2 minutes
- Bot polls each player at most once per 60 seconds (`_MIN_POLL_GAP`)
- `RATE_LIMIT_DELAY` controls per-request delay (default: `0.06s` ≈ 16 req/s)
- Global semaphore (`asyncio.Semaphore(20)`) prevents burst overruns

---

## Performance Score Formula

```
score = (winrate% × 0.40) + (avg_kda × 2.0) + (avg_cs_per_min × 0.5) + (avg_vision × 0.2)
```

Inputs are capped: KDA max 10, CS/min max 10, vision max 50.
Maximum theoretical score ≈ 100.

---

## Pro Player Dataset

28 players across 4 regions, loaded via `/load_pros`:

| Region | Teams | Players |
|---|---|---|
| KR (LCK) | T1, Gen.G, DRX, KDF | 12 |
| EUW (LEC) | G2, FNC, KCorp, Rogue | 9 |
| NA1 (LCS) | TL, C9 | 7 |
| LA2 (LLA) | Isurus | 2 |

To add a player to the dataset, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Architecture

```
main.py              — bot entry point, async lifecycle
handlers.py          — Telegram command handlers
poller.py            — background match polling loop (users + pros)
riot_api.py          — Riot API client (account/v1, match/v5)
riot_account.py      — account/v1 resolution helpers
stats.py             — pure aggregation engine (no I/O)
formatter.py         — pure message formatting (no I/O)
database.py          — SQLite persistence via aiosqlite (schema v2)
pro_players.py       — curated pro player dataset (28 players)
config.py            — environment variable loading
logging_setup.py     — stdlib logging, rotating file handler

tests/               — 78 unit tests (pytest)
tests/functional/    — functional tests (real API, requires .env)
scripts/             — legacy/utility scripts (not part of main bot)
docs/                — architecture, data model, and wiki pages
```

See [docs/architecture.md](docs/architecture.md) for the full data flow diagram.

---

## Documentation

| Document | Description |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Module map, async lifecycle, data flow |
| [docs/data-model.md](docs/data-model.md) | SQLite schema v2, field descriptions |
| [docs/dev-key-constraints.md](docs/dev-key-constraints.md) | Rate limits, 403 endpoints, workarounds |
| [docs/message-templates.md](docs/message-templates.md) | All Telegram message formats |
| [docs/test-coverage.md](docs/test-coverage.md) | Test strategy and coverage breakdown |
| [docs/future-improvements.md](docs/future-improvements.md) | Roadmap and conceptual CI/CD plan |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [SECURITY.md](SECURITY.md) | Secrets handling and safe logging policy |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## License

MIT
