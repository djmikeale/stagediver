import streamlit as st

from stagediver.web.components.sidebar import RATING_EMOJIS, show_sidebar


def show_ratings_summary(artists):
    """Display a summary of user ratings"""
    st.divider()
    st.subheader("Your Ratings")

    total_rated = len(st.session_state.ratings)
    if total_rated > 0:
        st.caption(f"You've rated {total_rated} out of {len(artists)} artists")

        # Show summary by rating
        for emoji, label in RATING_EMOJIS.items():
            rated_artists = [
                name
                for name, rating in st.session_state.ratings.items()
                if rating == emoji
            ]
            if rated_artists:
                with st.expander(f"{label} ({len(rated_artists)})", icon=f"{emoji}"):
                    st.markdown("- " + "\n- ".join(sorted(rated_artists)))
    else:
        st.info("Start rating artists to build your lineup!")


def main():
    # Initialize session state for ratings if not exists
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}

    # Show shared sidebar
    show_sidebar()

    # Main content
    st.title("Stagediver")

    if not st.session_state.get("selected_festival"):
        st.info("Please select a festival from the sidebar to begin")
        return

    st.markdown(
        f"""
    - 🕵️ Discover hidden gems
    - 📅 Save future favorites to your calendar
    - 🎉 Make unforgettable festival memories

    ## Introduction

    - With 100s of artists at large festivals, it's hard to know who to see.
    - Stagediver makes it easy to explore artists, and find out which ones you can't miss... and which ones are just `meh`.
    - When you're done with rating, export favorite artists to your calendar.

    *Don't wanna listen to 100+ artists in one sitting? Save your progress, and come back later to listen to more!*


    ## 👈 Get started by selecting a page from the sidebar!
    """
    )

    # Show ratings summary if there are any ratings
    if st.session_state.ratings:
        show_ratings_summary(st.session_state.artists_data["artists"])


if __name__ == "__main__":
    main()
