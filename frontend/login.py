import streamlit as st
from api_client import login_user


def render_login():
    st.markdown(
        """
        <style>
            #MainMenu, footer {visibility: hidden;}
            .block-container {padding-top: 4rem; max-width: 520px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Welcome back")
    st.caption("Log in to transcribe videos and chat with them.")

    notice = st.session_state.pop("auth_notice", None)
    if notice:
        st.success(notice)

    with st.container(border=True):
        with st.form("login_form", border=False):
            username = st.text_input("Username", placeholder="Your username")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input(
                "Password", type="password", placeholder="Your password"
            )
            submitted = st.form_submit_button(
                "Log in", type="primary", use_container_width=True
            )

        if submitted:
            username, email = username.strip(), email.strip()

            if not username or not email or not password:
                st.warning("Please fill in all fields.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            else:
                try:
                    with st.spinner("Signing you in..."):
                        result = login_user(username, password, email)

                    token = result.get("access_token")
                    if token:
                        st.session_state.token = token
                        st.session_state.page = "workspace"
                        st.rerun()
                    else:
                        st.error("Login failed: no access token was returned.")
                except Exception as exc:
                    st.error(f"Login failed: {exc}")

    left, right = st.columns([3, 2])
    left.caption("Don't have an account?")
    if right.button("Sign up", use_container_width=True):
        st.session_state.page = "signup"
        st.rerun()