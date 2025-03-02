from datetime import datetime, timedelta

import streamlit as st

from stagediver.web.components.artist_card import display_artist_card
from stagediver.web.components.sidebar import RATING_EMOJIS, show_sidebar
from stagediver.web.components.utils import get_artists_for_festival_year


def get_unrated_artists(artists_data, ratings):
    """Get list of artists that haven't been rated yet"""
    return [
        artist
        for artist in artists_data
        if artist["artist_name"] not in ratings
        and artist.get("_is_current", False)  # Only show current artists
    ]


def main():
    # Show shared sidebar
    show_sidebar()

    st.title("Explore Artists")

    # Initialize view mode in session state if not exists
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "explore"

    # Create view selector using radio
    st.session_state.view_mode = st.radio(
        "Select View",
        options=["explore", "blind", "all"],
        format_func=lambda x: {
            "explore": "Explore",
            "blind": "Blind Listen",
            "all": "All Artists",
        }[x],
        horizontal=True,
        label_visibility="collapsed",
    )

    # Get artists for selected festival/year
    artists = get_artists_for_festival_year(
        st.session_state.artists_data,
        st.session_state.selected_festival,
        st.session_state.selected_year,
    )

    # Display content based on selected view mode
    if st.session_state.view_mode in ["explore", "blind"]:
        # Get unrated artists
        unrated_artists = get_unrated_artists(artists, st.session_state.ratings)

        if not unrated_artists:
            st.success(
                "🎉 You've rated all artists! Check out your ratings on the Welcome page."
            )
        else:
            # Show count of remaining artists
            st.caption(f"{len(unrated_artists)} artists left to rate")

            # Display current artist
            current_artist = unrated_artists[0]

            # Create a card-like container
            with st.container():
                selected = display_artist_card(
                    current_artist, blind_mode=(st.session_state.view_mode == "blind")
                )

                # Handle rating selection
                if selected is not None:
                    new_rating = selected.split()[0]  # Get just the emoji
                    st.session_state.ratings[current_artist["artist_name"]] = new_rating
                    st.rerun()

    elif st.session_state.view_mode == "all":
        ARTISTS_PER_PAGE = 5

        # Initialize page in session state if not exists
        if "page" not in st.session_state:
            st.session_state.page = 1

        # Pagination logic
        total_pages = (len(artists) + ARTISTS_PER_PAGE - 1) // ARTISTS_PER_PAGE

        col1, col2, col3 = st.columns([2, 3, 2])
        with col2:
            page = st.number_input(
                f"Page (1-{total_pages})",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.page,
                key="page_input",
            )
            st.session_state.page = page

        start_idx = (page - 1) * ARTISTS_PER_PAGE
        end_idx = min(start_idx + ARTISTS_PER_PAGE, len(artists))

        st.caption(f"Showing {start_idx + 1}-{end_idx} of {len(artists)} artists")

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


if __name__ == "__main__":
    main()
