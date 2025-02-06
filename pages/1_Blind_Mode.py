import streamlit as st

st.title("Blind Mode Test")

st.components.v1.html(
    """
    <style>
        .container {
            position: relative;
            width: 100%;
            height: 152px;
        }

        .overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;  /* Cover left 75% */
            height: 70%;  /* Cover top 75% */
            background: rgb(14, 17, 23);
            z-index: 1;
        }

        .overlay-right {
            position: absolute;
            top: 0;
            left: 0;
            width: 93%;  /* Cover left 75% */
            height: 100%;  /* Cover top 75% */
            background: rgb(14, 17, 23);
            z-index: 1;
        }

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
        <div class="overlay-right"></div>
    </div>
    """,
    height=170
)

st.write("Bottom right quarter of the widget should be visible")


#<iframe style="border-radius:12px" src="https://open.spotify.com/embed/album/11H3JkQiYm6ydXZuDWs4RO?utm_source=generator&theme=0" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
