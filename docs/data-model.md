# Data Model

The bot uses two database backends depending on environment:

| Environment | Backend | Module |
|---|---|---|
| Local development | SQLite via `aiosqlite` | `database.py` |
| Azure (production) | CosmosDB Serverless | Terraform `cosmosdb/` module |

---

## SQLite Schema (local dev) — v2

Managed by `database.py`. Schema auto-migrated on `init_db()`.

### Table: `users`

| Column | Type | Description |
|---|---|---|
| `user_id` | INTEGER PK | Telegram user ID |
| `summoner_name` | TEXT | Full Riot ID: `GameName#TAG` |
| `game_name` | TEXT | GameName portion |
| `tag_line` | TEXT | TAG portion (without `#`) |
| `puuid` | TEXT | Riot PUUID (resolved via `account/v1`) |
| `region` | TEXT | Platform region code (e.g. `euw1`) |
| `notifications_enabled` | BOOLEAN | Default: 1 |
| `last_match_id` | TEXT | Last seen match ID — deduplication |
| `last_poll_time` | TIMESTAMP | When this user was last polled |
| `created_at` | TIMESTAMP | Row creation time |

### Table: `pro_players`

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | Internal pro ID |
| `summoner_name` | TEXT | Full Riot ID: `GameName#TAG` |
| `game_name` | TEXT | GameName portion |
| `tag_line` | TEXT | TAG portion |
| `puuid` | TEXT | Riot PUUID (resolved lazily on first poll) |
| `region` | TEXT | Platform region code |
| `team` | TEXT | Team name (e.g. `T1`, `G2`) |
| `role` | TEXT | `TOP`, `JGL`, `MID`, `BOT`, `SUP` |
| `last_match_id` | TEXT | Last seen match ID |
| `last_poll_time` | TIMESTAMP | When this pro was last polled |
| `created_at` | TIMESTAMP | Row creation time |

UNIQUE constraint: `(game_name, tag_line, region)`

---

## CosmosDB Schema (Azure production)

NoSQL / Core API, Serverless tier. Database: `lolnotifier`.

### Container: `users`

Partition key: `/user_id`

```json
{
  "id": "<telegram_user_id>",
  "user_id": 123456789,
  "game_name": "LaBísica",
  "tag_line": "EUW",
  "puuid": "...",
  "region": "euw1",
  "notifications_enabled": true,
  "last_match_id": "EUW1_7123456789",
  "last_poll_time": "2026-03-22T05:00:00Z"
}
```

### Container: `pro_players`

Partition key: `/region`

```json
{
  "id": "1",
  "game_name": "Caps",
  "tag_line": "EUW",
  "puuid": "...",
  "region": "euw1",
  "team": "G2",
  "role": "MID",
  "last_match_id": "EUW1_7123456789",
  "last_poll_time": "2026-03-22T05:00:00Z"
}
```

### Container: `match_history`

Partition key: `/puuid` — TTL: 90 days (`default_ttl = 7776000`)

```json
{
  "id": "EUW1_7123456789",
  "puuid": "...",
  "champion": "Orianna",
  "kills": 8,
  "deaths": 2,
  "assists": 12,
  "win": true,
  "cs": 245,
  "gold": 16200,
  "damage": 31400,
  "vision": 38,
  "queue_id": 420,
  "duration_seconds": 1934
}
```

Indexing: `raw_payload/*` excluded to reduce RU cost.

---

## Key Behaviors

- PUUID is resolved lazily: if null, `_resolve_puuid()` calls `account/v1` and stores the result
- `last_match_id` is compared against the latest match from `match/v5` to detect new games
- `get_all_users()` only returns rows where `notifications_enabled = true/1`
- Pro notifications are broadcast to **all** users with notifications enabled
- Match history TTL (90 days) auto-expires old records in CosmosDB to control storage costs
