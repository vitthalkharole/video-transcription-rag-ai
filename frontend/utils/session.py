
import streamlit as st


def initialize_session():
    """Initialize the frontend session variables."""

    defaults = {
        "token": None,
        "page": "login",
        "video": None,
        "active_chat_id": None,
        "active_chat_video_id": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_logged_in():
    """Check whether the user has a login token."""
    return bool(st.session_state.get("token"))


def logout():
    """Clear login and current workspace data."""
    st.session_state.token = None
    st.session_state.page = "login"
    st.session_state.video = None
    st.session_state.active_chat_id = None
    st.session_state.active_chat_video_id = None
