import streamlit as st
from api_client import register_user

MIN_PASSWORD_LENGTH = 8


def render_signup():
    st.markdown(
        """
        <style>
            #MainMenu, footer {visibility: hidden;}
            .block-container {padding-top: 4rem; max-width: 520px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Create your account")
    st.caption("Sign up to get started with Video RAG AI.")

    with st.container(border=True):
        with st.form("signup_form", border=False):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input(
                "Password",
                type="password",
                placeholder=f"At least {MIN_PASSWORD_LENGTH} characters",
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Re-enter your password",
            )
            submitted = st.form_submit_button(
                "Create account", type="primary", use_container_width=True
            )

        if submitted:
            username, email = username.strip(), email.strip()

            if not username or not email or not password:
                st.warning("Please fill in all fields.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            elif len(password) < MIN_PASSWORD_LENGTH:
                st.error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    with st.spinner("Creating your account..."):
                        register_user(username, email, password)
                    st.session_state.auth_notice = (
                        "Account created successfully. Please log in."
                    )
                    st.session_state.page = "login"
                    st.rerun()
                except Exception as exc:
                    st.error(f"Registration failed: {exc}")

    left, right = st.columns([3, 2])
    left.caption("Already have an account?")
    if right.button("Log in", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()