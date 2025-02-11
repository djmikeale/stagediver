import streamlit as st
from stagediver.web.components.sidebar import show_sidebar

def main():
    # Show shared sidebar
    show_sidebar()

    st.title("Share Your Lineup")
    # ... rest of the existing content ...

if __name__ == "__main__":
    main()
