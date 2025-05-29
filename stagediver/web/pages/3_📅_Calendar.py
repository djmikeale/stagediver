import streamlit as st

from stagediver.web.components.sidebar import show_sidebar
from stagediver.web.components.utils import get_artists_for_festival_year
from stagediver.web.pages.calendar_view import show_calendar_view


def main():
    # Show shared sidebar with wide layout
    show_sidebar(layout="wide")

    st.title("Calendar View")

    # Get artists for selected festival/year
    artists = get_artists_for_festival_year(
        st.session_state.artists_data,
        st.session_state.selected_festival,
        st.session_state.selected_year,
    )

    if not artists:
        st.info(
            "No artists found for this festival. Please select a different festival from the sidebar."
        )
        return

    # Show calendar view
    show_calendar_view(artists, st.session_state.ratings)


if __name__ == "__main__":
    main()
