"""
Unit tests for stats.py.
All functions are pure (no I/O) so no mocks are needed.
"""
import pytest
from stats import extract_match_stats, extract_participant, aggregate_stats, rank_players


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_match(puuid: str, kills: int, deaths: int, assists: int, win: bool,
                cs: int = 150, gold: int = 12000, damage: int = 20000,
                vision: int = 25, duration: int = 1800) -> dict:
    return {
        "metadata": {"matchId": f"EUW1_{puuid[:4]}"},
        "info": {
            "queueId": 420,
            "gameMode": "CLASSIC",
            "gameDuration": duration,
            "participants": [{
                "puuid": puuid,
                "championName": "Graves",
                "kills": kills, "deaths": deaths, "assists": assists,
                "win": win,
                "totalMinionsKilled": cs, "neutralMinionsKilled": 0,
                "goldEarned": gold,
                "totalDamageDealtToChampions": damage,
                "visionScore": vision,
                "firstBloodKill": False,
                "turretKills": 0,
                "doubleKills": 0, "tripleKills": 0,
                "quadraKills": 0, "pentaKills": 0,
            }],
        },
    }


PUUID = "player-puuid-001"


# ── extract_participant ───────────────────────────────────────────────────────

def test_extract_participant_found():
    match = _make_match(PUUID, 5, 3, 7, True)
    p = extract_participant(match, PUUID)
    assert p is not None
    assert p["puuid"] == PUUID


def test_extract_participant_not_found():
    match = _make_match(PUUID, 5, 3, 7, True)
    p = extract_participant(match, "wrong-puuid")
    assert p is None


def test_extract_participant_empty_match():
    assert extract_participant({}, PUUID) is None


# ── extract_match_stats ───────────────────────────────────────────────────────

def test_extract_match_stats_basic():
    match = _make_match(PUUID, 10, 2, 5, True, cs=200, duration=1800)
    stats = extract_match_stats(match, PUUID)
    assert stats is not None
    assert stats["kills"] == 10
    assert stats["deaths"] == 2
    assert stats["assists"] == 5
    assert stats["win"] is True
    assert stats["cs"] == 200
    assert stats["cs_per_min"] == round(200 / 30, 1)  # 1800s = 30min
    assert stats["kda_ratio"] == round((10 + 5) / 2, 2)


def test_extract_match_stats_zero_deaths_kda():
    match = _make_match(PUUID, 8, 0, 4, True)
    stats = extract_match_stats(match, PUUID)
    assert stats is not None
    assert stats["kda_ratio"] == float(8 + 4)  # perfect KDA


def test_extract_match_stats_zero_duration_cs_per_min():
    match = _make_match(PUUID, 3, 3, 3, False, duration=0)
    stats = extract_match_stats(match, PUUID)
    assert stats is not None
    assert stats["cs_per_min"] == 0.0


def test_extract_match_stats_not_found():
    match = _make_match(PUUID, 5, 5, 5, True)
    stats = extract_match_stats(match, "other-puuid")
    assert stats is None


# ── aggregate_stats ───────────────────────────────────────────────────────────

def test_aggregate_stats_empty():
    result = aggregate_stats([])
    assert result["games"] == 0
    assert result["winrate"] == 0.0
    assert result["performance_score"] == 0.0
    assert result["most_played_champion"] is None


def test_aggregate_stats_single_win():
    match = _make_match(PUUID, 5, 2, 8, True)
    stats = [extract_match_stats(match, PUUID)]
    result = aggregate_stats(stats)
    assert result["games"] == 1
    assert result["wins"] == 1
    assert result["losses"] == 0
    assert result["winrate"] == 100.0


def test_aggregate_stats_single_loss():
    match = _make_match(PUUID, 1, 8, 2, False)
    stats = [extract_match_stats(match, PUUID)]
    result = aggregate_stats(stats)
    assert result["wins"] == 0
    assert result["losses"] == 1
    assert result["winrate"] == 0.0


def test_aggregate_stats_wins_losses_sum():
    matches = [
        extract_match_stats(_make_match(PUUID, 5, 2, 3, True), PUUID),
        extract_match_stats(_make_match(PUUID, 2, 7, 1, False), PUUID),
        extract_match_stats(_make_match(PUUID, 8, 1, 6, True), PUUID),
    ]
    result = aggregate_stats(matches)
    assert result["games"] == 3
    assert result["wins"] + result["losses"] == 3
    assert result["winrate"] == round(2 / 3 * 100, 1)


def test_aggregate_stats_most_played_champion():
    p1 = {"champion": "Graves", "win": True, "kills": 5, "deaths": 2, "assists": 3,
          "kda_ratio": 4.0, "cs": 150, "cs_per_min": 5.0, "gold": 12000,
          "damage": 20000, "vision": 25, "first_blood": False, "multikills": {"penta": 0}}
    p2 = {"champion": "Graves", "win": False, "kills": 2, "deaths": 5, "assists": 1,
          "kda_ratio": 0.6, "cs": 100, "cs_per_min": 3.3, "gold": 8000,
          "damage": 10000, "vision": 15, "first_blood": False, "multikills": {"penta": 0}}
    p3 = {"champion": "Jinx", "win": True, "kills": 8, "deaths": 1, "assists": 5,
          "kda_ratio": 13.0, "cs": 200, "cs_per_min": 6.7, "gold": 15000,
          "damage": 30000, "vision": 30, "first_blood": True, "multikills": {"penta": 0}}
    result = aggregate_stats([p1, p2, p3])
    assert result["most_played_champion"] == "Graves"


def test_aggregate_stats_performance_score_range():
    matches = [extract_match_stats(_make_match(PUUID, 5, 3, 7, True), PUUID)]
    result = aggregate_stats(matches)
    assert 0 <= result["performance_score"] <= 100


def test_aggregate_stats_penta_kills():
    p = {"champion": "Jinx", "win": True, "kills": 20, "deaths": 0, "assists": 0,
         "kda_ratio": 20.0, "cs": 300, "cs_per_min": 10.0, "gold": 20000,
         "damage": 50000, "vision": 40, "first_blood": True,
         "multikills": {"penta": 2}}
    result = aggregate_stats([p])
    assert result["total_penta_kills"] == 2


# ── rank_players ──────────────────────────────────────────────────────────────

def test_rank_players_order():
    players = [
        ("PlayerA", {"performance_score": 45.0}),
        ("PlayerB", {"performance_score": 72.0}),
        ("PlayerC", {"performance_score": 60.0}),
    ]
    ranking = rank_players(players)
    assert ranking[0] == (1, "PlayerB", 72.0)
    assert ranking[1] == (2, "PlayerC", 60.0)
    assert ranking[2] == (3, "PlayerA", 45.0)


def test_rank_players_empty():
    assert rank_players([]) == []


def test_rank_players_single():
    ranking = rank_players([("Solo", {"performance_score": 55.5})])
    assert ranking == [(1, "Solo", 55.5)]
