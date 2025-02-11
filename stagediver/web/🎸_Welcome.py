import streamlit as st
from stagediver.web.components.sidebar import show_sidebar, RATING_EMOJIS

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
                name for name, rating in st.session_state.ratings.items()
                if rating == emoji
            ]
            if rated_artists:
                with st.expander(f"{label} ({len(rated_artists)})",icon=f"{emoji}"):
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

    st.markdown(f"""
    Welcome to Stagediver! 🎪

    We'll help you discover and organize your festival experience:

    1. **Explore Artists** - Browse and discover artists playing at the festival
    2. **My Lineup** - Rate artists and build your personal schedule
    3. **Share** - share and compare your lineup with friends

    Get started by selecting a page from the sidebar! 👈
    """)

    # Stats section
    st.divider()
    st.subheader("Quick Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Festivals", str(len({artist["festival_name"] for artist in st.session_state.artists_data})))
    with col2:
        st.metric("Artists", f"{len(st.session_state.artists_data):,}")
    with col3:
        rated_count = len(st.session_state.ratings)
        st.metric("Your Ratings", str(rated_count))

    # Show ratings summary if there are any ratings
    if st.session_state.ratings:
        show_ratings_summary(st.session_state.artists_data)

if __name__ == "__main__":
    main()
