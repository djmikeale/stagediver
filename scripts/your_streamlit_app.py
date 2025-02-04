import streamlit as st
import json
from pathlib import Path
from ics import Calendar, Event
from datetime import datetime, timedelta
import re

# Constants
RATING_EMOJIS = {
    "❤️": "Must see",
    "🟢": "Want to see",
    "🟡": "Maybe",
    "🚫": "Skip"
}

ARTISTS_PER_PAGE = 5

def extract_spotify_id(spotify_url):
    """Extract Spotify artist ID from full URL"""
    if not spotify_url:
        return None
    match = re.search(r'artist/([a-zA-Z0-9]+)', spotify_url)
    return match.group(1) if match else None

def spotify_embed(artist_id):
    """Generate Spotify embed HTML for an artist"""
    return f"""
        <iframe style="border-radius:12px"
                src="https://open.spotify.com/embed/artist/{artist_id}?utm_source=generator"
                width="100%"
                height="152"
                frameBorder="0"
                allowfullscreen=""
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy">
        </iframe>
    """

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

    # Pagination
    total_pages = (len(artists) + ARTISTS_PER_PAGE - 1) // ARTISTS_PER_PAGE

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        page = st.number_input(
            f"Page (1-{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1
        )

    start_idx = (page - 1) * ARTISTS_PER_PAGE
    end_idx = min(start_idx + ARTISTS_PER_PAGE, len(artists))

    st.subheader(f"Rate Artists (Showing {start_idx + 1}-{end_idx} of {len(artists)})")

    # Display artists for current page
    for artist in artists[start_idx:end_idx]:
        name = artist["artist_name"]
        current_rating = st.session_state.ratings.get(name, "")

        # Artist info
        st.markdown(f"### {name}")
        if artist.get("bio_short"):
            st.markdown(f"*{artist['bio_short']}*")
        if artist.get("stage_name"):
            st.markdown(f"**Stage:** {artist['stage_name']}")

        # Spotify embed
        if artist.get("social_links", {}).get("spotify"):
            spotify_id = extract_spotify_id(artist["social_links"]["spotify"])
            if spotify_id:
                st.components.v1.html(
                    spotify_embed(spotify_id),
                    height=170
                )

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

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if page > 1:
            if st.button("← Previous Page"):
                st.session_state.page = page - 1
                st.experimental_rerun()
    with col2:
        if page < total_pages:
            if st.button("Next Page →"):
                st.session_state.page = page + 1
                st.experimental_rerun()

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
