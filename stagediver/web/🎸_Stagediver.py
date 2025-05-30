from datetime import datetime, timedelta

import streamlit as st

from stagediver.web.components.artist_card import display_artist_card
from stagediver.web.components.sidebar import RATING_INFO, show_sidebar
from stagediver.web.components.utils import get_artists_for_festival_year


def get_unrated_artists(artists_data, ratings):
    """Get list of artists that haven't been rated yet"""
    return [artist for artist in artists_data if artist["artist_name"] not in ratings]


def main():
    # Initialize session state for ratings if not exists
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}

    # Show shared sidebar
    show_sidebar()

    col1, col2 = st.columns([10, 1], vertical_alignment="bottom")
    with col1:
        st.title(
            "Stagediver",
            help="""
With 100s of artists at large festivals, it's easy to miss out on great acts. Stagediver lets you:

- 🕵️ Discover which artists you'll love, and which ones are just `meh`
- 📅 Save your lineup to your calendar
- 🎉 Make unforgettable festival memories

---

This page contains two views:

- 🙈: Avoid bias by album artwork, nationality, gender, etc; focus on the music
- 👀: See all info related to the artist

---

Use the sidebar to see overviews of your lineup, and import/export your progress.
""",
            anchor=False,
        )

    with col2:
        st.session_state.view_mode = st.radio(
            "Select View",
            options=["blind", "explore"],
            format_func=lambda x: {
                "blind": "🙈",
                "explore": "👀",
            }[x],
            label_visibility="collapsed",
        )
        # st.session_state.view_mode = st.segmented_control(
        #    "select view",
        #    label_visibility="collapsed",
        #    options=["blind", "explore"],
        #    format_func=lambda x: {
        #        "blind": "🙈",
        #        "explore": "👀",
        #    }[x],
        #    default="blind",
        # )

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
            st.success("🎉 You've rated all artists!")
        else:
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


if __name__ == "__main__":
    main()
