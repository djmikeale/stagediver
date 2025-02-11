import streamlit as st
import json
from pathlib import Path
from ics import Calendar, Event
from datetime import datetime, timedelta
from stagediver.common.config import HISTORICAL_FILE
from stagediver.web.components.sidebar import show_sidebar, RATING_EMOJIS
from stagediver.web.components.artist_card import display_artist_card

ARTISTS_PER_PAGE = 5

def load_lineup_data():
    """Load the historical lineup data from JSON file"""
    data_path = Path(HISTORICAL_FILE)
    with open(data_path) as f:
        return json.load(f)

def get_artists_for_festival_year(data, festival, year):
    """Get all artists for a specific festival and year"""
    return [
        artist for artist in data
        if artist["festival_name"] == festival
        and artist["festival_year"] == year
        and artist.get("_is_current", False)  # Only show current artists
    ]

def main():
    # Show shared sidebar
    show_sidebar()

    st.title("Explore Artists")

    # Get artists for selected festival/year from session state
    artists = get_artists_for_festival_year(
        st.session_state.artists_data,
        st.session_state.selected_festival,
        st.session_state.selected_year
    )

    # Initialize session state for ratings if not exists
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}

    # Pagination
    total_pages = (len(artists) + ARTISTS_PER_PAGE - 1) // ARTISTS_PER_PAGE

    # Initialize page in session state if not exists
    if "page" not in st.session_state:
        st.session_state.page = 1

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        # Use session state page as the default value
        page = st.number_input(
            f"Page (1-{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.page,
            key="page_input"
        )
        # Keep page state in sync with number input
        st.session_state.page = page

    start_idx = (page - 1) * ARTISTS_PER_PAGE
    end_idx = min(start_idx + ARTISTS_PER_PAGE, len(artists))

    st.subheader(f"Rate Artists (Showing {start_idx + 1}-{end_idx} of {len(artists)})")

    # Display artists for current page
    for artist in artists[start_idx:end_idx]:
        selected = display_artist_card(artist)

        # Handle rating selection
        if selected is not None:
            new_rating = selected.split()[0]  # Get just the emoji
            name = artist["artist_name"]
            if new_rating != st.session_state.ratings.get(name, ""):
                st.session_state.ratings[name] = new_rating
                st.rerun()

        st.divider()

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if page > 1:
            if st.button("« previous", key=f"prev_page_{page}"):
                st.session_state.page -= 1
                st.rerun()
    with col2:
        if page < total_pages:
            if st.button("Next »", key=f"next_page_{page}"):
                st.session_state.page += 1
                st.rerun()

    # Keep the ratings summary at the very end
    st.divider()
    st.subheader("Your Ratings Summary")
    for emoji, label in RATING_EMOJIS.items():
        rated_artists = [
            name for name, rating in st.session_state.ratings.items()
            if rating == emoji
        ]
        if rated_artists:
            with st.expander(f"{emoji} {label} ({len(rated_artists)})"):
                st.markdown("- " + "\n- ".join(sorted(rated_artists)))

if __name__ == "__main__":
    main()
