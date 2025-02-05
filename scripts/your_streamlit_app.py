import streamlit as st
import json
from pathlib import Path
from ics import Calendar, Event
from datetime import datetime, timedelta
import re

# Constants
RATING_EMOJIS = {
    "❤️": "Must see",
    "🟢": "Want to see",
    "🟡": "Maybe",
    "🚫": "Skip"
}

ARTISTS_PER_PAGE = 5

def extract_spotify_id(spotify_url):
    """Extract Spotify artist ID from full URL"""
    if not spotify_url:
        return None
    match = re.search(r'artist/([a-zA-Z0-9]+)', spotify_url)
    return match.group(1) if match else None

def spotify_embed(artist_id):
    """Generate Spotify embed HTML for an artist"""
    return f"""
        <iframe style="border-radius:12px"
                src="https://open.spotify.com/embed/artist/{artist_id}?utm_source=generator"
                width="100%"
                height="152"
                frameBorder="0"
                allowfullscreen=""
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy">
        </iframe>
    """

def load_lineup_data():
    """Load the historical lineup data from JSON file"""
    data_path = Path("data/lineups_historical.json")
    with open(data_path) as f:
        return json.load(f)

def get_festivals_and_years(data):
    """Extract unique festival/year combinations"""
    festival_years = set()
    for artist in data:
        festival_years.add((artist["festival_name"], artist["festival_year"]))
    return sorted(festival_years, key=lambda x: (-x[1], x[0]))  # Sort by year desc, then festival name

def get_artists_for_festival_year(data, festival, year):
    """Get all artists for a specific festival and year"""
    return [
        artist for artist in data
        if artist["festival_name"] == festival
        and artist["festival_year"] == year
    ]

def create_calendar_export(artists_data, ratings):
    """Create ICS calendar with rated artists"""
    cal = Calendar()

    # Only include artists with positive ratings
    valid_ratings = ["❤️", "🟢", "🟡"]
    rated_artists = [
        artist for artist in artists_data
        if ratings.get(artist["artist_name"]) in valid_ratings
    ]

    for artist in rated_artists:
        event = Event()
        event.name = f"{artist['artist_name']} {ratings[artist['artist_name']]}"

        # If we have actual start/end times, use those
        if artist["start_ts"] and artist["end_ts"]:
            event.begin = artist["start_ts"]
            event.end = artist["end_ts"]
        else:
            # Placeholder times if not available
            event.begin = datetime(artist["festival_year"], 7, 1, 12, 0)  # Noon on July 1st
            event.end = event.begin + timedelta(hours=1)

        event.description = artist.get("bio_short", "")
        event.location = artist.get("stage_name", "TBA")
        cal.events.add(event)

    return cal

def export_ratings():
    """Export ratings data as JSON string"""
    # Initialize categories from RATING_EMOJIS
    export_data = {
        label: [] for label in RATING_EMOJIS.values()
    }
    export_data["timestamp"] = datetime.now().isoformat()

    # Group artists by rating category
    for artist, rating in st.session_state.ratings.items():
        category = RATING_EMOJIS.get(rating)
        if category:
            export_data[category].append(artist)

    # Sort artist lists alphabetically
    for category in RATING_EMOJIS.values():
        export_data[category].sort()

    return json.dumps(export_data, indent=2)

def import_ratings(json_str):
    """Import ratings data from JSON string"""
    try:
        data = json.loads(json_str)

        # Create reverse mapping (category -> emoji)
        categories_to_emoji = {v: k for k, v in RATING_EMOJIS.items()}

        # Create new ratings dictionary
        new_ratings = {}
        for category, emoji in categories_to_emoji.items():
            if category in data:
                for artist in data[category]:
                    new_ratings[artist] = emoji

        # Check if ratings are different before updating
        if new_ratings != st.session_state.ratings:
            st.session_state.ratings = new_ratings
            return True
        return False

    except (json.JSONDecodeError, KeyError):
        return False

