"""
Generate type 2 historical data from lineup scrapes.
Tracks changes to artist data over time and maintains history of changes.
"""

from typing import List, Dict, Any
import random
import string
from copy import deepcopy
from stagediver.common.config import LINEUPS_FILE, HISTORICAL_FILE
from stagediver.common.utils import load_json_file, save_json_file

def load_lineups() -> List[Dict]:
    """Load existing lineup data."""
    return load_json_file(LINEUPS_FILE)

def load_historical() -> List[Dict]:
    """Load existing historical data."""
    try:
        return load_json_file(HISTORICAL_FILE)
    except FileNotFoundError:
        return []

def save_historical(data: List[Dict]):
    """Save historical data."""
    save_json_file(data, HISTORICAL_FILE)

def create_historical_key(artist: Dict, festival: str, year: int) -> str:
    """
    Create a unique key for an artist at a specific festival and year.

    Args:
        artist: Artist data dictionary
        festival: Festival name
        year: Festival year

    Returns:
        Unique identifier string in format "festival::year::artist_name"
    """
    return f"{festival}::{year}::{artist['artist_name']}"

def has_relevant_changes(current: Dict, previous: Dict) -> bool:
    """
    Check if there are meaningful changes between two artist records.
    Ignores metadata fields.
    """
    relevant_fields = {
        'artist_name', 'stage_name', 'start_ts', 'end_ts',
        'social_links', 'bio_short', 'bio_long', 'country_code',
        'scrape_url', 'other_data'
    }

    return any(
        current.get(field) != previous.get(field)
        for field in relevant_fields
    )

def generate_artist_id() -> str:
    """
    Generate a random 5-character ID using alphanumeric characters.

    Returns:
        5-character string using [a-zA-Z0-9]
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=5))

def get_or_create_artist_id(artist_name: str, existing_ids: Dict[str, str]) -> str:
    """
    Get existing artist ID or generate a new one if it doesn't exist.

    Args:
        artist_name: Name of the artist
        existing_ids: Dictionary mapping artist names to their IDs

    Returns:
        5-character artist ID
    """
    if artist_name in existing_ids:
        return existing_ids[artist_name]

    # Generate new unique ID
    while True:
        new_id = generate_artist_id()
        if new_id not in existing_ids.values():
            existing_ids[artist_name] = new_id
            return new_id

def generate_historical_data(lineups: List[Dict], existing_historical: List[Dict] = None) -> List[Dict]:
    """
    Generate type 2 historical data from lineup scrapes.
    Preserves existing historical records and adds new changes.
    """
    historical_records: Dict[str, List[Dict]] = {}
    active_artists: Dict[str, bool] = {}
    artist_ids: Dict[str, str] = {}  # Map artist names to IDs

    # Load existing historical records and their artist IDs
    if existing_historical:
        for record in existing_historical:
            key = create_historical_key(record, record['festival_name'], record['festival_year'])
            if key not in historical_records:
                historical_records[key] = []
            # Preserve the existing record exactly as is
            historical_records[key].append(deepcopy(record))
            if record['_is_current']:
                active_artists[key] = True
            # Store existing artist ID mapping
            if 'artist_id' in record:
                artist_ids[record['artist_name']] = record['artist_id']

    # Sort lineups by scrape timestamp
    sorted_lineups = sorted(lineups, key=lambda x: x['scrape_ts'])

    # Process each lineup scrape
    for lineup in sorted_lineups:
        festival_name = lineup['festival_name']
        festival_year = lineup['festival_year']
        scrape_ts = lineup['scrape_ts']

        # Get current artists in this scrape
        current_artists = {}
        for artist in lineup['artists']:
            key = create_historical_key(artist, festival_name, festival_year)
            # Ensure artist has an ID
            if 'artist_id' not in artist:
                artist['artist_id'] = get_or_create_artist_id(artist['artist_name'], artist_ids)
            current_artists[key] = artist

        # Check for removed artists
        for key in list(active_artists.keys()):
            if key not in current_artists and active_artists[key]:
                # Artist was removed - close the record
                latest_record = historical_records[key][-1]
                if latest_record['_valid_to'] is None:  # Only if not already closed
                    latest_record['_valid_to'] = scrape_ts
                    latest_record['_is_current'] = False
                    active_artists[key] = False

        # Process current artists
        for key, artist in current_artists.items():
            if key not in historical_records:
                # New artist - create first record with scrape timestamp
                historical_records[key] = []
                new_record = deepcopy(artist)
                new_record.update({
                    'festival_name': festival_name,
                    'festival_year': festival_year,
                    '_valid_from': scrape_ts,  # When we first observed this artist
                    '_valid_to': None,
                    '_is_current': True
                })
                historical_records[key].append(new_record)
                active_artists[key] = True
            else:
                # Existing artist - check for changes
                latest_record = historical_records[key][-1]
                if has_relevant_changes(artist, latest_record):
                    # Close previous record
                    latest_record['_valid_to'] = scrape_ts
                    latest_record['_is_current'] = False

                    # Create new record with updated data but preserve valid_from and artist_id
                    new_record = deepcopy(artist)
                    new_record.update({
                        'festival_name': festival_name,
                        'festival_year': festival_year,
                        '_valid_from': latest_record['_valid_from'],  # Use original valid_from
                        '_valid_to': None,
                        '_is_current': True,
                        'artist_id': latest_record['artist_id']  # Preserve the artist ID
                    })

                    historical_records[key].append(new_record)
                    active_artists[key] = True

    # Flatten records into a list
    return [
        record
        for records in historical_records.values()
        for record in records
    ]

def main():
    """Generate and save historical lineup data."""
    print("Loading lineup data...")
    lineups = load_lineups()

    if not lineups:
        print("No lineup data found.")
        return

    print("Loading existing historical data...")
    existing_historical = load_historical()

    print(f"Generating historical data from {len(lineups)} scrapes...")
    historical_data = generate_historical_data(lineups, existing_historical)

    print(f"Saving {len(historical_data)} historical records...")
    save_historical(historical_data)
    print(f"Historical data saved to {HISTORICAL_FILE}")

    # Print some stats
    unique_artists = len({
        create_historical_key(
            record,
            record['festival_name'],
            record['festival_year']
        )
        for record in historical_data
    })
    current_records = len([r for r in historical_data if r['_is_current']])

    print("\nStats:")
    print(f"Total records: {len(historical_data)}")
    print(f"Active records: {current_records}")
    print(f"Added records: {len([r for r in historical_data if r['_valid_from'] == r['_valid_to']])}")
    print(f"Removed records: {len([r for r in historical_data if r['_valid_to'] is not None])}")

if __name__ == "__main__":
    main()
