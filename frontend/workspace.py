"""Video RAG AI - simple Streamlit workspace."""
from html import escape

import streamlit as st

from api_client import (
    process_video,
    create_chat,
    send_chat_message,
    get_all_user_chats,
    get_chat_details,
    delete_chat,
)

# --------------------------------------------------
# STYLING (kept small and simple)
# --------------------------------------------------
CSS = """
<style>
.block-container { max-width: 900px; padding: 2.5rem 1.5rem 4rem 1.5rem; }

[data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,0.25); }
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

.stButton > button {
    border-radius: 10px;
    padding: 0.5rem 0.9rem;
    text-align: left;
}

[data-testid="stChatMessage"] {
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

.card {
    border: 1px solid rgba(128,128,128,0.3);
    border-left: 4px solid #7c6cff;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0 1.2rem 0;
    background: rgba(124,108,255,0.07);
}
.card-label { font-size: 0.7rem; letter-spacing: 1px; opacity: 0.7; margin-bottom: 0.3rem; }
.card-title { font-size: 1rem; font-weight: 600; overflow-wrap: anywhere; }

.hero { text-align: center; padding: 3rem 1rem 1.5rem 1rem; }
.hero h1 { font-size: 2.2rem; margin-bottom: 0.6rem; }
.hero p { opacity: 0.75; max-width: 560px; margin: 0 auto; line-height: 1.7; }
</style>
"""


# --------------------------------------------------
# SMALL HELPERS
# --------------------------------------------------
def safe(value):
    """Escape text before placing it inside HTML."""
    return escape(str(value))


def get_id(item):
    """Return the 'id' of a video or chat dict (API may call it id or xxx_id)."""
    if isinstance(item, dict):
        return item.get("id") or item.get("chat_id") or item.get("video_id")
    return None


def to_text(value):
    """Turn an API value (string or dict) into plain text."""
    if value is None:
        return ""
    if isinstance(value, dict):
        for key in ("content", "text", "message", "answer"):
            if value.get(key) is not None:
                return str(value[key])
    return str(value)


def get_chat_list(response):
    """The API may return a list or a dict that contains the list."""
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        for key in ("chats", "items", "results", "data"):
            if isinstance(response.get(key), list):
                return response[key]
    return []


def get_role(message):
    role = str(message.get("role") or message.get("sender") or "assistant").lower()
    return "user" if role in ("user", "human") else "assistant"


def get_content(message):
    for key in ("content", "message", "text", "question", "answer"):
        if message.get(key) is not None:
            return to_text(message[key])
    return ""


def reset_chat():
    st.session_state.active_chat_id = None
    st.session_state.chat_video_id = None
    st.session_state.chat_messages = []
    st.session_state.loaded_chat_id = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
def show_sidebar(token):
    with st.sidebar:
        st.markdown("## ▶ Video RAG AI")
        st.caption("Understand every video")

        if st.button("＋ New chat", type="primary", use_container_width=True):
            reset_chat()
            st.rerun()

        if st.button("＋ Process a video", use_container_width=True):
            reset_chat()
            st.session_state.show_video_form = True
            st.rerun()

        st.divider()
        st.markdown("**Your chats**")
        search = st.text_input(
            "Search chats",
            placeholder="Search your chats...",
            label_visibility="collapsed",
        )

        try:
            chats = get_chat_list(get_all_user_chats(token))
        except Exception as error:
            st.caption(f"Could not load chats: {error}")
            chats = []

        search = search.strip().lower()
        if search:
            chats = [
                c for c in chats
                if isinstance(c, dict) and search in str(c.get("title", "")).lower()
            ]

        if not chats:
            st.caption("No conversations found.")

        for chat in chats:
            chat_id = get_id(chat)
            if chat_id is None:
                continue

            title = chat.get("title") or f"Conversation {chat_id}"
            is_active = str(st.session_state.active_chat_id) == str(chat_id)

            col_open, col_delete = st.columns([5, 1])
            with col_open:
                label = f"{'● ' if is_active else ''}{title}"
                if st.button(label, key=f"open_{chat_id}", use_container_width=True, help=title):
                    st.session_state.active_chat_id = chat_id
                    st.session_state.chat_video_id = chat.get("video_id")
                    st.session_state.chat_messages = []
                    st.session_state.loaded_chat_id = None
                    st.rerun()
            with col_delete:
                if st.button("🗑", key=f"delete_{chat_id}", help="Delete chat"):
                    try:
                        delete_chat(chat_id, token)
                        if is_active:
                            reset_chat()
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not delete chat: {error}")

        st.divider()
        if st.button("Log out", use_container_width=True):
            from utils.session import logout
            logout()
            st.rerun()


# --------------------------------------------------
# VIDEO FORM
# --------------------------------------------------
def show_video_form(token):
    no_context = not st.session_state.video and st.session_state.active_chat_id is None
    expanded = st.session_state.show_video_form or no_context

    with st.expander("🎬 Add or process a video", expanded=expanded):
        with st.form("video_form"):
            url = st.text_input("Video URL", placeholder="Paste a supported YouTube video URL...")
            submitted = st.form_submit_button(
                "Process video", type="primary", use_container_width=True
            )

    if not submitted:
        return

    if not url.strip():
        st.warning("Paste a video URL to continue.")
        return

    try:
        with st.spinner("Processing video and preparing the transcript..."):
            result = process_video(url.strip(), token)
    except Exception as error:
        st.error(f"Video processing failed: {error}")
        return

    if not isinstance(result, dict):
        st.error("The video API returned an unexpected response.")
        return

    st.session_state.video = result
    st.session_state.show_video_form = False
    reset_chat()
    st.rerun()


