import streamlit as st
from stagediver.web.components.sidebar import show_sidebar, RATING_EMOJIS
from stagediver.web.components.artist_card import display_artist_card
from stagediver.web.components.utils import get_artists_for_festival_year

def get_unrated_artists(artists_data, ratings):
    """Get list of artists that haven't been rated yet"""
    return [
        artist for artist in artists_data
        if artist["artist_name"] not in ratings
        and artist.get("_is_current", False)  # Only show current artists
    ]

def main():
    # Show shared sidebar
    show_sidebar()

    st.title("Explore Artists")

    # Add state management for the overlay visibility
    if 'overlay_visible' not in st.session_state:
        st.session_state.overlay_visible = True

    # Get artists for selected festival/year
    artists = get_artists_for_festival_year(
        st.session_state.artists_data,
        st.session_state.selected_festival,
        st.session_state.selected_year
    )

    # Get unrated artists
    unrated_artists = get_unrated_artists(artists, st.session_state.ratings)

    if not unrated_artists:
        st.success("🎉 You've rated all artists! Check out your ratings on the Welcome page.")
    else:
        # Show count of remaining artists
        st.caption(f"{len(unrated_artists)} artists left to rate")

        # Display current artist
        current_artist = unrated_artists[0]

        # Create a card-like container
        with st.container():
            # Button to toggle overlay
            if st.button('Reveal' if st.session_state.overlay_visible else 'Hide'):
                st.session_state.overlay_visible = not st.session_state.overlay_visible

            selected = display_artist_card(
                current_artist,
                blind_mode=st.session_state.overlay_visible
            )

            # Handle rating selection
            if selected is not None:
                new_rating = selected.split()[0]  # Get just the emoji
                st.session_state.ratings[current_artist["artist_name"]] = new_rating
                st.rerun()

if __name__ == "__main__":
    main()
