"""
Script to fetch and save the complete Roskilde Festival 2025 lineup.
"""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict
from stagediver.scraper.festivals.roskilde.roskilde_2025 import RoskildeFestival2025Scraper

LINEUPS_FILE = "data/lineups.json"

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

def transform_artist_data(raw_data: dict) -> dict:
    """Transform raw artist data into standardized format."""

    # Map Danish weekdays to dates
    date_mapping = {
        "Onsdag 2. juli": "07-02",
        "Torsdag 3. juli": "07-03",
        "Fredag 4. juli": "07-04",
        "Lørdag 5. juli": "07-05"
    }

    # Convert performance date to ISO format
    performance_date = date_mapping.get(raw_data['performance_date'])
    if performance_date:
        start_ts = f"2025-{performance_date}T12:00:00Z"
        end_ts = f"2025-{performance_date}T13:30:00Z"
    else:
        start_ts = None
        end_ts = None

    return {
        "artist_name": raw_data["name"],
        "stage_name": raw_data["stage"],
        "start_ts": start_ts,
        "end_ts": end_ts,
        "social_links": {
            "spotify": raw_data["spotify_link"]
        } if raw_data["spotify_link"] else {},
        "bio_short": raw_data["short_description"],
        "bio_long": raw_data["long_description"],
        "country_code": None,  # Not available in current scrape
        "scrape_url": raw_data["url"],
        "other_data": {}
    }

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

def main():
    scraper = RoskildeFestival2025Scraper()
    print("Starting Roskilde Festival 2025 scraper...")

    # Load existing data
    existing_lineups = load_existing_lineups()
    print(f"Loaded {len(existing_lineups)} existing scrapes")

    # Fetch new data
    data = scraper.fetch_lineup(sample_size=5)
    scrape_timestamp = datetime.now(timezone.utc)

    # Create new scrape entry
    new_scrape = {
        "festival_name": "Roskilde Festival",
        "scrape_ts": scrape_timestamp.isoformat(),
        "artists": [
            transform_artist_data(artist)
            for artist in data.raw_content["artists"]
        ]
    }

    # Add new scrape to existing data
    all_lineups = existing_lineups + [new_scrape]

    # Save combined data
    save_lineups(all_lineups)
    print(f"\nSaved new scrape with {len(new_scrape['artists'])} artists to {LINEUPS_FILE}")
    print(f"Total scrapes in file: {len(all_lineups)}")

if __name__ == "__main__":
    main()
