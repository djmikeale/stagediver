import streamlit as st
from stagediver.web.components.sidebar import show_sidebar, RATING_EMOJIS
from stagediver.web.components.utils import get_artists_for_festival_year

def update_ratings(edited_data, rated_artists):
    """Update session state ratings when table is edited"""
    for i, artist in enumerate(rated_artists):
        new_rating = edited_data["Rating"][i]
        if new_rating != artist["rating"]:
            st.session_state.ratings[artist["name"]] = new_rating
            st.rerun()

def main():
    # Show shared sidebar with wide layout
    show_sidebar(layout="wide")

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
        # Sort artists by rating (highest first, using order in RATING_EMOJIS)
        emoji_order = list(RATING_EMOJIS.keys())
        rated_artists.sort(
            key=lambda x: -(emoji_order.index(x["rating"]) if x["rating"] in emoji_order else len(emoji_order)),
            reverse=True
        )

        # Create a DataFrame for display
        data = {
            "Artist": [artist["name"] for artist in rated_artists],
            "Rating": [artist["rating"] for artist in rated_artists],
            "Stage": [artist["stage"] for artist in rated_artists],
            "Description": [artist["bio"] for artist in rated_artists],
            "Spotify": [artist["spotify"] for artist in rated_artists],
        }

        # Display as an editable table
        edited_data = st.data_editor(
            data,
            hide_index=True,
            column_config={
                "Artist": st.column_config.TextColumn(
                    "Artist",
                    width="medium",
                ),
                "Rating": st.column_config.SelectboxColumn(
                    "Rating",
                    width="small",
                    options=list(RATING_EMOJIS.keys()),
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
                    "Spotify",
                    width="small",
                    display_text="▶️",
                ),
            },
            disabled=["Artist", "Stage", "Description", "Spotify"],
            key="lineup_editor"
        )

        # Check for changes and update ratings
        update_ratings(edited_data, rated_artists)

if __name__ == "__main__":
    main()
