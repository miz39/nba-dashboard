"""Configuration for NBA Dashboard."""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
ASSETS_DIR = PROJECT_ROOT / "assets"
DOCS_DIR = PROJECT_ROOT / "docs"
DATA_DIR = DOCS_DIR / "data"

# NBA API
NBA_STATS_URL = "https://stats.nba.com/stats"
NBA_CDN_URL = "https://cdn.nba.com"
NBA_CDN_SCOREBOARD_URL = f"{NBA_CDN_URL}/static/json/liveData/scoreboard/todaysScoreboard_00.json"

NBA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
}

API_RETRY_COUNT = 3
API_RETRY_DELAYS = [2, 5, 10]
API_REQUEST_DELAY = 1.0  # seconds between API calls

# Current season
CURRENT_SEASON = "2025-26"
CURRENT_SEASON_TYPE = "Regular Season"

# Theme
THEME = {
    "bg": "#0a0a0a",
    "card": "#1a1a2e",
    "accent": "#c9082a",
    "text": "#e0e0e0",
    "text_secondary": "#8a8a8a",
    "success": "#00c853",
    "warning": "#ffd600",
}

# All 30 NBA teams: abbreviation -> (team_id, full_name, conference, division)
TEAMS = {
    # Eastern Conference - Atlantic
    "BOS": (1610612738, "Boston Celtics", "East", "Atlantic"),
    "BKN": (1610612751, "Brooklyn Nets", "East", "Atlantic"),
    "NYK": (1610612752, "New York Knicks", "East", "Atlantic"),
    "PHI": (1610612755, "Philadelphia 76ers", "East", "Atlantic"),
    "TOR": (1610612761, "Toronto Raptors", "East", "Atlantic"),
    # Eastern Conference - Central
    "CHI": (1610612741, "Chicago Bulls", "East", "Central"),
    "CLE": (1610612739, "Cleveland Cavaliers", "East", "Central"),
    "DET": (1610612765, "Detroit Pistons", "East", "Central"),
    "IND": (1610612754, "Indiana Pacers", "East", "Central"),
    "MIL": (1610612749, "Milwaukee Bucks", "East", "Central"),
    # Eastern Conference - Southeast
    "ATL": (1610612737, "Atlanta Hawks", "East", "Southeast"),
    "CHA": (1610612766, "Charlotte Hornets", "East", "Southeast"),
    "MIA": (1610612748, "Miami Heat", "East", "Southeast"),
    "ORL": (1610612753, "Orlando Magic", "East", "Southeast"),
    "WAS": (1610612764, "Washington Wizards", "East", "Southeast"),
    # Western Conference - Northwest
    "DEN": (1610612743, "Denver Nuggets", "West", "Northwest"),
    "MIN": (1610612750, "Minnesota Timberwolves", "West", "Northwest"),
    "OKC": (1610612760, "Oklahoma City Thunder", "West", "Northwest"),
    "POR": (1610612757, "Portland Trail Blazers", "West", "Northwest"),
    "UTA": (1610612762, "Utah Jazz", "West", "Northwest"),
    # Western Conference - Pacific
    "GSW": (1610612744, "Golden State Warriors", "West", "Pacific"),
    "LAC": (1610612746, "LA Clippers", "West", "Pacific"),
    "LAL": (1610612747, "Los Angeles Lakers", "West", "Pacific"),
    "PHX": (1610612756, "Phoenix Suns", "West", "Pacific"),
    "SAC": (1610612758, "Sacramento Kings", "West", "Pacific"),
    # Western Conference - Southwest
    "DAL": (1610612742, "Dallas Mavericks", "West", "Southwest"),
    "HOU": (1610612745, "Houston Rockets", "West", "Southwest"),
    "MEM": (1610612763, "Memphis Grizzlies", "West", "Southwest"),
    "NOP": (1610612740, "New Orleans Pelicans", "West", "Southwest"),
    "SAS": (1610612759, "San Antonio Spurs", "West", "Southwest"),
}

# Reverse lookup: team_id -> abbreviation
TEAM_ID_TO_ABBR = {v[0]: k for k, v in TEAMS.items()}

# Stat categories for leaders
STAT_CATEGORIES = ["PTS", "AST", "REB", "BLK", "STL"]

# Hot streak detection
HOT_STREAK_GAMES = 5
HOT_STREAK_THRESHOLD = 0.15  # 15% above season average
