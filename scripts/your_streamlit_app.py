import streamlit as st
import json
from pathlib import Path
from ics import Calendar, Event
from datetime import datetime, timedelta

# Constants
RATING_EMOJIS = {
    "❤️": "Must see",
    "🟢": "Want to see",
    "🟡": "Maybe",
    "🚫": "Skip"
}

def load_lineup_data():
    """Load the historical lineup data from JSON file"""
    data_path = Path("data/lineups_historical.json")
    with open(data_path) as f:
        return json.load(f)

def get_festivals_and_years(data):
    """Extract unique festival/year combinations"""
    festivals = {}
    for artist in data:
        festival = artist["festival_name"]
        year = artist["festival_year"]
        if festival not in festivals:
            festivals[festival] = set()
        festivals[festival].add(year)
    return festivals

def get_artists_for_festival_year(data, festival, year):
    """Get all artists for a specific festival and year"""
    return [
        artist for artist in data
        if artist["festival_name"] == festival
        and artist["festival_year"] == year
    ]

def create_calendar_export(artists_data, ratings):
    """Create ICS calendar with rated artists"""
    cal = Calendar()

    # Only include artists with positive ratings
    valid_ratings = ["❤️", "🟢", "🟡"]
    rated_artists = [
        artist for artist in artists_data
        if ratings.get(artist["artist_name"]) in valid_ratings
    ]

    for artist in rated_artists:
        event = Event()
        event.name = f"{artist['artist_name']} {ratings[artist['artist_name']]}"

        # If we have actual start/end times, use those
        if artist["start_ts"] and artist["end_ts"]:
            event.begin = artist["start_ts"]
            event.end = artist["end_ts"]
        else:
            # Placeholder times if not available
            event.begin = datetime(artist["festival_year"], 7, 1, 12, 0)  # Noon on July 1st
            event.end = event.begin + timedelta(hours=1)

        event.description = artist.get("bio_short", "")
        event.location = artist.get("stage_name", "TBA")
        cal.events.add(event)

    return cal

def main():
    st.title("Festival Lineup Rater")

    # Load data
    data = load_lineup_data()
    festivals = get_festivals_and_years(data)

    # Festival selection
    festival = st.selectbox(
        "Select Festival",
        options=list(festivals.keys())
    )

    # Year selection
    year = st.selectbox(
        "Select Year",
        options=sorted(festivals[festival], reverse=True)
    )

    # Get artists for selected festival/year
    artists = get_artists_for_festival_year(data, festival, year)

    # Initialize session state for ratings if not exists
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}

    st.subheader("Rate Artists")

    # Display artists in a single column
    for artist in artists:
        name = artist["artist_name"]
        current_rating = st.session_state.ratings.get(name, "")

        # Artist info
        st.markdown(f"### {name}")
        if artist.get("bio_short"):
            st.markdown(f"*{artist['bio_short']}*")
        if artist.get("stage_name"):
            st.markdown(f"**Stage:** {artist['stage_name']}")

        # Rating selection with radio buttons
        rating = st.radio(
            f"Rate {name}",
            options=[""] + list(RATING_EMOJIS.keys()),
            format_func=lambda x: f"{x} {RATING_EMOJIS.get(x, 'No rating')}" if x else "No rating",
            horizontal=True,
            key=f"rate_{name}"
        )

        if rating:
            st.session_state.ratings[name] = rating

        st.markdown("---")  # Add separator between artists

    # Export calendar button
    if st.button("Export Calendar"):
        cal = create_calendar_export(artists, st.session_state.ratings)
        st.download_button(
            label="Download Calendar File",
            data=str(cal),
            file_name=f"{festival}_{year}_lineup.ics",
            mime="text/calendar"
        )

    # Display current ratings summary
    st.subheader("Your Ratings Summary")
    for emoji, label in RATING_EMOJIS.items():
        rated_artists = [
            name for name, rating in st.session_state.ratings.items()
            if rating == emoji
        ]
        if rated_artists:
            st.markdown(f"**{emoji} {label}:**")
            st.markdown("- " + "\n- ".join(rated_artists))

if __name__ == "__main__":
    main()
