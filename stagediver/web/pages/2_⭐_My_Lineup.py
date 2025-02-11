import streamlit as st
from stagediver.web.components.sidebar import show_sidebar, RATING_EMOJIS
from stagediver.web.components.artist_card import display_artist_card

def get_unrated_artists(artists_data, ratings):
    """Get list of artists that haven't been rated yet"""
    return [
        artist for artist in artists_data
        if artist["artist_name"] not in ratings
        and artist.get("_is_current", False)  # Only show current artists
    ]

def get_artists_for_festival_year(data, festival, year):
    """Get all artists for a specific festival and year"""
    return [
        artist for artist in data
        if artist["festival_name"] == festival
        and artist["festival_year"] == year
        and artist.get("_is_current", False)  # Only show current artists
    ]

def create_spotify_player_with_overlay(spotify_id, visible=True):
    """Create a Spotify player with an overlay"""
    st.components.v1.html(
        f"""
        <style>
            .player-container {{
                position: relative;
                width: 100%;
                height: 152px;
                border-radius: 12px;
                overflow: hidden;
            }}
            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: calc(100% - 50px);
                height: 100%;
                background: rgba(14, 17, 23, 0.95);
                backdrop-filter: blur(8px);
                opacity: {1 if visible else 0};
                pointer-events: {'' if visible else 'none'};
                transition: opacity 0.3s ease;
                z-index: 1000;
            }}
        </style>
        <div class="player-container">
            <iframe src="https://open.spotify.com/embed/album/{spotify_id}"
                    width="100%"
                    height="152"
                    frameBorder="0"
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                    loading="lazy">
            </iframe>
            <div class="overlay"></div>
        </div>
        """,
        height=170
    )

def main():
    # Show shared sidebar
    show_sidebar()

    st.title("My Festival Lineup")

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
        st.success("🎉 You've rated all artists! Check out your ratings summary below.")
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

    # Show ratings summary
    st.divider()
    st.subheader("Your Ratings Summary")

    total_rated = len(st.session_state.ratings)
    if total_rated > 0:
        st.caption(f"You've rated {total_rated} out of {len(artists)} artists")

        # Show summary by rating
        for emoji, label in RATING_EMOJIS.items():
            rated_artists = [
                name for name, rating in st.session_state.ratings.items()
                if rating == emoji
            ]
            if rated_artists:
                with st.expander(f"{emoji} {label} ({len(rated_artists)})"):
                    st.markdown("- " + "\n- ".join(sorted(rated_artists)))
    else:
        st.info("Start rating artists to build your lineup!")

if __name__ == "__main__":
    main()
