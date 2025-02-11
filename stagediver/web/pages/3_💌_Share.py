import streamlit as st
from stagediver.web.components.sidebar import show_sidebar

def main():
    # Show shared sidebar with artists data from session state
    show_sidebar(artists_data=st.session_state.artists_data)

    st.title("Share Your Lineup")
    # ... rest of the existing content ...

if __name__ == "__main__":
    main()
