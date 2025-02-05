import pytest
from datetime import datetime
from copy import deepcopy
from scripts.generate_lineup_history import generate_historical_data, create_historical_key

def test_historical_data_handling():
    # Test data setup
    ts1 = "2024-01-01T12:00:00+00:00"
    ts2 = "2024-01-02T12:00:00+00:00"

    # Initial lineup with one artist
    lineup1 = {
        "festival_name": "Test Festival",
        "festival_year": 2024,
        "scrape_ts": ts1,
        "artists": [{
            "artist_name": "Artist 1",
            "artist_id": "id1",
            "stage_name": "Stage A",
            "bio_short": "Original bio"
        }]
    }

    # Second lineup with modified artist and one new artist
    lineup2 = {
        "festival_name": "Test Festival",
        "festival_year": 2024,
        "scrape_ts": ts2,
        "artists": [
            {
                "artist_name": "Artist 1",
                "artist_id": "id1",
                "stage_name": "Stage B",  # Changed
                "bio_short": "Original bio"
            },
            {
                "artist_name": "Artist 2",
                "artist_id": "id2",
                "stage_name": "Stage C",
                "bio_short": "New artist"
            }
        ]
    }

    # Existing historical data
    existing_historical = [{
        "artist_name": "Artist 1",
        "artist_id": "id1",
        "stage_name": "Stage A",
        "bio_short": "Original bio",
        "festival_name": "Test Festival",
        "festival_year": 2024,
        "_valid_from": ts1,
        "_valid_to": None,
        "_is_current": True
    }]

    # Generate historical data
    result = generate_historical_data([lineup1, lineup2], existing_historical)

    # Sort results by artist name and valid_from for consistent testing
    result.sort(key=lambda x: (x['artist_name'], x['_valid_from']))

    # Verify results
    assert len(result) == 3, "Should have 3 records total"

    # Check Artist 1's records
    artist1_records = [r for r in result if r['artist_name'] == 'Artist 1']
    assert len(artist1_records) == 2, "Artist 1 should have 2 records"

    # First record should be closed
    assert artist1_records[0]['_valid_from'] == ts1, "Should preserve original valid_from"
    assert artist1_records[0]['_valid_to'] == ts2, "Should be closed at second scrape"
    assert not artist1_records[0]['_is_current'], "Should not be current"
    assert artist1_records[0]['stage_name'] == "Stage A", "Should preserve original stage"

    # Second record should be current
    assert artist1_records[1]['_valid_from'] == ts1, "Should preserve original valid_from"
    assert artist1_records[1]['_valid_to'] is None, "Should be open"
    assert artist1_records[1]['_is_current'], "Should be current"
    assert artist1_records[1]['stage_name'] == "Stage B", "Should have updated stage"

    # Check Artist 2's record
    artist2_records = [r for r in result if r['artist_name'] == 'Artist 2']
    assert len(artist2_records) == 1, "Artist 2 should have 1 record"
    assert artist2_records[0]['_valid_from'] == ts2, "Should start at second scrape"
    assert artist2_records[0]['_valid_to'] is None, "Should be open"
    assert artist2_records[0]['_is_current'], "Should be current"

def test_artist_removal():
    ts1 = "2024-01-01T12:00:00+00:00"
    ts2 = "2024-01-02T12:00:00+00:00"

    # Initial lineup with two artists
    lineup1 = {
        "festival_name": "Test Festival",
        "festival_year": 2024,
        "scrape_ts": ts1,
        "artists": [
            {
                "artist_name": "Artist 1",
                "artist_id": "id1",
                "stage_name": "Stage A"
            },
            {
                "artist_name": "Artist 2",
                "artist_id": "id2",
                "stage_name": "Stage B"
            }
        ]
    }

    # Second lineup with one artist removed
    lineup2 = {
        "festival_name": "Test Festival",
        "festival_year": 2024,
        "scrape_ts": ts2,
        "artists": [{
            "artist_name": "Artist 1",
            "artist_id": "id1",
            "stage_name": "Stage A"
        }]
    }

    # Existing historical data
    existing_historical = [
        {
            "artist_name": "Artist 1",
            "artist_id": "id1",
            "stage_name": "Stage A",
            "festival_name": "Test Festival",
            "festival_year": 2024,
            "_valid_from": ts1,
            "_valid_to": None,
            "_is_current": True
        },
        {
            "artist_name": "Artist 2",
            "artist_id": "id2",
            "stage_name": "Stage B",
            "festival_name": "Test Festival",
            "festival_year": 2024,
            "_valid_from": ts1,
            "_valid_to": None,
            "_is_current": True
        }
    ]

    result = generate_historical_data([lineup1, lineup2], existing_historical)

    # Check Artist 2's removal
    artist2_records = [r for r in result if r['artist_name'] == 'Artist 2']
    assert len(artist2_records) == 1, "Artist 2 should have 1 record"
    assert artist2_records[0]['_valid_from'] == ts1, "Should preserve original valid_from"
    assert artist2_records[0]['_valid_to'] == ts2, "Should be closed at second scrape"
    assert not artist2_records[0]['_is_current'], "Should not be current"

    # Check Artist 1 remains unchanged
    artist1_records = [r for r in result if r['artist_name'] == 'Artist 1']
    assert len(artist1_records) == 1, "Artist 1 should have 1 record"
    assert artist1_records[0]['_valid_from'] == ts1, "Should preserve original valid_from"
    assert artist1_records[0]['_valid_to'] is None, "Should remain open"
    assert artist1_records[0]['_is_current'], "Should remain current"
