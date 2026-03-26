"""Statistical analysis for NBA player data."""

import logging

from src.config import STAT_CATEGORIES

logger = logging.getLogger(__name__)


def extract_stat_leaders(leaders_data):
    """Extract top 5 leaders per stat category.

    Args:
        leaders_data: dict from fetch_league_leaders()

    Returns:
        dict mapping category -> top 5 list
    """
    if not leaders_data:
        return {cat: [] for cat in STAT_CATEGORIES}

    result = {}
    for cat in STAT_CATEGORIES:
        result[cat] = leaders_data.get(cat, [])[:5]
    return result


def compute_award_races(players):
    """Compute simplified award race rankings based on stats.

    Args:
        players: list of player dicts from fetch_all_players()

    Returns:
        dict with 'mvp' and 'dpoy' lists
    """
    if not players:
        return {"mvp": [], "dpoy": []}

    # Filter to players with significant minutes
    qualified = [p for p in players if p.get("gp", 0) >= 30 and p.get("min", 0) >= 25]

    # MVP: weighted combination of pts, ast, reb, efficiency
    for p in qualified:
        p["_mvp_score"] = (
            p.get("pts", 0) * 1.0
            + p.get("ast", 0) * 1.5
            + p.get("reb", 0) * 1.2
            + p.get("fg_pct", 0) * 20
            + p.get("eff", 0) * 0.5
        )

    mvp_candidates = sorted(qualified, key=lambda p: p["_mvp_score"], reverse=True)[:5]
    mvp = [
        {
            "rank": i + 1,
            "player_name": p.get("player_name"),
            "team_abbr": p.get("team_abbr"),
            "pts": round(p.get("pts", 0), 1),
            "ast": round(p.get("ast", 0), 1),
            "reb": round(p.get("reb", 0), 1),
        }
        for i, p in enumerate(mvp_candidates)
    ]

    # DPOY: blocks + steals weighted
    for p in qualified:
        p["_dpoy_score"] = p.get("blk", 0) * 2.0 + p.get("stl", 0) * 1.5 + p.get("reb", 0) * 0.5

    dpoy_candidates = sorted(qualified, key=lambda p: p["_dpoy_score"], reverse=True)[:5]
    dpoy = [
        {
            "rank": i + 1,
            "player_name": p.get("player_name"),
            "team_abbr": p.get("team_abbr"),
            "blk": round(p.get("blk", 0), 1),
            "stl": round(p.get("stl", 0), 1),
            "reb": round(p.get("reb", 0), 1),
        }
        for i, p in enumerate(dpoy_candidates)
    ]

    # Clean up temp keys
    for p in qualified:
        p.pop("_mvp_score", None)
        p.pop("_dpoy_score", None)

    return {"mvp": mvp, "dpoy": dpoy}


def build_analysis(leaders_data, players):
    """Run all analysis and return combined results.

    Args:
        leaders_data: dict from fetch_league_leaders()
        players: list from fetch_all_players()

    Returns:
        dict with all analysis results
    """
    return {
        "stat_leaders": extract_stat_leaders(leaders_data),
        "award_races": compute_award_races(players),
    }
