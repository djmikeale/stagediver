import streamlit as st
from stagediver.web.components.sidebar import show_sidebar

def main():
    # Initialize session state for ratings if not exists
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}

    # Show shared sidebar
    show_sidebar()

    # Main content
    st.title("Festival Lineup Rater")

    st.markdown("""
    Welcome to Festival Lineup Rater! 🎪

    This tool helps you discover and organize your festival experience:

    1. **Explore** - Browse and discover artists playing at the festival
    2. **My Lineup** - Rate artists and build your personal schedule
    3. **Share** - Export and share your lineup with friends

    Get started by selecting a page from the sidebar! 👈
    """)

    # Stats section
    st.divider()
    st.subheader("Quick Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Festivals", "5")
    with col2:
        st.metric("Artists", "1,000+")
    with col3:
        st.metric("Users", "100+")

if __name__ == "__main__":
    main()
