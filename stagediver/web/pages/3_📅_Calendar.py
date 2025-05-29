from datetime import datetime, timedelta

import streamlit as st
from streamlit_calendar import calendar

from stagediver.web.components.sidebar import show_sidebar
from stagediver.web.components.utils import get_artists_for_festival_year


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

    # Define color mapping for ratings
    rating_colors = {
        "❤️": "#ff4b4b",  # Red for Must see
        "🟢": "#177233",  # Green for Yes
        "🟡": "#ffa421",  # Yellow for Meh
        "🚫": "#808080",  # Gray for No
        "⚪": "#a9a9a9",  # Dark gray for unrated
    }

    # Create calendar events from all artists
    calendar_events = []
    for artist in artists:
        start_time = artist.get("start_ts")
        if start_time:
            start_time = datetime.fromisoformat(start_time)
        else:
            start_time = datetime(2024, 7, 1, 13, 37)

        end_time = artist.get("end_ts")
        if end_time:
            end_time = datetime.fromisoformat(end_time)
        else:
            end_time = start_time + timedelta(hours=1)

        # Get rating and color
        rating = st.session_state.ratings.get(artist["artist_name"], "⚪")
        color = rating_colors.get(rating, rating_colors["⚪"])

        event = {
            "title": f"{rating} {artist['artist_name']}",
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "resourceId": artist.get("stage_name", "Unknown Stage"),
            "description": artist.get("bio_short", ""),
            "url": artist.get("scrape_url", ""),
            "backgroundColor": color,
            "borderColor": color,
        }
        calendar_events.append(event)

    # Get unique stages for resources
    stages = sorted(set(event["resourceId"] for event in calendar_events))

    # Add filters in a more compact layout
    col1, col2 = st.columns(2)
    with col1:
        selected_stages = st.multiselect(
            "Stages",
            options=stages,
            default=["Apollo", "Arena", "Gaia", "Gloria", "Orange Scene", "Platform"],
            help="Select stages to display",
        )

    with col2:
        selected_ratings = st.multiselect(
            "Ratings",
            options=list(rating_colors.keys()),
            default=list(rating_colors.keys()),
            help="Filter by rating",
        )

    # Filter events based on selected stages and ratings
    filtered_events = [
        event
        for event in calendar_events
        if event["resourceId"] in selected_stages
        and any(rating in event["title"] for rating in selected_ratings)
    ]

    # Filter resources based on selected stages
    filtered_resources = [
        {"id": stage, "building": stage, "title": stage}
        for stage in selected_stages
        if any(
            event["resourceId"] == stage
            and any(rating in event["title"] for rating in selected_ratings)
            for event in calendar_events
        )
    ]

    calendar_options = {
        "editable": False,
        "selectable": True,
        "initialDate": (
            calendar_events[0]["start"].split("T")[0]
            if calendar_events
            else datetime.now().strftime("%Y-%m-%d")
        ),
        "initialView": "resourceTimeGridDay",
        "slotMinTime": "09:00:00",
        "slotMaxTime": "28:30:00",  # 28:30 represents 04:30 the next day
        "resourceGroupField": "building",
        "resources": filtered_resources,
    }

    calendar_data = calendar(
        events=filtered_events,
        options=calendar_options,
    )


if __name__ == "__main__":
    main()
