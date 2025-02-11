import streamlit as st
import json
from pathlib import Path
from ics import Calendar, Event
from datetime import datetime, timedelta
import re
from stagediver.common.config import HISTORICAL_FILE
from stagediver.web.components.sidebar import show_sidebar, RATING_EMOJIS

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
    # Use artists data from session state if available, otherwise load it
    if "artists_data" not in st.session_state:
        st.session_state.artists_data = load_lineup_data()

    data = st.session_state.artists_data

    # Show shared sidebar with artists data
    show_sidebar()

    st.title("Explore Artists")

    # Check if festival is selected
    if not st.session_state.get("selected_festival"):
        st.info("Please select a festival from the sidebar to begin")
        return

    # Get artists for selected festival/year from session state
    artists = get_artists_for_festival_year(
        data,
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
        name = artist["artist_name"]

        # Artist info
        st.markdown(f"### {name}")
        if artist.get("bio_short"):
            if artist.get("bio_long"):  # Show short bio as expander title
                with st.expander(f"{artist['bio_short']} *:gray[click to read more]*"):
                    st.markdown(artist["bio_long"].replace('\n', '<br><br>'), unsafe_allow_html=True)
            else:  # Only short bio available
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

        # Rating buttons
        current_rating = st.session_state.ratings.get(name, "")

        # Create options list for segmented control
        rating_options = [f"{emoji} {label}" for emoji, label in RATING_EMOJIS.items()]

        # Find current rating option or default to None
        default = None
        if current_rating:
            default = f"{current_rating} {RATING_EMOJIS[current_rating]}"

        selected = st.segmented_control(
            label="Rate this artist:",
            options=rating_options,
            key=f"rate_{name}",
            default=default
        )

        # Update rating based on selection
        if selected is not None:
            new_rating = selected.split()[0]  # Get just the emoji
            if new_rating != current_rating:
                st.session_state.ratings[name] = new_rating
                st.rerun()
        elif current_rating:  # Selection was cleared
            del st.session_state.ratings[name]
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
            st.markdown(f"**{emoji} {label}:**")
            st.markdown("- " + "\n- ".join(rated_artists))

if __name__ == "__main__":
    main()
