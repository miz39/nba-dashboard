"""Main builder: collect data, analyze, generate HTML dashboard."""

import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.collectors.nba_api import fetch_scoreboard, fetch_standings
from src.collectors.player_stats import fetch_league_leaders, fetch_all_players
from src.analyzers.stat_analyzer import build_analysis
from src.config import ASSETS_DIR, DATA_DIR, DOCS_DIR, TEMPLATES_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def collect_data():
    """Collect all data from NBA API."""
    logger.info("Collecting data from NBA API...")

    logger.info("Fetching scoreboard (CDN)...")
    scoreboard = fetch_scoreboard()

    logger.info("Fetching standings (game log)...")
    standings = fetch_standings()

    logger.info("Fetching league leaders...")
    leaders = fetch_league_leaders()

    logger.info("Fetching all player stats...")
    players = fetch_all_players()

    return {
        "scoreboard": scoreboard,
        "standings": standings,
        "leaders": leaders,
        "players": players,
    }


def analyze_data(collected):
    """Run analysis on collected data."""
    logger.info("Analyzing data...")
    return build_analysis(collected.get("leaders"), collected.get("players"))


def build_html(collected, analysis):
    """Render HTML dashboard using Jinja2."""
    logger.info("Building HTML dashboard...")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template("index.html")

    scoreboard = collected.get("scoreboard") or {}
    games = scoreboard.get("games", [])
    game_date = scoreboard.get("game_date", "")

    context = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "score_date": game_date,
        "games": games,
        "standings": collected.get("standings"),
        "stat_leaders": analysis.get("stat_leaders"),
        "award_races": analysis.get("award_races"),
    }

    html = template.render(**context)
    return html, context


def main():
    """Main orchestration: collect -> analyze -> build."""
    logger.info("=== NBA Dashboard Build Start ===")

    # Ensure output directories exist
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Collect
    collected = collect_data()

    # Analyze
    analysis = analyze_data(collected)

    # Build HTML
    html, context = build_html(collected, analysis)

    # Write HTML
    output_html = DOCS_DIR / "index.html"
    output_html.write_text(html, encoding="utf-8")
    logger.info("HTML written to %s", output_html)

    # Copy assets
    for asset_file in ASSETS_DIR.iterdir():
        if asset_file.is_file():
            shutil.copy2(asset_file, DOCS_DIR / asset_file.name)
            logger.info("Copied %s to docs/", asset_file.name)

    # Save raw data as JSON
    dashboard_data = {
        "updated_at": context["updated_at"],
        "score_date": context["score_date"],
        "games": context["games"],
        "standings": collected.get("standings"),
        "stat_leaders": analysis.get("stat_leaders"),
        "award_races": analysis.get("award_races"),
    }
    data_file = DATA_DIR / "dashboard.json"
    data_file.write_text(
        json.dumps(dashboard_data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    logger.info("Data written to %s", data_file)

    logger.info("=== NBA Dashboard Build Complete ===")


if __name__ == "__main__":
    main()
