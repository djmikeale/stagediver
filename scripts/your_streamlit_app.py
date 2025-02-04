import streamlit as st
from ics import Calendar, Event
from datetime import datetime
import pytz
from stagediver.common.config import LINEUPS_FILE
from stagediver.common.utils import load_json_file

#todo the streamlit app will have data visualization functionality, user rating functionality, and calendar download functionality.

st.title("Roskilde Festival 2025 Calendar")

# Load the lineup data using the utility function
lineups = load_json_file(LINEUPS_FILE)

# Extract artist names from the first festival (assuming one festival in the JSON)
festival = lineups[0]
artists = festival["artists"]
artist_names = sorted([artist["artist_name"] for artist in artists])

# Create tabs for different views
tab1, tab2 = st.tabs(["Add to Calendar", "View Full Lineup"])

with tab1:
    # Create a dropdown to select an artist
    selected_artist_name = st.selectbox(
        "Select a concert to add to your calendar",
        artist_names
    )

    # Find the selected artist's data
    selected_artist = next(
        (artist for artist in artists if artist["artist_name"] == selected_artist_name),
        None
    )

    if selected_artist:
        # Display artist info
        st.write(f"**Stage:** {selected_artist['stage_name'] or 'TBA'}")
        st.write(f"**Description:** {selected_artist['bio_short']}")

        # Create calendar event
        def create_ics_file(artist):
            c = Calendar()
            e = Event()
            e.name = f"{artist['artist_name']} at {festival['festival_name']}"
            e.description = artist['bio_short']

            # Since we don't have exact times, we'll set it to a placeholder date
            festival_year = festival['festival_year']
            e.begin = datetime(festival_year, 7, 1, 12, 0, tzinfo=pytz.UTC)  # Example date
            e.end = datetime(festival_year, 7, 1, 13, 30, tzinfo=pytz.UTC)   # Example end time

            if artist['stage_name']:
                e.location = f"{artist['stage_name']}, {festival['festival_name']}"
            else:
                e.location = festival['festival_name']

            c.events.add(e)
            return c

        # Generate ICS file when button is clicked
        if st.download_button(
            label="Add to Calendar",
            data=str(create_ics_file(selected_artist)),
            file_name=f"{selected_artist['artist_name']}_concert.ics",
            mime="text/calendar"
        ):
            st.success("Calendar file generated! Check your downloads.")

with tab2:
    # Display full lineup
    st.write("### Full Lineup")
    for artist in sorted(artists, key=lambda x: x['artist_name']):
        st.write(f"**{artist['artist_name']}**")
        if artist['stage_name']:
            st.write(f"*Stage:* {artist['stage_name']}")
        st.write(artist['bio_short'])
        st.write("---")
