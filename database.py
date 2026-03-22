"""
Database layer — aiosqlite, async, schema v2.
Schema v2 adds: game_name, tag_line, puuid to users and pro_players.
Pro players also get team and role columns.
Migration runs automatically on init_db().
"""

from __future__ import annotations

import aiosqlite
from typing import Any, Optional


# ── Schema ────────────────────────────────────────────────────────────────────

_DDL_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY,
    summoner_name TEXT NOT NULL,
    game_name     TEXT,
    tag_line      TEXT,
    puuid         TEXT,
    region        TEXT NOT NULL,
    notifications_enabled BOOLEAN DEFAULT 1,
    last_match_id TEXT DEFAULT NULL,
    last_poll_time TIMESTAMP DEFAULT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

_DDL_PROS = """
CREATE TABLE IF NOT EXISTS pro_players (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    summoner_name TEXT NOT NULL,
    game_name     TEXT,
    tag_line      TEXT,
    puuid         TEXT,
    region        TEXT NOT NULL,
    team          TEXT DEFAULT '',
    role          TEXT DEFAULT '',
    last_match_id TEXT DEFAULT NULL,
    last_poll_time TIMESTAMP DEFAULT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_name, tag_line, region)
)
"""

_MIGRATIONS = [
    "ALTER TABLE users ADD COLUMN game_name TEXT",
    "ALTER TABLE users ADD COLUMN tag_line TEXT",
    "ALTER TABLE users ADD COLUMN puuid TEXT",
    "ALTER TABLE pro_players ADD COLUMN game_name TEXT",
    "ALTER TABLE pro_players ADD COLUMN tag_line TEXT",
    "ALTER TABLE pro_players ADD COLUMN puuid TEXT",
    "ALTER TABLE pro_players ADD COLUMN team TEXT DEFAULT ''",
    "ALTER TABLE pro_players ADD COLUMN role TEXT DEFAULT ''",
]


async def init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_DDL_USERS)
        await db.execute(_DDL_PROS)
        # Run migrations idempotently (ignore "duplicate column" errors)
        for sql in _MIGRATIONS:
            try:
                await db.execute(sql)
            except Exception:
                pass
        await db.commit()


# ── Row helpers ───────────────────────────────────────────────────────────────


def _user_row(row: tuple) -> dict[str, Any]:
    keys = [
        "user_id",
        "summoner_name",
        "game_name",
        "tag_line",
        "puuid",
        "region",
        "notifications_enabled",
        "last_match_id",
        "last_poll_time",
        "created_at",
    ]
    return dict(zip(keys, row))


def _pro_row(row: tuple) -> dict[str, Any]:
    keys = [
        "id",
        "summoner_name",
        "game_name",
        "tag_line",
        "puuid",
        "region",
        "team",
        "role",
        "last_match_id",
        "last_poll_time",
        "created_at",
    ]
    return dict(zip(keys, row))


# ── Users ─────────────────────────────────────────────────────────────────────


async def get_user(db_path: str, user_id: int) -> Optional[dict[str, Any]]:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT user_id, summoner_name, game_name, tag_line, puuid, region, "
            "notifications_enabled, last_match_id, last_poll_time, created_at "
            "FROM users WHERE user_id = ?",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return _user_row(row) if row else None


async def set_user_summoner(
    db_path: str,
    user_id: int,
    summoner_name: str,
    region: str,
    *,
    game_name: str | None = None,
    tag_line: str | None = None,
    puuid: str | None = None,
) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """INSERT INTO users (user_id, summoner_name, game_name, tag_line, puuid, region)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                 summoner_name = excluded.summoner_name,
                 game_name     = excluded.game_name,
                 tag_line      = excluded.tag_line,
                 puuid         = excluded.puuid,
                 region        = excluded.region""",
            (user_id, summoner_name, game_name, tag_line, puuid, region),
        )
        await db.commit()


async def update_user_puuid(db_path: str, user_id: int, puuid: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE users SET puuid = ? WHERE user_id = ?", (puuid, user_id))
        await db.commit()


async def update_last_match_id(db_path: str, user_id: int, match_id: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE users SET last_match_id = ? WHERE user_id = ?", (match_id, user_id))
        await db.commit()


async def toggle_notifications(db_path: str, user_id: int, enabled: bool) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE users SET notifications_enabled = ? WHERE user_id = ?", (enabled, user_id))
        await db.commit()


async def get_all_users(db_path: str) -> list[dict[str, Any]]:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT user_id, summoner_name, game_name, tag_line, puuid, region, "
            "notifications_enabled, last_match_id, last_poll_time, created_at "
            "FROM users WHERE notifications_enabled = 1"
        ) as cur:
            return [_user_row(r) for r in await cur.fetchall()]


async def get_all_user_ids(db_path: str) -> list[int]:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT DISTINCT user_id FROM users WHERE notifications_enabled = 1") as cur:
            return [r[0] for r in await cur.fetchall()]


async def update_user_last_poll_time(db_path: str, user_id: int, poll_time: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE users SET last_poll_time = ? WHERE user_id = ?", (poll_time, user_id))
        await db.commit()


# ── Pro players ───────────────────────────────────────────────────────────────


async def get_all_pros(db_path: str) -> list[dict[str, Any]]:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT id, summoner_name, game_name, tag_line, puuid, region, "
            "team, role, last_match_id, last_poll_time, created_at "
            "FROM pro_players ORDER BY id"
        ) as cur:
            return [_pro_row(r) for r in await cur.fetchall()]


async def get_pro_by_id(db_path: str, pro_id: int) -> Optional[dict[str, Any]]:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT id, summoner_name, game_name, tag_line, puuid, region, "
            "team, role, last_match_id, last_poll_time, created_at "
            "FROM pro_players WHERE id = ?",
            (pro_id,),
        ) as cur:
            row = await cur.fetchone()
            return _pro_row(row) if row else None


async def add_pro(
    db_path: str,
    summoner_name: str,
    region: str,
    *,
    game_name: str | None = None,
    tag_line: str | None = None,
    puuid: str | None = None,
    team: str = "",
    role: str = "",
) -> int:
    """Returns the row id, or 0 if already exists."""
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute(
            """INSERT OR IGNORE INTO pro_players
               (summoner_name, game_name, tag_line, puuid, region, team, role)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (summoner_name, game_name, tag_line, puuid, region, team, role),
        )
        await db.commit()
        if cur.lastrowid:
            return cur.lastrowid
        async with db.execute(
            "SELECT id FROM pro_players WHERE summoner_name = ? AND region = ?",
            (summoner_name, region),
        ) as cur2:
            row = await cur2.fetchone()
            return row[0] if row else 0


async def remove_pro(db_path: str, pro_id: int) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DELETE FROM pro_players WHERE id = ?", (pro_id,))
        await db.commit()


async def update_pro_puuid(db_path: str, pro_id: int, puuid: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE pro_players SET puuid = ? WHERE id = ?", (puuid, pro_id))
        await db.commit()


async def update_pro_last_match_id(db_path: str, pro_id: int, match_id: Optional[str]) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE pro_players SET last_match_id = ? WHERE id = ?", (match_id, pro_id))
        await db.commit()


async def update_pro_last_poll_time(db_path: str, pro_id: int, poll_time: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE pro_players SET last_poll_time = ? WHERE id = ?", (poll_time, pro_id))
        await db.commit()
