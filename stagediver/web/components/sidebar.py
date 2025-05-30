import json
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
from ics import Calendar, Event

from stagediver.common import LINEUPS_FILE

# Constants
RATING_INFO = {
    "❤️": {"text": "Must see", "short_name": "heart", "bg_color": "#ff4b4b"},
    "🟢": {"text": "Yes", "short_name": "yes", "bg_color": "#177233"},
    "🟡": {"text": "Meh", "short_name": "meh", "bg_color": "#ffa421"},
    "🚫": {"text": "No", "short_name": "no", "bg_color": "#808080"},
}


@st.cache_data
def load_lineup_data():
    """Load the historical lineup data from JSON file"""
    try:
        with open(Path(LINEUPS_FILE)) as f:
            data = json.load(f)
        return data if isinstance(data, dict) and "artists" in data else {"artists": []}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Error loading lineup data: {e}")
        return {"artists": []}


def create_calendar_export(artists_data, ratings):
    """Create ICS calendar with rated artists"""
    cal = Calendar()

    for artist in artists_data["artists"]:
        # Skip artists that haven't been rated or that sucks
        if (
            artist["artist_name"] not in ratings
            or ratings[artist["artist_name"]] == "🚫"
        ):
            continue

        event = Event()
        event.name = f"{ratings[artist['artist_name']]} {artist['artist_name']}"
        event.begin = artist.get("start_ts") or datetime(
            artists_data["festival_year"], 7, 1, 13, 37
        )
        event.end = artist.get("end_ts") or event.begin + timedelta(hours=1)
        event.url = artist.get("scrape_url", "")
        event.location = artist.get("stage_name", "TBA")

        description = artist.get("bio_short", "")
        if spotify_url := artist.get("social_links", {}).get("spotify"):
            description += f"\n\n▶️: {spotify_url}"
        event.description = description

        cal.events.add(event)
    return cal


def export_ratings():
    """Export ratings data as JSON string"""
    export_data = {
        info["text"]: sorted(
            artist
            for artist, rating in st.session_state.ratings.items()
            if rating == emoji
        )
        for emoji, info in RATING_INFO.items()
    }
    export_data["timestamp"] = datetime.now().isoformat()
    return json.dumps(export_data, indent=2)


def import_ratings(json_str):
    """Import ratings data from JSON string"""
    try:
        data = json.loads(json_str)
        categories_to_emoji = {
            info["text"]: emoji for emoji, info in RATING_INFO.items()
        }
        new_ratings = {
            artist: emoji
            for category, emoji in categories_to_emoji.items()
            for artist in data.get(category, [])
        }

        if new_ratings != st.session_state.ratings:
            st.session_state.ratings = new_ratings
            return True
        return False
    except (json.JSONDecodeError, KeyError):
        return False


def get_festivals_and_years(data):
    """Extract unique festival/year combinations"""
    if festival_name := data.get("festival_name"):
        if festival_year := data.get("festival_year"):
            return [(festival_name, festival_year)]
    return []


def display_rating_stats(rating_counts, total_concerts, rated_concerts):
    """Display rating statistics in a proportional table format"""
    # Display stats text
    st.text(
        f"You've rated {rated_concerts} out of {total_concerts} concerts ({rated_concerts/total_concerts*100:.0f}%), spread across the following ratings:"
    )

    # Calculate percentages for each rating
    total_rated = sum(rating_counts.values())
    rating_percentages = {
        emoji: (count / total_rated * 100) if total_rated > 0 else 0
        for emoji, count in rating_counts.items()
    }

    # Filter out ratings with 0 count
    active_ratings = {
        emoji: (count, rating_percentages[emoji])
        for emoji, count in rating_counts.items()
        if count > 0
    }

    if active_ratings:
        st.markdown(
            f"""
            <style>
                .rating-table {{
                    width: 100%;
                }}
                .rating-table, .rating-table tr, .rating-table td {{
                    border: none !important;
                }}
                .rating-cell {{
                    padding: 8px;
                    text-align: center;
                    color: white;
                }}
                .rating-cell:first-child {{
                    border-top-left-radius: 0.5rem;
                    border-bottom-left-radius: 0.5rem;
                }}
                .rating-cell:last-child {{
                    border-top-right-radius: 0.5rem;
                    border-bottom-right-radius: 0.5rem;
                }}
                {''.join(
                    f'.rating-cell.{info["short_name"]} {{ background-color: {info["bg_color"]}; }}'
                    for info in RATING_INFO.values()
                )}
            </style>
            <table class="rating-table">
                <tr>
                    {''.join(
                        f'<td class="rating-cell {RATING_INFO[emoji]["short_name"]}" style="width: {percentage}%">'
                        f'{emoji}<br>{count}</td>'
                        for emoji, (count, percentage) in active_ratings.items()
                    )}
                </tr>
            </table>
            """,
            unsafe_allow_html=True,
        )


def show_sidebar(layout="centered"):
    """Display the shared sidebar content"""
    st.set_page_config(page_title="Stagediver", page_icon="🎸", layout=layout)

    # Initialize session states
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}
    if "show_import" not in st.session_state:
        st.session_state.show_import = True
    if "artists_data" not in st.session_state:
        st.session_state.artists_data = load_lineup_data()

    # Festival selection
    festival_years = get_festivals_and_years(st.session_state.artists_data)
    if festival_years:
        festival_year_options = [
            f"{festival} ({year})" for festival, year in festival_years
        ]
        if not st.session_state.get("selected_festival"):
            st.session_state.selected_festival, st.session_state.selected_year = (
                festival_years[0]
            )

        with st.sidebar:
            selected = st.selectbox(
                "Select Festival",
                options=festival_year_options,
                index=festival_year_options.index(
                    f"{st.session_state.selected_festival} ({st.session_state.selected_year})"
                ),
                key="festival_selector",
            )

            if selected:
                festival, year = selected.rsplit(" (", 1)
                st.session_state.selected_festival = festival
                st.session_state.selected_year = int(year.rstrip(")"))

            # Ratings import/export
            if st.session_state.show_import:
                if uploaded_file := st.file_uploader(
                    "📂 Load Ratings",
                    type=["json"],
                    help="Upload a previously saved ratings file",
                ):
                    if import_ratings(uploaded_file.read().decode()):
                        st.success("Ratings loaded successfully!")
                        st.session_state.show_import = False
                        st.session_state.pop("ratings_upload", None)
                        st.rerun()
                    else:
                        st.info("Ratings already up to date")
            else:
                if st.button("Import Different Ratings", type="tertiary", icon="📂"):
                    st.session_state.show_import = True
                    st.rerun()

            # Export options
            if st.session_state.ratings:
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
                    )
                with col2:
                    st.download_button(
                        label="Calendar",
                        icon="📅",
                        data=create_calendar_export(
                            st.session_state.artists_data, st.session_state.ratings
                        ).serialize(),
                        file_name="my_lineup.ics",
                        mime="text/calendar",
                        help="Download your lineup as calendar",
                        use_container_width=True,
                        type="tertiary",
                    )

                # Show rating statistics
                st.divider()

                # Get total concerts and rated count
                total_concerts = len(
                    [
                        a
                        for a in st.session_state.artists_data["artists"]
                        if a["artist_name"]
                    ]
                )
                rated_concerts = len(st.session_state.ratings)

                # Count each rating type
                rating_counts = {
                    emoji: len(
                        [r for r in st.session_state.ratings.values() if r == emoji]
                    )
                    for emoji in RATING_INFO
                }

                # Create proportional table for ratings
                if rating_counts:
                    display_rating_stats(rating_counts, total_concerts, rated_concerts)
