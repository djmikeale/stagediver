import streamlit as st
from stagediver.web.components.sidebar import show_sidebar, RATING_EMOJIS
from stagediver.web.components.utils import get_artists_for_festival_year

def main():
    # Show shared sidebar
    show_sidebar()

    st.title("My Lineup")

    # Get artists for selected festival/year
    artists = get_artists_for_festival_year(
        st.session_state.artists_data,
        st.session_state.selected_festival,
        st.session_state.selected_year
    )

    # Create a list of rated artists with their full info
    rated_artists = [
        {
            "name": artist["artist_name"],
            "rating": st.session_state.ratings.get(artist["artist_name"], ""),
            "stage": artist.get("stage_name", "TBA"),
            "bio": artist.get("bio_short", ""),
            "spotify": artist.get("social_links", {}).get("spotify", ""),
        }
        for artist in artists
        if artist["artist_name"] in st.session_state.ratings
    ]

    if not rated_artists:
        st.info("You haven't rated any artists yet. Head over to the Explore Artists page to start rating!")
    else:
        # Sort artists by rating (highest first)
        # Convert ratings to numeric values (1 for lowest, 5 for highest)
        rating_values = {"⭐": 5, "👍": 4, "🤔": 3, "👎": 2, "💩": 1}
        rated_artists.sort(
            key=lambda x: rating_values.get(x["rating"], 0),
            reverse=True
        )

        # Create a DataFrame for display with enhanced columns
        data = {
            "Artist": [artist["name"] for artist in rated_artists],
            "Rating": [artist["rating"] for artist in rated_artists],
            "Stage": [artist["stage"] for artist in rated_artists],
            "Description": [artist["bio"] for artist in rated_artists],
            "Spotify": [
                f"[![Spotify]('https://spotify.com/favicon.ico')]({url})" if url else ""
                for artist in rated_artists
                for url in [artist["spotify"]]
            ],
        }

        # Display as a styled table
        st.dataframe(
            data,
            hide_index=True,
            column_config={
                "Artist": st.column_config.TextColumn(
                    "Artist",
                    width="medium",
                ),
                "Rating": st.column_config.TextColumn(
                    "Rating",
                    width="small",
                ),
                "Stage": st.column_config.TextColumn(
                    "Stage",
                    width="small",
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    width="large",
                ),
                "Spotify": st.column_config.LinkColumn(
                    "Links",
                    width="small",
                    display_text="🎵"
                ),
            }
        )

if __name__ == "__main__":
    main()
