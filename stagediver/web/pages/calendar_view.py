from datetime import datetime, timedelta

import streamlit as st
from streamlit_calendar import calendar


def show_calendar_view(artists_data, ratings):
    """Display rated artists in a calendar view"""
    # Filter out unrated artists and those marked as "No"
    rated_artists = [
        artist
        for artist in artists_data
        if artist["artist_name"] in ratings and ratings[artist["artist_name"]] != "🚫"
    ]

    # Create calendar events from rated artists
    calendar_events = []
    for artist in rated_artists:
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

        event = {
            "title": f"{ratings[artist['artist_name']]} {artist['artist_name']}",
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "resourceId": artist.get("stage_name", "TBA"),
            "description": artist.get("bio_short", ""),
            "url": artist.get("scrape_url", ""),
        }
        calendar_events.append(event)

    # Get unique stages for resources
    stages = sorted(set(event["resourceId"] for event in calendar_events))
    resources = [{"id": stage, "building": stage, "title": stage} for stage in stages]

    calendar_options = {
        "editable": False,
        "selectable": True,
        "initialDate": (
            calendar_events[0]["start"].split("T")[0]
            if calendar_events
            else datetime.now().strftime("%Y-%m-%d")
        ),
        "initialView": "resourceTimeGridDay",
        "slotMinTime": "00:00:00",
        "slotMaxTime": "23:59:59",
        "resourceGroupField": "building",
        "resources": resources,
    }

    calendar_data = calendar(
        events=calendar_events,
        options=calendar_options,
    )

    # Handle calendar event clicks
    if calendar_data and "clicked" in calendar_data:
        clicked_event = calendar_data["clicked"]
        if clicked_event and "url" in clicked_event:
            st.markdown(f"[Open artist page]({clicked_event['url']})")
