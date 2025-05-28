import re
from datetime import datetime

import streamlit as st


def extract_spotify_id(spotify_url):
    """Extract Spotify artist ID from full URL"""
    if not spotify_url:
        return None
    match = re.search(r"artist/([a-zA-Z0-9]+)", spotify_url)
    return match.group(1) if match else None


def create_spotify_player_with_overlay(spotify_id, visible=True):
    """Create a Spotify player with an overlay"""
    st.components.v1.html(
        f"""
        <style>
            .player-container {{
                position: relative;
                width: 100%;
                height: 152px;
                border-radius: 12px;
                overflow: hidden;
            }}
            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: calc(100% - 45px);
                height: 100%;
                backdrop-filter: blur(6px);
                opacity: {1 if visible else 0};
                pointer-events: none;
                transition: opacity 0.3s ease;
                z-index: 1000;
            }}
        </style>
        <div class="player-container">
            <iframe src="https://open.spotify.com/embed/artist/{spotify_id}"
                    width="100%"
                    height="152"
                    frameBorder="0"
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                    loading="lazy">
            </iframe>
            <div class="overlay"></div>
        </div>
        """,
        height=170,
    )


def display_artist_card(artist, blind_mode=False):
    """Display an artist card with optional rating controls and blind mode"""
    from stagediver.web.components.sidebar import RATING_EMOJIS

    name = artist["artist_name"]

    # Artist info - only show if not in blind mode
    if not blind_mode:
        st.markdown(f"### {name}")

        if stage := artist.get("stage_name"):
            text = f"{stage}"
            if start_ts := artist.get("start_ts"):
                start_time = datetime.fromisoformat(start_ts)
                text += f" • {start_time.strftime('%A, %-d %B, %H:%M')}"
            st.markdown(f":gray[{text}]")

        if artist.get("bio_short"):
            if artist.get("bio_long"):  # Show short bio as expander title
                with st.expander(f"{artist['bio_short']} *:gray[click to read more]*"):
                    st.markdown(
                        artist["bio_long"].replace("\n", "<br><br>"),
                        unsafe_allow_html=True,
                    )
            else:  # Only short bio available
                st.markdown(f"*{artist['bio_short']}*")

    else:
        # In blind mode, show a placeholder title
        st.markdown("### 🎵 Mystery Artist")

    # Spotify embed with optional overlay
    if spotify_url := artist.get("social_links", {}).get("spotify"):
        if spotify_id := extract_spotify_id(spotify_url):
            create_spotify_player_with_overlay(
                spotify_id=spotify_id, visible=blind_mode
            )

    # Rating buttons
    current_rating = st.session_state.ratings.get(name, "")

    # Create options list for segmented control
    rating_options = [f"{emoji} {label}" for emoji, label in RATING_EMOJIS.items()]

    # Find current rating option or default to None
    default = None
    if current_rating:
        default = f"{current_rating} {RATING_EMOJIS[current_rating]}"

    selected = st.segmented_control(
        label="Rate this artist:",
        options=rating_options,
        key=f"rate_{name}",
        default=default,
    )

    return selected
