import streamlit as st
from stagediver.web.components.sidebar import show_sidebar, RATING_EMOJIS
from stagediver.web.components.utils import get_artists_for_festival_year

def update_ratings(edited_data, all_artists):
    """Update session state ratings when table is edited"""
    for i, artist in enumerate(all_artists):
        new_rating = edited_data["Rating"][i]
        current_rating = st.session_state.ratings.get(artist["name"], "")
        if new_rating != current_rating:
            if new_rating:  # Only update if a rating was selected
                st.session_state.ratings[artist["name"]] = new_rating
            elif artist["name"] in st.session_state.ratings:  # Remove rating if empty
                del st.session_state.ratings[artist["name"]]
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

    if not artists:
        st.info("No artists found for this festival. Please select a different festival from the sidebar.")
        return

    # Create a list of all artists with their full info
    all_artists = [
        {
            "name": artist["artist_name"],
            "rating": st.session_state.ratings.get(artist["artist_name"], ""),
            "stage": artist.get("stage_name", "TBA"),
            "bio": artist.get("bio_short", ""),
            "spotify": artist.get("social_links", {}).get("spotify", ""),
        }
        for artist in artists
    ]

    # Sort artists: rated ones first (by rating), then unrated (alphabetically)
    emoji_order = list(RATING_EMOJIS.keys())
    all_artists.sort(
        key=lambda x: (
            # First sort by whether it has a rating (rated first)
            x["rating"] == "",
            # Then by rating order (if rated)
            emoji_order.index(x["rating"]) if x["rating"] in emoji_order else len(emoji_order),
            # Finally by name
            x["name"].lower()
        )
    )

    # Create a DataFrame for display
    data = {
        "Artist": [artist["name"] for artist in all_artists],
        "Rating": [artist["rating"] for artist in all_artists],
        "Stage": [artist["stage"] for artist in all_artists],
        "Description": [artist["bio"] for artist in all_artists],
        "Spotify": [artist["spotify"] for artist in all_artists],
    }

    # Show rating stats
    total_artists = len(all_artists)
    rated_artists = sum(1 for artist in all_artists if artist["rating"])
    st.caption(f"Rated {rated_artists} out of {total_artists} artists")

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
                options=[""] + list(RATING_EMOJIS.keys()),  # Add empty option to allow clearing rating
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
    update_ratings(edited_data, all_artists)

if __name__ == "__main__":
    main()
