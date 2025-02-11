import streamlit as st
from datetime import datetime, timedelta
import json
from ics import Calendar, Event

# Constants
RATING_EMOJIS = {
    "❤️": "Must see",
    "🟢": "Good",
    "🟡": "Meh",
    "🚫": "Skip"
}

def create_calendar_export(artists_data, ratings):
    """Create ICS calendar with rated artists"""
    cal = Calendar()
    valid_ratings = ["❤️", "🟢", "🟡"]
    rated_artists = [
        artist for artist in artists_data
        if ratings.get(artist["artist_name"]) in valid_ratings
    ]

    for artist in rated_artists:
        event = Event()
        event.name = f"{ratings[artist['artist_name']]} {artist['artist_name']}"

        if artist["start_ts"] and artist["end_ts"]:
            event.begin = artist["start_ts"]
            event.end = artist["end_ts"]
        else:
            event.begin = datetime(artist["festival_year"], 7, 1, 12, 0)
            event.end = event.begin + timedelta(hours=1)

        event.url = artist.get("scrape_url", "")
        description = artist.get("bio_short", "")
        if artist.get("social_links", {}).get("spotify"):
            description += f"\n\n▶️: {artist['social_links']['spotify']}"
        event.description = description
        event.location = artist.get("stage_name", "TBA")
        cal.events.add(event)

    return cal

def export_ratings():
    """Export ratings data as JSON string"""
    export_data = {label: [] for label in RATING_EMOJIS.values()}
    export_data["timestamp"] = datetime.now().isoformat()

    for artist, rating in st.session_state.ratings.items():
        category = RATING_EMOJIS.get(rating)
        if category:
            export_data[category].append(artist)

    for category in RATING_EMOJIS.values():
        export_data[category].sort()

    return json.dumps(export_data, indent=2)

def import_ratings(json_str):
    """Import ratings data from JSON string"""
    try:
        data = json.loads(json_str)
        categories_to_emoji = {v: k for k, v in RATING_EMOJIS.items()}
        new_ratings = {}

        for category, emoji in categories_to_emoji.items():
            if category in data:
                for artist in data[category]:
                    new_ratings[artist] = emoji

        if new_ratings != st.session_state.ratings:
            st.session_state.ratings = new_ratings
            return True
        return False

    except (json.JSONDecodeError, KeyError):
        return False

def show_sidebar(artists_data=None):

    st.set_page_config(
        page_title="Stagediver",
        page_icon="🎪",
    )

    """Display the shared sidebar content"""
    # Initialize session state for ratings and artists_data if not exists
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}
    if "artists_data" not in st.session_state:
        st.session_state.artists_data = artists_data

    # Use artists_data from session state if not provided directly
    artists_data = artists_data or st.session_state.get("artists_data")

    with st.sidebar:
        st.subheader("Save/Load Progress")


        uploaded_file = st.file_uploader(
            "📂 Load Ratings",
            type=["json"],
            help="Upload a previously saved ratings file",
            accept_multiple_files=False,
            key="ratings_upload"
        )
        if uploaded_file:
            content = uploaded_file.read().decode()
            if import_ratings(content):
                st.success("Ratings loaded successfully!")
                st.rerun()
            else:
                st.info("Ratings already up to date")


        # Only show download buttons if there are ratings
        if len(st.session_state.ratings) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="💾 Save Ratings",
                    data=export_ratings(),
                    file_name="festival_ratings.json",
                    mime="application/json",
                    help="Download your ratings to a file",
                    use_container_width=True,
                    type="tertiary",
                    args=dict(style="text-align: left;"),
                )

            with col2:
                if artists_data:
                    cal = create_calendar_export(artists_data, st.session_state.ratings)
                    st.download_button(
                        label="📅 Calendar",
                        data=str(cal),
                        file_name="my_lineup.ics",
                        mime="text/calendar",
                        help="Download your lineup as calendar",
                        use_container_width=True,
                        type="tertiary",
                        args=dict(style="text-align: left;"),
                    )
                else:
                    st.info("Artist data not available for calendar export")
        else:
            st.info("Rate some artists to enable export options")
