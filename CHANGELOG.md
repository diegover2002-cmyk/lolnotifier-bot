# CHANGELOG

## [2.1.0] - 2026-03-22

### New features
- New `stats.py` — pure aggregation engine (no I/O, no API calls)
  - `extract_match_stats()` — pulls KDA, CS, CS/min, gold, damage, vision, first blood, multikills from match/v5
  - `aggregate_stats()` — winrate, avg KDA ratio, avg CS/min, avg gold, avg damage, avg vision, most played champion, performance score
  - `rank_players()` — sorts players by performance score descending
- New `/stats` command — aggregated stats from the user's last 5 matches (dev key compatible)
- New `tests/functional/stats_test.py` — `test_aggregated_stats()` functional test
- `formatter.py` additions: `format_aggregated_stats()`, `format_player_ranking()`
- README rewritten with full feature table, setup guide, architecture map, performance score formula

### Architecture fix
- `get_match_history_ids()` and `parse_match_for_puuid()` moved from `tests/functional/riot_functional.py` into `riot_api.py`
- Production code (`poller.py`) no longer imports from the test directory
- Test file imports both functions from `riot_api`

### Test results
- 10 PASS / 0 FAIL / 2 WARN (expected dev key 403s on `summoner/v4` and `league/v4`)

---

## [2.0.0] - 2026-03-22

### Architecture
- New `formatter.py` — pure message formatting layer, rich emoji templates
- New `pro_players.py` — curated dataset of 28 real pro players (LCK/LEC/LCS/LLA)
- Rewrote `database.py` — schema v2 with `game_name`, `tag_line`, `puuid`, `team`, `role` columns; auto-migration on startup
- Rewrote `poller.py` — PUUID-based match/v5 history polling; no spectator/summoner dependency
- Rewrote `handlers.py` — Riot ID format (`GameName#TAG`), account verification on registration
- Rewrote `main.py` — proper async lifecycle, removed nest_asyncio

### New commands
- `/set_summoner GameName#TAG region` — replaces `/set_lol_summoner` (old kept as alias)
- `/toggle` — replaces `/stop_notifications` (old kept as alias)
- `/load_pros` — bulk-insert curated pro player dataset

### Bug fixes
- URL-encode accented characters in Riot ID API requests (`LaBísica` → `LaB%C3%ADsica`)
- `get_summoner_by_puuid` no longer retries on 401/403 (dev key limits)
- `get_match_info` now uses correct regional cluster instead of hardcoded `americas`
- Participant matching uses PUUID instead of deprecated `summonerName` field
- Fixed double response body read in `telegram_delivery_test.py`

### API research findings
- Dev key: `account/v1`, `match/v5` fully available ✅
- Dev key: `summoner/v4`, `league/v4`, `spectator/v5`, `champion-mastery/v4` blocked (403) ⚠️
- Ranked and live game features will activate automatically on production key upgrade

### Test results
- 9 PASS / 0 FAIL / 2 WARN

---

## [1.1.0] - 2026-03-22

### Functional test suite
- Added `tests/functional/` with full test pipeline (11 tests)
- `riot_functional.py` — account resolution, match history, match parsing, tracking logic, ranked data, edge cases
- `message_generation_test.py` — match summary message validation
- `telegram_delivery_test.py` — live Telegram delivery test
- `telegram_reporting.py` — `build_result()`, `format_test_report()`, `send_telegram_report()`
- `functional_test_suite.py` — orchestrator with context propagation between tests

### Bug fixes
- Fixed `UnicodeEncodeError` on Windows console (emoji output) — force UTF-8 stdout
- Fixed `aiohttp` not installed in venv — installed all dependencies
- Corrected Riot test account name: `LaBísica#EUW` (was `LaBífica`)

---

## [1.0.0] - 2026-03-22

- Initial release of LoLNotifierBot
- Personal match notifications via Telegram
- Pro player tracking with broadcast notifications
- Commands: `/set_lol_summoner`, `/status`, `/stop_notifications`, `/add_pro`, `/list_pros`, `/remove_pro`
- SQLite persistence via aiosqlite
- Docker and docker-compose deployment support
