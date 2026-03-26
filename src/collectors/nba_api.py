"""NBA API collector for scores and standings.

Uses CDN endpoints for scoreboard and schedule data.
"""

import logging
import time

import requests

from src.config import (
    API_REQUEST_DELAY,
    API_RETRY_COUNT,
    API_RETRY_DELAYS,
    NBA_CDN_SCOREBOARD_URL,
    NBA_CDN_URL,
    NBA_HEADERS,
    NBA_STATS_URL,
    TEAMS,
)

logger = logging.getLogger(__name__)

_last_request_time = 0.0


def _request(url, params=None):
    """Make an HTTP request with retry and exponential backoff.

    Returns parsed JSON or None on failure.
    """
    global _last_request_time

    # Rate limiting
    elapsed = time.time() - _last_request_time
    if elapsed < API_REQUEST_DELAY:
        time.sleep(API_REQUEST_DELAY - elapsed)

    for attempt in range(API_RETRY_COUNT):
        try:
            _last_request_time = time.time()
            resp = requests.get(
                url, headers=NBA_HEADERS, params=params, timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            delay = API_RETRY_DELAYS[attempt] if attempt < len(API_RETRY_DELAYS) else 10
            logger.warning(
                "API request failed (attempt %d/%d): %s. Retrying in %ds...",
                attempt + 1, API_RETRY_COUNT, e, delay,
            )
            if attempt < API_RETRY_COUNT - 1:
                time.sleep(delay)

    logger.error("API request failed after %d attempts: %s", API_RETRY_COUNT, url)
    return None


def _parse_result_set(data, set_name=None, set_index=0):
    """Parse NBA API resultSets format into a list of dicts."""
    if not data:
        return []

    # Some endpoints use "resultSet" (singular), others use "resultSets" (plural)
    result_sets = data.get("resultSets", [])
    if not result_sets:
        single = data.get("resultSet")
        if single:
            result_sets = [single]
        else:
            return []

    target = None
    if set_name:
        for rs in result_sets:
            if rs.get("name") == set_name:
                target = rs
                break
        if not target:
            logger.warning("Result set '%s' not found", set_name)
            return []
    else:
        if set_index < len(result_sets):
            target = result_sets[set_index]
        else:
            return []

    headers = target.get("headers", [])
    rows = target.get("rowSet", [])
    return [dict(zip(headers, row)) for row in rows]


def fetch_scoreboard():
    """Fetch today's game scores from CDN endpoint.

    Returns:
        dict with 'games' list and 'game_date', or None on failure.
    """
    data = _request(NBA_CDN_SCOREBOARD_URL)
    if not data:
        return None

    scoreboard = data.get("scoreboard", {})
    game_date = scoreboard.get("gameDate", "")
    raw_games = scoreboard.get("games", [])

    games = []
    for g in raw_games:
        home = g.get("homeTeam", {})
        away = g.get("awayTeam", {})
        games.append({
            "game_id": g.get("gameId"),
            "status": g.get("gameStatusText", ""),
            "home_team": home.get("teamTricode", ""),
            "home_team_id": home.get("teamId"),
            "home_score": home.get("score"),
            "away_team": away.get("teamTricode", ""),
            "away_team_id": away.get("teamId"),
            "away_score": away.get("score"),
        })

    return {"games": games, "game_date": game_date}


def fetch_standings():
    """Derive standings from CDN schedule data.

    The schedule endpoint contains each game's result and the team's
    W-L record at the time of the game. We find each team's most
    recent finished game to get their current record.

    Returns:
        dict with 'east' and 'west' lists, or None on failure.
    """
    url = f"{NBA_CDN_URL}/static/json/staticData/scheduleLeagueV2.json"
    data = _request(url)
    if not data:
        return None

    schedule = data.get("leagueSchedule", {})
    game_dates = schedule.get("gameDates", [])
    if not game_dates:
        return None

    # Find the latest W-L record for each team from finished games
    # Iterate in reverse (most recent first)
    team_records = {}  # team_id -> {wins, losses, team_name, ...}
    recent_results = {}  # team_id -> list of recent W/L results

    for date_entry in reversed(game_dates):
        for g in date_entry.get("games", []):
            if g.get("gameStatus") != 3:  # Not finished
                continue

            for side in ("homeTeam", "awayTeam"):
                t = g.get(side, {})
                tid = t.get("teamId")
                if not tid or tid in team_records:
                    continue

                team_records[tid] = {
                    "team_id": tid,
                    "team_abbr": t.get("teamTricode", ""),
                    "team_name": f"{t.get('teamCity', '')} {t.get('teamName', '')}".strip(),
                    "wins": t.get("wins", 0),
                    "losses": t.get("losses", 0),
                }

            # Stop once we have all 30 teams
            if len(team_records) >= 30:
                break
        if len(team_records) >= 30:
            break

    # Collect recent results (last 10) for each team
    games_counted = {}  # team_id -> count
    for date_entry in reversed(game_dates):
        for g in date_entry.get("games", []):
            if g.get("gameStatus") != 3:
                continue

            home = g.get("homeTeam", {})
            away = g.get("awayTeam", {})
            home_id = home.get("teamId")
            away_id = away.get("teamId")
            home_score = int(home.get("score", 0) or 0)
            away_score = int(away.get("score", 0) or 0)

            for tid, won in [(home_id, home_score > away_score), (away_id, away_score > home_score)]:
                if not tid:
                    continue
                if tid not in recent_results:
                    recent_results[tid] = []
                if tid not in games_counted:
                    games_counted[tid] = 0
                if games_counted[tid] < 10:
                    recent_results[tid].append("W" if won else "L")
                    games_counted[tid] += 1

    # Build standings
    east = []
    west = []

    for tid, rec in team_records.items():
        abbr = rec["team_abbr"]
        team_info = TEAMS.get(abbr)
        conference = team_info[2] if team_info else "Unknown"

        total = rec["wins"] + rec["losses"]
        win_pct = rec["wins"] / total if total > 0 else 0.0

        results = recent_results.get(tid, [])
        l10_w = results.count("W")
        l10_l = results.count("L")

        # Streak
        streak_type = results[0] if results else ""
        streak_count = 0
        for r in results:
            if r == streak_type:
                streak_count += 1
            else:
                break
        streak = f"{streak_type}{streak_count}" if streak_type else ""

        entry = {
            "team_id": tid,
            "team_abbr": abbr,
            "team_name": rec["team_name"],
            "wins": rec["wins"],
            "losses": rec["losses"],
            "win_pct": win_pct,
            "conf_rank": 0,
            "streak": streak,
            "last_10": f"{l10_w}-{l10_l}",
        }

        if conference == "East":
            east.append(entry)
        else:
            west.append(entry)

    east.sort(key=lambda x: x["win_pct"], reverse=True)
    west.sort(key=lambda x: x["win_pct"], reverse=True)

    for i, team in enumerate(east):
        team["conf_rank"] = i + 1
    for i, team in enumerate(west):
        team["conf_rank"] = i + 1

    return {"east": east, "west": west}
