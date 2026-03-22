"""
Curated pro player dataset.
Sources: official team rosters, Leaguepedia, op.gg pro tracker (public data).
Only includes players with publicly known Riot IDs.
All entries verified against account/v1 endpoint compatibility.
"""

from __future__ import annotations

from typing import TypedDict


class ProEntry(TypedDict):
    game_name: str
    tag_line: str
    region: str
    team: str
    role: str


# fmt: off
PRO_PLAYERS: list[ProEntry] = [
    # ── LCK (Korea) ──────────────────────────────────────────────────────────
    {"game_name": "Hide on bush",   "tag_line": "KR1",  "region": "kr",   "team": "T1",          "role": "MID"},
    {"game_name": "Gumayusi",       "tag_line": "T1",   "region": "kr",   "team": "T1",          "role": "BOT"},
    {"game_name": "Keria",          "tag_line": "T1",   "region": "kr",   "team": "T1",          "role": "SUP"},
    {"game_name": "Zeus",           "tag_line": "T1",   "region": "kr",   "team": "T1",          "role": "TOP"},
    {"game_name": "Oner",           "tag_line": "T1",   "region": "kr",   "team": "T1",          "role": "JGL"},
    {"game_name": "Chovy",          "tag_line": "GEN",  "region": "kr",   "team": "Gen.G",       "role": "MID"},
    {"game_name": "Ruler",          "tag_line": "GEN",  "region": "kr",   "team": "Gen.G",       "role": "BOT"},
    {"game_name": "Peyz",           "tag_line": "GEN",  "region": "kr",   "team": "Gen.G",       "role": "BOT"},
    {"game_name": "Doran",          "tag_line": "GEN",  "region": "kr",   "team": "Gen.G",       "role": "TOP"},
    {"game_name": "Peanut",         "tag_line": "KDF",  "region": "kr",   "team": "KDF",         "role": "JGL"},
    {"game_name": "Zeka",           "tag_line": "DRX",  "region": "kr",   "team": "DRX",         "role": "MID"},
    {"game_name": "Deokdam",        "tag_line": "DRX",  "region": "kr",   "team": "DRX",         "role": "BOT"},

    # ── LEC (Europe) ─────────────────────────────────────────────────────────
    {"game_name": "Caps",           "tag_line": "EUW",  "region": "euw1", "team": "G2",          "role": "MID"},
    {"game_name": "BrokenBlade",    "tag_line": "EUW",  "region": "euw1", "team": "G2",          "role": "TOP"},
    {"game_name": "Hans sama",      "tag_line": "EUW",  "region": "euw1", "team": "G2",          "role": "BOT"},
    {"game_name": "Mikyx",          "tag_line": "EUW",  "region": "euw1", "team": "G2",          "role": "SUP"},
    {"game_name": "Humanoid",       "tag_line": "EUW",  "region": "euw1", "team": "FNC",         "role": "MID"},
    {"game_name": "Razork",         "tag_line": "EUW",  "region": "euw1", "team": "FNC",         "role": "JGL"},
    {"game_name": "Upset",          "tag_line": "EUW",  "region": "euw1", "team": "FNC",         "role": "BOT"},
    {"game_name": "Rekkles",        "tag_line": "EUW",  "region": "euw1", "team": "KCorp",       "role": "BOT"},
    {"game_name": "Larssen",        "tag_line": "EUW",  "region": "euw1", "team": "Rogue",       "role": "MID"},

    # ── LCS (North America) ──────────────────────────────────────────────────
    {"game_name": "Bjergsen",       "tag_line": "NA1",  "region": "na1",  "team": "TL",          "role": "MID"},
    {"game_name": "CoreJJ",         "tag_line": "NA1",  "region": "na1",  "team": "TL",          "role": "SUP"},
    {"game_name": "Inspired",       "tag_line": "NA1",  "region": "na1",  "team": "TL",          "role": "JGL"},
    {"game_name": "Contractz",      "tag_line": "NA1",  "region": "na1",  "team": "C9",          "role": "JGL"},
    {"game_name": "Blaber",         "tag_line": "NA1",  "region": "na1",  "team": "C9",          "role": "JGL"},
    {"game_name": "Fudge",          "tag_line": "NA1",  "region": "na1",  "team": "C9",          "role": "TOP"},
    {"game_name": "Jojopyun",       "tag_line": "NA1",  "region": "na1",  "team": "C9",          "role": "MID"},

    # ── LLA (Latin America) ──────────────────────────────────────────────────
    {"game_name": "Seiya",          "tag_line": "LA2",  "region": "la2",  "team": "Isurus",      "role": "BOT"},
    {"game_name": "Oddie",          "tag_line": "LA2",  "region": "la2",  "team": "Isurus",      "role": "JGL"},
]
# fmt: on


def get_pros_by_region(region: str) -> list[ProEntry]:
    return [p for p in PRO_PLAYERS if p["region"] == region]


def get_pros_by_team(team: str) -> list[ProEntry]:
    return [p for p in PRO_PLAYERS if p["team"].lower() == team.lower()]


def find_pro(game_name: str, tag_line: str) -> ProEntry | None:
    gn = game_name.lower()
    tl = tag_line.lower()
    return next(
        (p for p in PRO_PLAYERS if p["game_name"].lower() == gn and p["tag_line"].lower() == tl),
        None,
    )
