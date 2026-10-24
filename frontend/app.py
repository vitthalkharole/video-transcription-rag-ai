
import streamlit as st

from utils.session import initialize_session, is_logged_in, logout
from login import render_login
from signup import render_signup
from workspace import render_workspace


st.set_page_config(
    page_title="Video Transcription RAG AI",
    page_icon="🎬",
    layout="wide"
)

initialize_session()


def main():
    if is_logged_in():
        render_workspace()

    else:
        current_page = st.session_state.get("page", "login")

        if current_page == "signup":
            render_signup()
        else:
            render_login()


if __name__ == "__main__":
    main()
