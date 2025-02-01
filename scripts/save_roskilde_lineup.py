"""
Script to fetch and save the complete Roskilde Festival 2025 lineup.
"""

import json
from datetime import datetime, timezone
from stagediver.scraper.festivals.roskilde.roskilde_2025 import RoskildeFestival2025Scraper

def transform_artist_data(raw_data: dict, scrape_timestamp: datetime) -> dict:
    """Transform raw scraped data into standardized format."""

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
        "festival_name": "Roskilde Festival",
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
        "scrape_ts": scrape_timestamp.isoformat(),
        "other_data": {}
    }

def main():
    scraper = RoskildeFestival2025Scraper()
    print("Starting Roskilde Festival 2025 scraper...")

    # Fetch all artists (no limit)
    data = scraper.fetch_lineup()
    scrape_timestamp = datetime.now(timezone.utc)  # Using timezone-aware UTC time

    # Transform data to required format
    transformed_data = [
        transform_artist_data(artist, scrape_timestamp)
        for artist in data.raw_content["artists"]
    ]

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"roskilde_lineup_{timestamp}.json"

    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(transformed_data)} artists to {filename}")

if __name__ == "__main__":
    main()
