"""
Unit tests for formatter.py.
All functions are pure (no I/O) so no mocks are needed.
"""
from formatter import (
    _duration,
    _kda_ratio,
    _queue_label,
    format_match_summary,
    format_match_summary_with_stats,
    format_aggregated_stats,
    format_player_ranking,
    format_status,
    format_pro_list,
    format_help,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def test_duration_zero():
    assert _duration(0) == "?"


def test_duration_none():
    assert _duration(None) == "?"


def test_duration_90_seconds():
    assert _duration(90) == "1m 30s"


def test_duration_3600_seconds():
    assert _duration(3600) == "60m 00s"


def test_kda_ratio_normal():
    assert _kda_ratio(5, 2, 8) == "6.50"


def test_kda_ratio_zero_deaths():
    assert _kda_ratio(10, 0, 5) == "Perfect"


def test_queue_label_known():
    assert _queue_label(420) == "Ranked Solo/Duo"
    assert _queue_label(450) == "ARAM"


def test_queue_label_unknown():
    label = _queue_label(9999)
    assert "9999" in label


def test_queue_label_none():
    assert _queue_label(None) == "Unknown Queue"


# ── format_match_summary ──────────────────────────────────────────────────────

PARSED = {
    "champion": "Graves",
    "kills": 10, "deaths": 8, "assists": 6,
    "kda": "10/8/6",
    "win": False,
    "queue_id": 420,
    "duration_seconds": 1800,
    "match_id": "EUW1_123",
}


def test_format_match_summary_contains_champion():
    msg = format_match_summary("Caps#EUW", PARSED)
    assert "Graves" in msg


def test_format_match_summary_contains_kda():
    msg = format_match_summary("Caps#EUW", PARSED)
    assert "10/8/6" in msg


def test_format_match_summary_loss():
    msg = format_match_summary("Caps#EUW", PARSED)
    assert "DERROTA" in msg or "❌" in msg


def test_format_match_summary_win():
    parsed_win = {**PARSED, "win": True}
    msg = format_match_summary("Caps#EUW", parsed_win)
    assert "VICTORIA" in msg or "✅" in msg


def test_format_match_summary_pro_header():
    msg = format_match_summary("Caps#EUW", PARSED, pro_team="G2")
    assert "G2" in msg
    assert "PRO" in msg


def test_format_match_summary_personal_header():
    msg = format_match_summary("LaBísica#EUW", PARSED)
    assert "Partida" in msg


def test_format_match_summary_contains_queue():
    msg = format_match_summary("Caps#EUW", PARSED)
    assert "Ranked Solo/Duo" in msg


def test_format_match_summary_contains_duration():
    msg = format_match_summary("Caps#EUW", PARSED)
    assert "30m" in msg


# ── format_match_summary_with_stats ──────────────────────────────────────────

FULL_PARTICIPANT = {
    "totalMinionsKilled": 200,
    "neutralMinionsKilled": 10,
    "goldEarned": 14500,
    "totalDamageDealtToChampions": 28000,
    "visionScore": 32,
}


def test_format_match_summary_with_stats_contains_cs():
    msg = format_match_summary_with_stats("Caps#EUW", PARSED, FULL_PARTICIPANT)
    assert "210" in msg  # 200 + 10


def test_format_match_summary_with_stats_contains_gold():
    msg = format_match_summary_with_stats("Caps#EUW", PARSED, FULL_PARTICIPANT)
    assert "14" in msg  # 14,500


def test_format_match_summary_with_stats_contains_damage():
    msg = format_match_summary_with_stats("Caps#EUW", PARSED, FULL_PARTICIPANT)
    assert "28" in msg


def test_format_match_summary_with_stats_contains_vision():
    msg = format_match_summary_with_stats("Caps#EUW", PARSED, FULL_PARTICIPANT)
    assert "32" in msg


# ── format_aggregated_stats ───────────────────────────────────────────────────

AGG = {
    "games": 5, "wins": 3, "losses": 2, "winrate": 60.0,
    "avg_kda_ratio": 3.5,
    "avg_kills": 6.0, "avg_deaths": 3.0, "avg_assists": 8.0,
    "avg_cs": 180.0, "avg_cs_per_min": 6.0,
    "avg_gold": 13000.0, "avg_damage": 22000.0, "avg_vision": 28.0,
    "most_played_champion": "Orianna",
    "performance_score": 55.0,
    "total_penta_kills": 1,
    "total_first_bloods": 2,
}


def test_format_aggregated_stats_contains_winrate():
    msg = format_aggregated_stats("Caps#EUW", AGG)
    assert "60.0%" in msg


def test_format_aggregated_stats_contains_champion():
    msg = format_aggregated_stats("Caps#EUW", AGG)
    assert "Orianna" in msg


def test_format_aggregated_stats_contains_score():
    msg = format_aggregated_stats("Caps#EUW", AGG)
    assert "55.0" in msg


def test_format_aggregated_stats_penta_shown():
    msg = format_aggregated_stats("Caps#EUW", AGG)
    assert "Penta" in msg or "1" in msg


def test_format_aggregated_stats_pro_header():
    msg = format_aggregated_stats("Caps#EUW", AGG, pro_team="G2", role="MID")
    assert "G2" in msg
    assert "⚡" in msg  # MID emoji


# ── format_player_ranking ─────────────────────────────────────────────────────

def test_format_player_ranking_order():
    ranking = [(1, "Faker", 80.0), (2, "Caps", 65.0), (3, "Bjergsen", 50.0)]
    msg = format_player_ranking(ranking)
    assert "🥇" in msg
    assert "Faker" in msg
    assert "Caps" in msg


def test_format_player_ranking_empty():
    msg = format_player_ranking([])
    assert "No hay" in msg


# ── format_status ─────────────────────────────────────────────────────────────

def test_format_status_with_tag():
    user = {
        "game_name": "LaBísica", "tag_line": "EUW", "region": "euw1",
        "notifications_enabled": True,
        "last_poll_time": "2026-03-22 01:00:00",
        "last_match_id": "EUW1_999",
    }
    msg = format_status(user)
    assert "LaBísica#EUW" in msg
    assert "euw1" in msg
    assert "activas" in msg


def test_format_status_notifications_paused():
    user = {
        "game_name": "Test", "tag_line": "NA1", "region": "na1",
        "notifications_enabled": False,
        "last_poll_time": None, "last_match_id": None,
    }
    msg = format_status(user)
    assert "pausadas" in msg


# ── format_pro_list ───────────────────────────────────────────────────────────

def test_format_pro_list_empty():
    msg = format_pro_list([])
    assert "add_pro" in msg or "No hay" in msg


def test_format_pro_list_shows_players():
    pros = [
        {"id": 1, "game_name": "Faker", "tag_line": "KR1", "region": "kr", "team": "T1", "role": "MID"},
        {"id": 2, "game_name": "Caps", "tag_line": "EUW", "region": "euw1", "team": "G2", "role": "MID"},
    ]
    msg = format_pro_list(pros)
    assert "Faker" in msg
    assert "Caps" in msg
    assert "T1" in msg


# ── format_help ───────────────────────────────────────────────────────────────

def test_format_help_contains_commands():
    msg = format_help()
    for cmd in ["/set_summoner", "/status", "/stats", "/toggle", "/add_pro", "/list_pros", "/load_pros"]:
        assert cmd in msg
