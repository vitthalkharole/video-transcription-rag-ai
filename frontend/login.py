

import streamlit as st
from api_client import login_user


def render_login():
    st.title("🎬 Video Transcription RAG AI")
    st.subheader("Welcome Back!")
    st.write(
        "Login to transcribe videos and chat with their content."
    )

    with st.form("login_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if submitted:
        if not username.strip() or not email.strip() or not password:
            st.warning("Please fill in all fields.")
        else:
            try:
                result = login_user(
                    username.strip(),
                    password,
                    email.strip()
                )

                token = result.get("access_token")

                if token:
                    st.session_state.token = token
                    st.session_state.page = "workspace"
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(
                        "Login failed: access token was not returned."
                    )

            except Exception as exc:
                st.error(f"Login failed: {exc}")

    st.divider()
    st.write("Don't have an account?")

    if st.button("Create an account"):
        st.session_state.page = "signup"
        st.rerun()

