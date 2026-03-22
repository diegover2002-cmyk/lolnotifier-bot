# CHANGELOG

## [4.0.0] - 2026-03-22

### Release
- Stable release consolidating all infrastructure, CI/CD, and testing work
- Git tag: `v4.0.0`
- **78 unit tests passing** — 0 failures, 0 warnings
- **Coverage: 61%** on testable modules (100% on `stats.py`, `formatter.py`, `config.py`)
- Functional test suite: 10 PASS / 0 FAIL / 2 WARN (expected Dev Key 403s)

### CI/CD
- Added `.github/workflows/ci.yml` — lint (ruff), unit tests + coverage gate (55% floor), security scans (bandit + checkov)
- Added `.github/workflows/release.yml` — Docker build/push to GHCR, deploy to dev then prod with manual approval gate
- Both workflows are non-blocking — branch protection rules not enforced until explicitly configured

### Testing & Coverage
- Added `.coveragerc` — excludes `main.py`, `logging_setup.py`, `functional_test_suite.py`, `scripts/`
- Added `pytest-cov==6.1.0` to `requirements.txt`
- Added `docs/coverage-report.md` — per-module breakdown with gap analysis and improvement roadmap
- Coverage by module: `stats.py` 100%, `formatter.py` 99%, `config.py` 100%, `poller.py` 62%, `riot_api.py` 61%, `handlers.py` 46%, `database.py` 27%

### Infrastructure
- Terraform modules complete: `keyvault/`, `cosmosdb/`, `function_app/`, `scheduler/`, `storage/`, `monitoring/`, `container_app/`
- `terraform/scripts/bootstrap-backend.sh` — one-time remote state setup
- `terraform/terraform.tfvars.example` — safe example with no secrets
- `docs/terraform-deployment-guide.md` — 10-step deploy guide with troubleshooting table

### Dev Key compliance
- All endpoints used: `account/v1` ✔, `match/v5` ✔
- Blocked endpoints return `None` gracefully — no retries on 401/403
- `poll_interval_seconds >= 60` enforced by Terraform variable validation
- Dev Key rotation: `az keyvault secret set` — no Terraform re-apply needed

---

## [3.0.0] - 2026-03-22

### Release
- First stable production-ready release
- Git tag: `v3.0.0`
- All 78 unit tests passing (0 failures)
- Functional test suite: 10 PASS / 0 FAIL / 2 WARN (expected Dev Key 403s)

### Documentation
- Full README rewrite: badges, setup guide, command table, example Telegram output, architecture map
- Added `CONTRIBUTING.md`: pro player workflow, test guidelines, code style, PR checklist
- Added `SECURITY.md`: secrets policy, logging policy, Dev Key safe usage, incident response
- Added `docs/` wiki folder: architecture, data model, dev-key-constraints, message-templates, test-coverage, future-improvements
- Added `pyproject.toml` with project metadata and tool configuration

### Infrastructure
- Dockerfile upgraded to Python 3.11-slim, non-root user, selective COPY
- docker-compose.yml updated to named volumes (no bind-mount DB)
- `.gitignore` extended with Terraform state files and `.tfvars`
- Added `terraform/` module structure for Azure deployment (conceptual)
- Added `docs/azure-deployment.md`: full Terraform + Azure architecture guide
- Added `docs/cicd-workflow.md`: conceptual CI/CD pipeline definition
- Added `docs/release-plan.md`: step-by-step release and migration checklist

### Security
- Dockerfile runs as non-root `botuser`
- `riot_account.py` replaced `print()` with `logging` — no PII in stdout
- `config.py` module docstring added
- All secrets excluded from repo (verified via `.gitignore` audit)

### Dev Key compliance
- All polling uses only `account/v1` and `match/v5`
- 403-guarded endpoints (`summoner/v4`, `league/v4`, `spectator/v5`) return `None` gracefully
- No retries on 401/403 — prevents rate limit waste on expired keys

---

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
