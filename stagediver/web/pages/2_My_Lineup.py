import streamlit as st

def main():
    st.title("My Festival Lineup")

    st.info("""
    This page will show:
    - Your rated artists
    - Schedule view
    - Conflicts checker
    - Export options (calendar, playlist)
    """)

    st.write("🚧 Under construction 🚧")

    st.title("Blind Mode Test")

    # Add state management for the overlay visibility
    if 'overlay_visible' not in st.session_state:
        st.session_state.overlay_visible = True

    # Button to toggle overlay
    if st.button('Reveal' if st.session_state.overlay_visible else 'Hide'):
        st.session_state.overlay_visible = not st.session_state.overlay_visible

    # HTML component with dynamic overlay visibility
    st.components.v1.html(
        f"""
        <style>
            .container {{
                position: relative;
                width: 100%;
                height: 152px;
            }}

            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: calc(100% - 50px);
                height: 100%;
                background: rgb(14, 17, 23);
                z-index: 1;
                opacity: {1 if st.session_state.overlay_visible else 0};
                pointer-events: {'' if st.session_state.overlay_visible else 'none'};
                transition: opacity 0.3s ease;
            }}
        </style>

        <div class="container">
            <iframe id="spotify-player"
                    src="https://open.spotify.com/embed/album/11H3JkQiYm6ydXZuDWs4RO"
                    width="100%"
                    height="152"
                    frameBorder="0"
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                    loading="lazy">
            </iframe>
            <div class="overlay"></div>
        </div>
        """,
        height=170
    )

    st.write("Bottom right quarter of the widget should be visible")

if __name__ == "__main__":
    main()
