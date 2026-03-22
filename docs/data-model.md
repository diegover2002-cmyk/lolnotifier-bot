# Data Model

SQLite database managed by `database.py` using `aiosqlite` for async access.
Schema version: **v2** (auto-migrated on `init_db()`).

---

## Table: `users`

Stores Telegram users who have linked a LoL account.

| Column | Type | Description |
|---|---|---|
| `user_id` | INTEGER PK | Telegram user ID |
| `summoner_name` | TEXT | Full Riot ID string: `GameName#TAG` |
| `game_name` | TEXT | GameName portion of Riot ID |
| `tag_line` | TEXT | TAG portion of Riot ID (without `#`) |
| `puuid` | TEXT | Riot PUUID (resolved via `account/v1`) |
| `region` | TEXT | Platform region code (e.g. `euw1`, `kr`) |
| `notifications_enabled` | BOOLEAN | Whether to send match notifications (default: 1) |
| `last_match_id` | TEXT | Last seen match ID — used for deduplication |
| `last_poll_time` | TIMESTAMP | When this user was last polled |
| `created_at` | TIMESTAMP | Row creation time |

### Key behaviors

- `user_id` is the primary key — one row per Telegram user
- `ON CONFLICT(user_id) DO UPDATE` in `set_user_summoner()` — re-registering updates all fields
- `get_all_users()` only returns rows where `notifications_enabled = 1`
- `last_match_id` is compared against the latest match from `match/v5` to detect new games

---

## Table: `pro_players`

Stores tracked pro players. Shared across all users — all users receive notifications for all pros.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | Internal pro ID |
| `summoner_name` | TEXT | Full Riot ID string: `GameName#TAG` |
| `game_name` | TEXT | GameName portion |
| `tag_line` | TEXT | TAG portion |
| `puuid` | TEXT | Riot PUUID (resolved lazily on first poll) |
| `region` | TEXT | Platform region code |
| `team` | TEXT | Team name (e.g. `T1`, `G2`) |
| `role` | TEXT | Role code: `TOP`, `JGL`, `MID`, `BOT`, `SUP` |
| `last_match_id` | TEXT | Last seen match ID |
| `last_poll_time` | TIMESTAMP | When this pro was last polled |
| `created_at` | TIMESTAMP | Row creation time |

### Key behaviors

- `UNIQUE(game_name, tag_line, region)` — prevents duplicate entries
- `INSERT OR IGNORE` in `add_pro()` — safe to call multiple times
- PUUID is resolved lazily: if `puuid` is NULL, `_resolve_puuid()` calls `account/v1` and stores the result
- Notifications for pros are sent to **all** users with `notifications_enabled = 1`

---

## Schema Migration

`init_db()` runs `CREATE TABLE IF NOT EXISTS` for both tables, then applies `_MIGRATIONS` — a list of `ALTER TABLE ADD COLUMN` statements. Each migration is wrapped in `try/except` to silently skip columns that already exist.

This means the database is always forward-compatible: running `init_db()` on an old v1 database will add the missing columns without data loss.

---

## Row Helpers

`_user_row(tuple)` and `_pro_row(tuple)` convert raw SQLite tuples to named dicts. Column order in these helpers must match the `SELECT` column order in every query — they are tightly coupled.

---

## Database Path

Configured via `DB_PATH` in `.env` (default: `./lolnotifier.db`).
The file is excluded from git via `.gitignore`.
