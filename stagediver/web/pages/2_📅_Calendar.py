from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import streamlit as st
from streamlit_calendar import calendar

from stagediver.web.components.artist_card import display_artist_card
from stagediver.web.components.sidebar import RATING_INFO, show_sidebar
from stagediver.web.components.utils import get_artists_for_festival_year


def create_calendar_event(artist: Dict[str, Any], rating: str) -> Dict[str, Any]:
    """Creates a calendar event from artist data."""
    start_time = (
        datetime.fromisoformat(artist.get("start_ts"))
        if artist.get("start_ts")
        else datetime(2024, 7, 1, 13, 37)
    )
    end_time = (
        datetime.fromisoformat(artist.get("end_ts"))
        if artist.get("end_ts")
        else start_time + timedelta(hours=1)
    )

    # Get color from RATING_INFO or use gray for unrated
    color = RATING_INFO[rating]["bg_color"] if rating in RATING_INFO else "#a9a9a9"

    return {
        "title": f"{rating} {artist['artist_name']}",
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "resourceId": artist.get("stage_name", "Unknown Stage"),
        "description": artist.get("bio_short", ""),
        "backgroundColor": color,
        "borderColor": color,
        "artist_data": artist,
    }


def get_calendar_options(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Returns calendar configuration options."""
    return {
        "editable": False,
        "selectable": True,
        "initialDate": (
            events[0]["start"].split("T")[0]
            if events
            else datetime.now().strftime("%Y-%m-%d")
        ),
        "initialView": "resourceTimeGridDay",
        "slotMinTime": "11:00:00",
        "slotMaxTime": "28:30:00",  # 28:30 represents 04:30 the next day
        "resourceGroupField": "building",
        "height": "500px",  # Set a fixed height for the calendar
        "scrollTime": "17:00:00",
        "slotLabelFormat": {
            "hour": "2-digit",
            "hour12": False,
        },
        "allDaySlot": False,
    }


def handle_event_click(
    clicked_event: Dict[str, Any], artists: List[Dict[str, Any]]
) -> None:
    """Handles calendar event click and displays artist card."""
    artist_name = clicked_event.get("title", "Unknown Artist")[2:]
    artist = next((a for a in artists if a["artist_name"] == artist_name), None)

    if artist:
        selected = display_artist_card(artist)
        if selected is not None:
            new_rating = selected.split()[0]  # Get just the emoji
            if new_rating != st.session_state.ratings.get(artist_name, ""):
                st.session_state.ratings[artist_name] = new_rating
                st.rerun()
    else:
        st.error(f"Could not find artist data for: {artist_name}")


def main() -> None:
    """Main function to render the calendar view."""
    # Show shared sidebar with wide layout
    show_sidebar(layout="wide")

    # Initialize clicked event in session state if not exists
    if "clicked_event" not in st.session_state:
        st.session_state.clicked_event = None

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

    # Create calendar events
    calendar_events = [
        create_calendar_event(
            artist,
            st.session_state.ratings.get(artist["artist_name"], "⚪"),
        )
        for artist in artists
    ]

    # Get unique stages for resources
    stages = sorted(set(event["resourceId"] for event in calendar_events))

    # Add filters in a more compact layout
    col1, col2 = st.columns(2)
    with col1:
        selected_stages = st.multiselect(
            "Stages",
            options=stages,
            default=[
                "Apollo",
                "Arena",
                "Avalon",
                "Gaia",
                "Gloria",
                "Orange Scene",
                "Platform",
            ],
            help="Select stages to display",
        )

    with col2:
        rating_options = [
            f"{emoji} {info['text']}" for emoji, info in RATING_INFO.items()
        ]
        rating_options.append("⚪ Unrated")
        selected_ratings = st.multiselect(
            "Filter by rating",
            options=rating_options,
            default=rating_options,
            help="Select ratings to display",
        )
        # Extract just the emoji from the selected ratings
        selected_ratings = [rating.split()[0] for rating in selected_ratings]

    # Filter events and resources
    filtered_events = [
        event
        for event in calendar_events
        if (
            # If "⚪" is selected, include unrated events
            ("⚪" in selected_ratings and event["title"].split()[0] not in RATING_INFO)
            or
            # Otherwise, only include events with selected ratings
            event["title"].split()[0] in selected_ratings
        )
    ]

    filtered_resources = [
        {"id": stage, "building": stage, "title": stage} for stage in selected_stages
    ]

    # Configure and render calendar
    calendar_options = get_calendar_options(filtered_events)
    calendar_options["resources"] = filtered_resources

    # Create a unique key based on the filters and current ratings state
    ratings_state = "-".join(
        f"{k}:{v}" for k, v in sorted(st.session_state.ratings.items())
    )
    calendar_key = f"calendar_view_{'-'.join(selected_ratings)}_{'-'.join(selected_stages)}_{ratings_state}"

    calendar_result = calendar(
        events=filtered_events,
        options=calendar_options,
        key=calendar_key,
        callbacks=["eventClick"],
    )

    # Handle event clicks
    if calendar_result and "eventClick" in calendar_result:
        st.session_state.clicked_event = calendar_result["eventClick"]["event"]

    # Display artist card if an event was clicked
    if st.session_state.clicked_event:
        handle_event_click(st.session_state.clicked_event, artists)


if __name__ == "__main__":
    main()
