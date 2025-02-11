import streamlit as st
from datetime import datetime, timedelta
import json
from ics import Calendar, Event
from pathlib import Path
from stagediver.common.config import HISTORICAL_FILE

# Constants
RATING_EMOJIS = {
    "❤️": "Must see",
    "🟢": "Good",
    "🟡": "Meh",
    "🚫": "Skip"
}

@st.cache_data
def load_lineup_data():
    """Load the historical lineup data from JSON file"""
    data_path = Path(HISTORICAL_FILE)
    try:
        with open(data_path) as f:
            data = json.load(f)
        if not isinstance(data, list):
            st.error(f"Invalid data format in {HISTORICAL_FILE}. Expected a list but got {type(data)}")
            return []
        return data
    except FileNotFoundError:
        st.error(f"Lineup data file not found: {HISTORICAL_FILE}")
        return []
    except json.JSONDecodeError:
        st.error(f"Invalid JSON in lineup data file: {HISTORICAL_FILE}")
        return []

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

def get_festivals_and_years(data):
    """Extract unique festival/year combinations"""
    festival_years = set()
    for artist in data:
        festival_years.add((artist["festival_name"], artist["festival_year"]))
    return sorted(festival_years, key=lambda x: (-x[1], x[0]))  # Sort by year desc, then festival name

def show_sidebar(layout="centered"):
    """Display the shared sidebar content"""
    st.set_page_config(
        page_title="Stagediver",
        page_icon="🎪",
        layout=layout,
    )

    # Initialize session states
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}
    if "show_import" not in st.session_state:
        st.session_state.show_import = True

    # Load and store artists data in session state
    if "artists_data" not in st.session_state:
        st.session_state.artists_data = load_lineup_data()

    # Initialize festival selection with first available option if not set
    festival_years = get_festivals_and_years(st.session_state.artists_data)
    festival_year_options = [f"{festival} ({year})" for festival, year in festival_years]

    if not st.session_state.get("selected_festival") and festival_year_options:
        # Set initial selection to first available option
        first_festival, first_year = festival_years[0]
        st.session_state.selected_festival = first_festival
        st.session_state.selected_year = first_year

    with st.sidebar:
        if festival_year_options:
            # Find current selection index
            current_selection = f"{st.session_state.selected_festival} ({st.session_state.selected_year})"
            current_index = festival_year_options.index(current_selection) if current_selection in festival_year_options else 0

            selected_festival_year = st.selectbox(
                "Select Festival",
                options=festival_year_options,
                index=current_index,
                key="festival_selector"
            )

            # Update session state when selection changes
            if selected_festival_year:
                festival, year_str = selected_festival_year.rsplit(" (", 1)
                year = int(year_str.rstrip(")"))
                st.session_state.selected_festival = festival
                st.session_state.selected_year = year

        # Show either the import button or file uploader
        if st.session_state.show_import:
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
                    st.session_state.show_import = False  # Hide the uploader after successful import
                    # Clear the file uploader state
                    st.session_state.pop('ratings_upload', None)
                    st.rerun()
                else:
                    st.info("Ratings already up to date")
        else:
            if st.button("Import Different Ratings", type="tertiary",icon="📂"):
                st.session_state.show_import = True
                st.rerun()

        # Only show download buttons if there are ratings
        if len(st.session_state.ratings) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Save Ratings",
                    icon="💾",
                    data=export_ratings(),
                    file_name="festival_ratings.json",
                    mime="application/json",
                    help="Download your ratings to a file",
                    use_container_width=True,
                    type="tertiary",
                    args=dict(style="text-align: left;"),
                )

            with col2:
                cal = create_calendar_export(st.session_state.artists_data, st.session_state.ratings)
                st.download_button(
                    label="Calendar",
                    icon="📅",
                    data=cal.serialize(),
                    file_name="my_lineup.ics",
                    mime="text/calendar",
                    help="Download your lineup as calendar",
                    use_container_width=True,
                    type="tertiary",
                    args=dict(style="text-align: left;"),
                )
