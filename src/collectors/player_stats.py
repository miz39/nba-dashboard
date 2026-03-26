"""Player stats collector from NBA API.

Uses the leagueleaders endpoint which returns full stat lines for all players.
"""

import logging

from src.collectors.nba_api import _request, _parse_result_set
from src.config import CURRENT_SEASON, NBA_STATS_URL, STAT_CATEGORIES

logger = logging.getLogger(__name__)


def fetch_league_leaders():
    """Fetch league leaders using the leagueleaders endpoint.

    One call returns all stats columns, so we extract leaders per category
    by re-sorting the same dataset.

    Returns:
        dict mapping category -> list of player dicts, or None on failure.
    """
    url = f"{NBA_STATS_URL}/leagueleaders"
    params = {
        "LeagueID": "00",
        "PerMode": "PerGame",
        "Scope": "S",
        "Season": CURRENT_SEASON,
        "SeasonType": "Regular Season",
        "StatCategory": "PTS",
    }

    data = _request(url, params)
    if not data:
        return None

    rows = _parse_result_set(data, "LeagueLeaders")
    if not rows:
        return None

    leaders = {}
    for category in STAT_CATEGORIES:
        sorted_rows = sorted(rows, key=lambda r: r.get(category, 0), reverse=True)
        top = []
        for row in sorted_rows[:10]:
            top.append({
                "player_id": row.get("PLAYER_ID"),
                "player_name": row.get("PLAYER"),
                "team_abbr": row.get("TEAM"),
                "gp": row.get("GP"),
                "min": row.get("MIN"),
                "value": row.get(category),
            })
        leaders[category] = top

    return leaders


def fetch_all_players():
    """Fetch all player stats from leagueleaders endpoint.

    Returns:
        list of player stat dicts, or None on failure.
    """
    url = f"{NBA_STATS_URL}/leagueleaders"
    params = {
        "LeagueID": "00",
        "PerMode": "PerGame",
        "Scope": "S",
        "Season": CURRENT_SEASON,
        "SeasonType": "Regular Season",
        "StatCategory": "PTS",
    }

    data = _request(url, params)
    if not data:
        return None

    rows = _parse_result_set(data, "LeagueLeaders")
    players = []
    for row in rows:
        players.append({
            "player_id": row.get("PLAYER_ID"),
            "player_name": row.get("PLAYER"),
            "team_abbr": row.get("TEAM"),
            "gp": row.get("GP", 0),
            "min": row.get("MIN", 0.0),
            "pts": row.get("PTS", 0.0),
            "ast": row.get("AST", 0.0),
            "reb": row.get("REB", 0.0),
            "stl": row.get("STL", 0.0),
            "blk": row.get("BLK", 0.0),
            "fg_pct": row.get("FG_PCT", 0.0),
            "fg3_pct": row.get("FG3_PCT", 0.0),
            "ft_pct": row.get("FT_PCT", 0.0),
            "eff": row.get("EFF", 0.0),
        })

    return players
