"""Video RAG AI - Streamlit workspace."""
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
# STYLING
# --------------------------------------------------
CSS = """
<style>
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 820px; padding: 2.5rem 1.5rem 6rem 1.5rem; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: rgba(128,128,128,0.07); }
[data-testid="stSidebar"] .block-container { padding: 1.2rem 0.7rem; }

.brand { font-size: 1.1rem; font-weight: 650; padding: 0.2rem 0.6rem 0.8rem 0.6rem; }
.section-label {
    font-size: 0.72rem; letter-spacing: 0.06em; opacity: 0.55;
    padding: 0.8rem 0.6rem 0.3rem 0.6rem;
}

/* chat rows: flat, left aligned, no borders */
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: none;
    box-shadow: none;
    color: inherit;
    justify-content: flex-start;
    text-align: left;
    font-weight: 400;
    padding: 0.5rem 0.7rem;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stButton > button p {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-align: left;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(128,128,128,0.16);
}
/* active chat */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: rgba(128,128,128,0.22);
    color: inherit;
}

/* the "..." menu button */
[data-testid="stSidebar"] [data-testid="stPopover"] button {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0.5rem 0;
    justify-content: center;
}
[data-testid="stSidebar"] [data-testid="stPopover"] button:hover {
    background: rgba(128,128,128,0.16);
}
[data-testid="stSidebar"] [data-testid="stPopover"] button svg { display: none; }

/* search box */
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    border-radius: 8px;
    background: rgba(128,128,128,0.12);
    border: none;
}

/* ---------- Main area ---------- */
.stButton > button { border-radius: 8px; }

/* chat messages: no boxes, like ChatGPT */
[data-testid="stChatMessage"] {
    background: transparent;
    border: none;
    padding: 0.6rem 0;
}
</style>
"""


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def get_id(item):
    """Return the id of a video or chat dict (API may use id, chat_id or video_id)."""
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
        st.markdown('<div class="brand">Video RAG AI</div>', unsafe_allow_html=True)

        search = st.text_input(
            "Search chats",
            placeholder="Search chats",
            label_visibility="collapsed",
        )

        st.markdown('<div class="section-label">CHATS</div>', unsafe_allow_html=True)

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
            st.caption("No conversations yet.")

        for chat in chats:
            chat_id = get_id(chat)
            if chat_id is None:
                continue

            title = chat.get("title") or f"Conversation {chat_id}"
            is_active = str(st.session_state.active_chat_id) == str(chat_id)

            col_open, col_menu = st.columns([6, 1], vertical_alignment="center")
            with col_open:
                if st.button(
                    title,
                    key=f"open_{chat_id}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                    help=title,
                ):
                    st.session_state.active_chat_id = chat_id
                    st.session_state.chat_video_id = chat.get("video_id")
                    st.session_state.chat_messages = []
                    st.session_state.loaded_chat_id = None
                    st.rerun()
            with col_menu:
                with st.popover("⋯", use_container_width=True):
                    if st.button("Delete chat", key=f"delete_{chat_id}"):
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

    with st.expander("Add a video", expanded=no_context):
        with st.form("video_form", border=False):
            url = st.text_input(
                "Video URL",
                placeholder="Paste a YouTube video URL",
            )
            submitted = st.form_submit_button(
                "Process video", type="primary", use_container_width=True
            )

    if not submitted:
        return

    if not url.strip():
        st.warning("Please paste a video URL.")
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
    reset_chat()
    st.rerun()


# --------------------------------------------------
# WELCOME SCREEN
# --------------------------------------------------
def show_welcome():
    st.markdown("")
    st.markdown("## Ask questions about any video")
    st.write(
        "Process a YouTube video, read its transcript, and chat with "
        "the content."
    )

    features = [
        ("Transcribe", "Turn any video into searchable text."),
        ("Summarize", "Get the key ideas without rewatching."),
        ("Ask questions", "Chat with the transcript in plain language."),
    ]
    for col, (title, text) in zip(st.columns(3), features):
        with col.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(text)

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

        with st.container(border=True):
            st.caption("CURRENT VIDEO")
            st.markdown(f"**{title}**")

            tab_summary, tab_transcript = st.tabs(["Summary", "Transcript"])
            with tab_summary:
                if summary:
                    st.markdown(to_text(summary))
                else:
                    st.caption("No summary available.")
            with tab_transcript:
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
        with st.container(border=True):
            st.caption("SAVED CONVERSATION")
            st.markdown(f"**Conversation #{active_chat_id}**")


# --------------------------------------------------
# START A NEW CHAT
# --------------------------------------------------
def show_start_chat(video_id, token):
    if video_id is None:
        st.info("Process a video to start a conversation.")
        return

    st.markdown("#### Start a conversation")
    st.caption("Answers are based on the processed video.")

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

    messages = st.session_state.chat_messages

    if not messages:
        st.caption("Ask a question about the video to get started.")

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask anything about this video")
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
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    show_sidebar(token)

    st.title("Workspace")

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