# --------------------------------------------------
# WELCOME SCREEN
# --------------------------------------------------
def show_welcome():
    st.markdown(
        """
        <div class="hero">
            <h1>✦ What video are we exploring today?</h1>
            <p>Process a video, explore its transcript, and ask questions
               in a natural conversation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.markdown("**📝 Transcribe**")
    col1.caption("Turn your video into searchable text.")
    col2.markdown("**🔎 Understand**")
    col2.caption("Find key ideas without rewatching.")
    col3.markdown("**💬 Ask questions**")
    col3.caption("Chat with the video transcript.")

    st.caption("AI answers may be imperfect. Please verify important details.")


# --------------------------------------------------
# VIDEO DETAILS
# --------------------------------------------------
def show_video_details(video, video_id, active_chat_id, chat_video_id):
    same_video = active_chat_id is None or (
        video_id is not None
        and chat_video_id is not None
        and str(video_id) == str(chat_video_id)
    )

    if video and same_video:
        title = video.get("title") or video.get("video_title") or "Processed video"
        summary = video.get("summary") or video.get("video_summary")
        transcript = video.get("transcript") or video.get("full_transcript")

        st.markdown(
            f"""
            <div class="card">
                <div class="card-label">CURRENT VIDEO</div>
                <div class="card-title">🎞️ {safe(title)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("📝 Summary"):
                if summary:
                    st.markdown(to_text(summary))
                else:
                    st.caption("No summary available.")
        with col2:
            with st.expander("📄 Transcript"):
                if transcript:
                    st.text_area(
                        "Transcript",
                        value=to_text(transcript),
                        height=220,
                        disabled=True,
                        label_visibility="collapsed",
                    )
                else:
                    st.caption("No transcript available.")

    elif active_chat_id is not None:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-label">SAVED CONVERSATION</div>
                <div class="card-title">💬 Conversation #{safe(active_chat_id)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# START A NEW CHAT
# --------------------------------------------------
def show_start_chat(video_id, token):
    if video_id is None:
        st.info("Process a video before starting a conversation.")
        return

    st.subheader("Start chatting with your video")
    st.caption("Answers will be based on the processed video content.")

    if st.button("Start conversation", type="primary", use_container_width=True):
        try:
            result = create_chat(video_id, token)
        except Exception as error:
            st.error(f"Could not create conversation: {error}")
            return

        chat_id = get_id(result)
        if chat_id is None:
            st.error("The API did not return a chat ID.")
            return

        st.session_state.active_chat_id = chat_id
        st.session_state.chat_video_id = video_id
        st.session_state.chat_messages = []
        st.session_state.loaded_chat_id = chat_id  # new chat is empty
        st.rerun()


# --------------------------------------------------
# CHAT
# --------------------------------------------------
def load_messages(chat_id, token):
    """Load saved messages once per chat. Returns False on failure."""
    if str(st.session_state.loaded_chat_id) == str(chat_id):
        return True

    try:
        with st.spinner("Opening conversation..."):
            details = get_chat_details(chat_id, token)
    except Exception as error:
        st.error(f"Could not load conversation: {error}")
        return False

    raw_messages = details.get("messages", []) if isinstance(details, dict) else []
    messages = []
    for item in raw_messages if isinstance(raw_messages, list) else []:
        if isinstance(item, dict) and get_content(item):
            messages.append({"role": get_role(item), "content": get_content(item)})

    st.session_state.chat_messages = messages
    st.session_state.loaded_chat_id = chat_id
    return True


def show_chat(chat_id, token):
    if not load_messages(chat_id, token):
        return

    st.subheader("Conversation")
    messages = st.session_state.chat_messages

    if not messages:
        st.caption("Ask a question about the video to get started.")

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask anything about this video...")
    if not question or not question.strip():
        return

    question = question.strip()
    messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                result = send_chat_message(chat_id, question, token)
            answer = to_text(result.get("answer") if isinstance(result, dict) else result)
            answer = answer or "Sorry, I could not generate an answer."
            st.markdown(answer)
            messages.append({"role": "assistant", "content": answer})
        except Exception as error:
            messages.pop()  # remove the unanswered question
            st.error(f"Could not send message: {error}")


# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------
def render_workspace():
    st.markdown(CSS, unsafe_allow_html=True)

    token = st.session_state.get("token")
    if not token:
        st.warning("Please log in first.")
        return

    defaults = {
        "video": None,
        "active_chat_id": None,
        "chat_video_id": None,
        "chat_messages": [],
        "loaded_chat_id": None,
        "show_video_form": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    show_sidebar(token)

    st.title("Video workspace")
    st.caption("Transcribe, explore, and ask questions about video content.")

    show_video_form(token)

    video = st.session_state.video
    video_id = get_id(video)
    active_chat_id = st.session_state.active_chat_id

    if not video and active_chat_id is None:
        show_welcome()
        return

    show_video_details(video, video_id, active_chat_id, st.session_state.chat_video_id)
    st.divider()

    if active_chat_id is None:
        show_start_chat(video_id, token)
    else:
        show_chat(active_chat_id, token)