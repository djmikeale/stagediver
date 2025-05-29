import re
from datetime import datetime

import pycountry
import streamlit as st

from stagediver.web.components.sidebar import RATING_INFO


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


def country_code_to_flag(country_code):
    """Convert a country code to a flag emoji using pycountry"""
    if not country_code:
        return ""
    try:
        # Map UK to GB
        if country_code.upper() == "UK":
            country_code = "GB"
        if country_code.upper() == "INT":
            country_code = "🌐"
        country = pycountry.countries.get(alpha_2=country_code.upper())
        return country.flag if country else country_code
    except (KeyError, AttributeError):
        return country_code


def display_artist_card(artist, blind_mode=False):
    """Display an artist card with optional rating controls and blind mode"""
    name = artist["artist_name"]

    # Artist info - only show if not in blind mode
    if not blind_mode:

        if stage := artist.get("stage_name"):
            text = f"{stage}"
            if start_ts := artist.get("start_ts"):
                start_time = datetime.fromisoformat(start_ts)
                text += f" • {start_time.strftime('%A, %-d %B, %H:%M')}"

            # Convert country codes to flags
            country_flags = " ".join(
                country_code_to_flag(code) for code in artist.get("country_code", [])
            )
            st.markdown(f"### {country_flags} {name} :gray[&nbsp;&nbsp;{text}] ")

        if artist.get("scrape_url"):
            subheader = f"[🌐]({artist['scrape_url']})"

        if artist.get("social_links", {}).get("spotify"):
            subheader += f"&nbsp;&nbsp;[▶️]({artist['social_links']['spotify']})"

        if artist.get("bio_short"):
            subheader += f"&nbsp;&nbsp;*{artist['bio_short']}*"

        st.markdown(f"{subheader}")

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
    rating_options = [f"{emoji} {info['text']}" for emoji, info in RATING_INFO.items()]

    # Find current rating option or default to None
    default = None
    if current_rating:
        default = f"{current_rating} {RATING_INFO[current_rating]['text']}"

    rating = st.segmented_control(
        "Rating",
        label_visibility="collapsed",
        options=rating_options,
        default=default,
        key=f"rating_{name}",
    )

    if rating:
        emoji = rating.split(" ")[0]
        st.session_state.ratings[name] = emoji
    elif name in st.session_state.ratings:
        del st.session_state.ratings[name]

    if artist.get("bio_long") and not blind_mode:
        st.divider()
        with st.expander(f"Read more about {name}"):
            st.markdown(
                artist["bio_long"].replace("\n", "<br><br>"),
                unsafe_allow_html=True,
            )

    return rating
