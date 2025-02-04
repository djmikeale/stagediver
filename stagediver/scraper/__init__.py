"""
Web scraping functionality.
Contains:
- Festival website scrapers
- Data extraction logic
- Scheduling for regular updates
- Raw data validation
"""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional, Type

from stagediver.models import ScrapedData
from stagediver.config import LINEUPS_FILE

def load_existing_lineups() -> List[Dict]:
    """Load existing lineup data with integrity check."""
    if not os.path.exists(LINEUPS_FILE):
        os.makedirs(os.path.dirname(LINEUPS_FILE), exist_ok=True)
        return []

    try:
        with open(LINEUPS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Basic integrity checks
        if not isinstance(data, list):
            raise ValueError("Lineup data must be a list")

        required_fields = {'festival_name', 'scrape_ts', 'artists'}
        for entry in data:
            if not isinstance(entry, dict):
                raise ValueError("Each scrape entry must be a dictionary")
            if not all(field in entry for field in required_fields):
                raise ValueError(f"Missing required fields: {required_fields}")
            if not isinstance(entry['artists'], list):
                raise ValueError("Artists must be a list")

        return data

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error loading existing lineup data: {e}")
        backup_file = f"{LINEUPS_FILE}.bak"
        if os.path.exists(LINEUPS_FILE):
            os.rename(LINEUPS_FILE, backup_file)
            print(f"Corrupted file backed up to {backup_file}")
        return []

def save_lineups(lineups: List[Dict]):
    """Save lineup data with error handling."""
    temp_file = f"{LINEUPS_FILE}.tmp"

    try:
        # Write to temporary file first
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(lineups, f, indent=2, ensure_ascii=False)

        # If successful, rename to actual file
        os.replace(temp_file, LINEUPS_FILE)

    except Exception as e:
        print(f"Error saving lineup data: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise

def transform_artist_data(raw_data: dict) -> dict:
    """Transform raw artist data into standardized format."""
    return {
        "artist_name": raw_data.get("name"),
        "stage_name": raw_data.get("stage"),
        "start_ts": raw_data.get("start_ts"),
        "end_ts": raw_data.get("end_ts"),
        "social_links": {
            "spotify": raw_data.get("spotify_link")
        } if raw_data.get("spotify_link") else {},
        "bio_short": raw_data.get("short_description"),
        "bio_long": raw_data.get("long_description"),
        "country_code": raw_data.get("country_code"),
        "scrape_url": raw_data.get("url"),
        "other_data": raw_data.get("other_data", {})
    }

def run_scraper(scraper, sample_size: Optional[int] = None) -> None:
    """Run a scraper and save results."""
    print(f"Running {scraper.__class__.__name__}...")

    # Get lineup data
    lineup_data = scraper.fetch_lineup(sample_size=sample_size)

    # Convert ScrapedData to dictionary format
    new_lineup = {
        "festival_name": lineup_data.festival_name,
        "festival_year": scraper.festival_year,
        "scrape_ts": datetime.utcnow().isoformat(),
        "artists": []
    }

    # Process each artist from raw content
    for artist_data in lineup_data.raw_content["artists"]:
        artist = {
            "artist_name": artist_data["name"],
            "stage_name": artist_data.get("stage", ""),
            "start_ts": None,  # Could parse from performance_date if needed
            "end_ts": None,
            "social_links": {
                "spotify": artist_data.get("spotify_link")
            } if artist_data.get("spotify_link") else {},
            "bio_short": artist_data.get("short_description", ""),
            "bio_long": artist_data.get("long_description", ""),
            "country_code": None,  # Not available in current scrape
            "scrape_url": artist_data["url"],
            "other_data": {}
        }
        new_lineup["artists"].append(artist)

    # Load existing lineups
    existing_lineups = load_existing_lineups()

    # Add new lineup to the list
    existing_lineups.append(new_lineup)

    # Save to file
    os.makedirs(os.path.dirname(LINEUPS_FILE), exist_ok=True)
    with open(LINEUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing_lineups, f, indent=2)

    print(f"Saved {len(new_lineup['artists'])} artists to {LINEUPS_FILE}")