def main():
    st.title("Festival Lineup Rater")

    # Load data
    data = load_lineup_data()
    festival_years = get_festivals_and_years(data)

    # Combined festival and year selection
    festival_year_options = [f"{festival} ({year})" for festival, year in festival_years]
    selected_festival_year = st.selectbox(
        "Select Festival",
        options=festival_year_options
    )

    # Extract festival and year from selection
    selected_festival, year_str = selected_festival_year.rsplit(" (", 1)
    selected_year = int(year_str.rstrip(")"))

    # Get artists for selected festival/year
    artists = get_artists_for_festival_year(data, selected_festival, selected_year)

    # Initialize session state for ratings if not exists
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}

    # Pagination
    total_pages = (len(artists) + ARTISTS_PER_PAGE - 1) // ARTISTS_PER_PAGE

    # Initialize page in session state if not exists
    if "page" not in st.session_state:
        st.session_state.page = 1

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        # Use session state page as the default value
        page = st.number_input(
            f"Page (1-{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.page,
            key="page_input"
        )
        # Keep page state in sync with number input
        st.session_state.page = page

    start_idx = (page - 1) * ARTISTS_PER_PAGE
    end_idx = min(start_idx + ARTISTS_PER_PAGE, len(artists))

    st.subheader(f"Rate Artists (Showing {start_idx + 1}-{end_idx} of {len(artists)})")

    # Display artists for current page
    for artist in artists[start_idx:end_idx]:
        name = artist["artist_name"]

        # Artist info
        st.markdown(f"### {name}")
        if artist.get("bio_short"):
            st.markdown(f"*{artist['bio_short']}*")
        if artist.get("stage_name"):
            st.markdown(f"**Stage:** {artist['stage_name']}")

        # Spotify embed
        if artist.get("social_links", {}).get("spotify"):
            spotify_id = extract_spotify_id(artist["social_links"]["spotify"])
            if spotify_id:
                st.components.v1.html(
                    spotify_embed(spotify_id),
                    height=170
                )

        # Rating buttons
        st.write("Rate this artist:")
        cols = st.columns(len(RATING_EMOJIS))
        current_rating = st.session_state.ratings.get(name, "")

        for emoji, (col, label) in zip(RATING_EMOJIS.keys(), enumerate(RATING_EMOJIS.values())):
            with cols[col]:
                button_type = "primary" if current_rating == emoji else "secondary"
                if st.button(
                    label,
                    icon=emoji,
                    key=f"rate_{name}_{emoji}",
                    type=button_type,
                    use_container_width=True
                ):
                    # If clicking the same rating again, remove it
                    if current_rating == emoji:
                        del st.session_state.ratings[name]
                    else:
                        st.session_state.ratings[name] = emoji
                    st.rerun()

        st.markdown("---")  # Add separator between artists

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if page > 1:
            if st.button("« previous", key=f"prev_page_{page}"):
                st.session_state.page -= 1
                st.rerun()
    with col2:
        if page < total_pages:
            if st.button("Next »", key=f"next_page_{page}"):
                st.session_state.page += 1
                st.rerun()

    # Save/Load buttons
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Save Progress",
            icon="💾",
            data=export_ratings(),
            file_name="festival_ratings.json",
            mime="application/json",
            help="Download your ratings to a file",
        )

    with col2:
        uploaded_file = st.file_uploader(
            "Load Progress",
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

    # Export calendar button (moved after save/load)
    st.download_button(
        label="Export Calendar",
        icon="📆",
        data=str(create_calendar_export(artists, st.session_state.ratings)),
        file_name=f"{selected_festival}_{selected_year}_lineup.ics",
        mime="text/calendar",
        help="Download your schedule as a calendar file",
    )

    st.markdown("---")

    # Display current ratings summary
    st.subheader("Your Ratings Summary")
    for emoji, label in RATING_EMOJIS.items():
        rated_artists = [
            name for name, rating in st.session_state.ratings.items()
            if rating == emoji
        ]
        if rated_artists:
            st.markdown(f"**{emoji} {label}:**")
            st.markdown("- " + "\n- ".join(rated_artists))

if __name__ == "__main__":
    main()
