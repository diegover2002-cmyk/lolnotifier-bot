# Test Coverage

## Overview

| Test suite | Tests | Type | API calls |
|---|---|---|---|
| `tests/test_formatter.py` | 30 | Unit | None |
| `tests/test_stats.py` | 20 | Unit | None |
| `tests/test_handlers.py` | 10 | Unit | Mocked |
| `tests/test_poller.py` | 10 | Unit | Mocked |
| `tests/test_riot_api.py` | 8 | Unit | Mocked |
| **Total unit** | **78** | | |
| `functional_test_suite.py` | 12 | Functional | Real (requires `.env`) |

---

## Running Tests

```bash
# Unit tests (no credentials needed)
python -m pytest tests/ -v

# Functional tests (requires .env with real keys)
python functional_test_suite.py
```

---

## Unit Test Breakdown

### `test_formatter.py` — 30 tests

Tests every public function in `formatter.py`. No mocks needed — all functions are pure.

| Test group | Count | What it covers |
|---|---|---|
| `_duration` | 4 | Zero, None, 90s, 3600s |
| `_kda_ratio` | 2 | Normal, zero deaths (Perfect) |
| `_queue_label` | 3 | Known ID, unknown ID, None |
| `format_match_summary` | 8 | Champion, KDA, win/loss, pro header, personal header, queue, duration |
| `format_match_summary_with_stats` | 4 | CS, gold, damage, vision |
| `format_aggregated_stats` | 5 | Winrate, champion, score, penta, pro header with role |
| `format_player_ranking` | 2 | Order, empty list |
| `format_status` | 2 | With tag, notifications paused |
| `format_pro_list` | 2 | Empty, with data |
| `format_help` | 1 | All commands present |

### `test_stats.py` — 20 tests

Tests every function in `stats.py`. No mocks needed — all functions are pure.

| Test group | Count | What it covers |
|---|---|---|
| `extract_participant` | 3 | Found, not found, empty match |
| `extract_match_stats` | 4 | Basic fields, zero deaths KDA, zero duration CS/min, not found |
| `aggregate_stats` | 7 | Empty, single win, single loss, wins+losses sum, most played champion, performance score range, penta kills |
| `rank_players` | 3 | Order, empty, single player |

### `test_handlers.py` — 10 tests

Tests Telegram command handlers with mocked `Update`, `Context`, DB, and Riot API.

| Test | What it covers |
|---|---|
| `test_set_summoner_missing_args` | No args → usage message |
| `test_set_summoner_bad_format_no_hash` | No `#` in Riot ID → format error |
| `test_set_summoner_account_not_found` | `_resolve_account` returns None → ❌ message |
| `test_set_summoner_success` | Happy path → ✅ message |
| `test_status_no_user` | No DB record → prompt to register |
| `test_status_with_user` | DB record exists → shows name and region |
| `test_toggle_no_user` | No DB record → prompt to register |
| `test_toggle_disables_notifications` | Toggles from True → False |
| `test_list_pros_empty` | Empty DB → prompt to add |
| `test_list_pros_with_data` | Two pros → both names in output |

### `test_poller.py` — 10 tests

Tests poller internals with mocked DB and Riot API.

| Test | What it covers |
|---|---|
| `test_last_poll_age_none_returns_infinity` | None → inf |
| `test_last_poll_age_invalid_returns_infinity` | Bad string → inf |
| `test_last_poll_age_recent_is_small` | Now → < 5s |
| `test_last_poll_age_old_is_large` | Year 2000 → > 1M seconds |
| `test_resolve_puuid_cached` | PUUID in record → returned directly |
| `test_resolve_puuid_resolves_via_api` | No PUUID → calls account/v1 |
| `test_resolve_puuid_api_returns_none` | API returns None → None |
| `test_process_player_no_new_match` | Same match ID → None, no send |
| `test_process_player_new_match_sends_notification` | New match → sends message |
| `test_process_player_no_history_returns_none` | Empty history → None |

### `test_riot_api.py` — 8 tests

Tests Riot API client with mocked `aiohttp` responses.

| Test | What it covers |
|---|---|
| `test_parse_match_for_puuid_found` | All fields extracted correctly |
| `test_parse_match_for_puuid_not_found` | Unknown PUUID → None |
| `test_parse_match_for_puuid_empty_match` | Empty dict → None |
| `test_parse_match_for_puuid_zero_deaths` | 0 deaths → KDA string correct |
| `test_get_match_history_ids_success` | 200 → list of IDs |
| `test_get_match_history_ids_403_returns_empty` | 403 → empty list |
| `test_get_match_info_success` | 200 → full payload |
| `test_get_match_info_404_returns_none` | 404 → None |

---

## Functional Test Breakdown

Requires real credentials in `.env`. Run with `python functional_test_suite.py`.

| Test | Expected | Notes |
|---|---|---|
| `test_account_resolution` | PASS | account/v1 returns PUUID |
| `test_match_history` | PASS | match/v5 returns IDs |
| `test_match_detail` | PASS | match/v5 returns full payload |
| `test_parse_match` | PASS | parse_match_for_puuid extracts fields |
| `test_summoner_lookup` | WARN | summoner/v4 → 403 on dev key |
| `test_ranked_entries` | WARN | league/v4 → 403 on dev key |
| `test_match_notification_format` | PASS | formatter produces valid string |
| `test_tracking_state` | PASS | last_match_id deduplication works |
| `test_telegram_delivery` | PASS | message sent to Telegram |
| `test_aggregated_stats` | PASS | 5 matches aggregated correctly |
| `test_message_generation` | PASS | all formatter functions produce output |
| `test_report_delivery` | PASS | final report sent to Telegram |

2 WARNs are expected and permanent on a Dev Key.

---

## What Is Not Tested

| Area | Reason |
|---|---|
| `database.py` | Requires a real SQLite file; integration tests not yet written |
| `poll_users()` / `poll_pros()` full loop | Requires real DB + bot; covered by functional suite |
| `logging_setup.py` | Configuration-only, no logic to test |
| `config.py` | Env var loading, no logic to test |
| `pro_players.py` helper functions | Simple list filters; low risk |

These are candidates for future test expansion.
