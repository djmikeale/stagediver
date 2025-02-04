# Stagediver

## Find new music to love, and plan your must-see concerts

## What it does
Stagediver helps you:
- Discover festival lineups through automated website scraping
- Preview and rate artists' music to find your favorites
- Create an optimized concert schedule based on ratings, time, and location
- Export your schedule to your calendar

## installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development Roadmap

1. Core Data Models & Storage
   - [ ] Design JSON schema for festivals, artists, stages, performances
   - [ ] Implement Pydantic models for data validation
   - [ ] Create JSON file-based data store
   - [ ] Add helper functions for data access and modification
   - [ ] Generate sample festival data for development

2. Festival Data Collection
   - [ ] Build festival website scrapers
   - [ ] Parse and normalize lineup data
   - [ ] Store festival data in database

3. Artist Enrichment
   - [ ] Integrate with music APIs (Spotify, etc)
   - [ ] Collect artist metadata and preview URLs
   - [ ] Classify genres and detect similar artists
   - [ ] Run data quality checks

4. User Features
   - [ ] Export to calendar
   - [ ] Implement artist rating system
   - [ ] Import from calendar

5. Calendar Integration
   - [ ] Generate iCal feeds
   - [ ] Add export filtering options
   - [ ] Support multi-user exports
   - [ ] Test with various calendar clients
   - [ ] apple script to remove old events + import new events

streamlit:
- create "save string" to save the current state of the app as a string, and "load string" to load the app state from a string. and add as parameter to url
- add "compare" functionality to compare different festivals
- add "compare faves" functionality to compare your favorite artists with others' favorite artists
