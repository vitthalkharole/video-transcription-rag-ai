
import streamlit as st
from api_client import register_user


def render_signup():
    st.title("🎬 Create Your Account")
    st.write("Register to start using Video Transcription RAG AI.")

    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

    if submitted:
        if not username.strip() or not email.strip() or not password:
            st.warning("Please fill in all fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        else:
            try:
                result = register_user(
                    username.strip(),
                    email.strip(),
                    password
                )

                st.success("Account created successfully!")
                st.info("You can now log in with your credentials.")

                if st.button("Go to Login"):
                    st.session_state.page = "login"
                    st.rerun()

            except Exception as exc:
                st.error(f"Registration failed: {exc}")

    st.divider()

    if st.button("Already have an account? Login"):
        st.session_state.page = "login"
        st.rerun()
