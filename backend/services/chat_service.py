
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from backend.models.video_model import Video
from backend.models.chat_model import Chat
from backend.models.chat_message_model import ChatMessage

from backend.services.vectore_store import load_vector_store
from backend.services.summarize import get_llm

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# CHANGE 1: Verify that a video belongs to the logged-in user
def get_owned_video(db: Session, video_id: int, user_id: int):
    video = (
        db.query(Video)
        .filter(
            Video.id == video_id,
            Video.user_id == user_id
        )
        .first()
    )

    if video is None:
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    return video


# CHANGE 2: Verify that a chat belongs to the logged-in user
def get_owned_chat(db: Session, chat_id: int, user_id: int):
    chat = (
        db.query(Chat)
        .join(Video, Chat.video_id == Video.id)
        .filter(
            Chat.id == chat_id,
            Video.user_id == user_id
        )
        .first()
    )

    if chat is None:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    return chat


def create_chat(
    db: Session,
    video_id: int,
    user_id: int,  # CHANGE
    title: str = "New Chat"
):
    video = get_owned_video(db, video_id, user_id)

    if video.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Video processing is not completed"
        )

    chat = Chat(video_id=video_id, title=title)

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def list_chats(db: Session, video_id: int, user_id: int):  # CHANGE
    get_owned_video(db, video_id, user_id)

    return (
        db.query(Chat)
        .filter(Chat.video_id == video_id)
        .order_by(Chat.updated_at.desc(), Chat.id.desc())
        .all()
    )


def get_chat(db: Session, chat_id: int, user_id: int):  # CHANGE
    return get_owned_chat(db, chat_id, user_id)


def send_message(
    db: Session,
    chat_id: int,
    question: str,
    user_id: int  # CHANGE
):
    # CHANGE 3: Verify chat ownership before reading or writing messages
    chat = get_owned_chat(db, chat_id, user_id)

    video = get_owned_video(db, chat.video_id, user_id)

    if video.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="The associated video is not available for chatting"
        )

    # 1. Load recent conversation history
    history_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.id.desc())
        .limit(10)
        .all()
    )

    history_messages.reverse()

    history = "\n".join(
        f"{message.role}: {message.content}"
        for message in history_messages
    )

    # 2. Save the user's question
    user_message = ChatMessage(
        chat_id=chat_id,
        role="user",
        content=question
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    try:
        # 3. Retrieve transcript chunks for this video
        vector_store = load_vector_store()

        documents = vector_store.similarity_search(
            query=question,
            k=4,
            filter={"video_id": chat.video_id}
        )

        context = "\n\n".join(
            document.page_content for document in documents
        )

        if not context:
            context = (
                "No relevant transcript information was retrieved. "
                "Do not invent facts about the video."
            )

        # 4. Generate an answer using conversation history and RAG
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an assistant answering questions about a video.

Use the retrieved transcript as the source of factual information.
Use conversation history to understand follow-up questions and references.
Do not treat conversation history as verified video evidence.
If the transcript does not support an answer, say that the information
is not available in the retrieved transcript.
Keep answers clear and concise."""
            ),
            (
                "human",
                """Previous conversation:
{history}

Retrieved transcript:
{context}

Current question:
{question}"""
            )
        ])

        chain = prompt | get_llm() | StrOutputParser()

        answer = chain.invoke({
            "history": history or "No previous conversation.",
            "context": context,
            "question": question
        })

        # 5. Save the assistant's answer
        assistant_message = ChatMessage(
            chat_id=chat_id,
            role="assistant",
            content=answer
        )

        db.add(assistant_message)

        if chat.title == "New Chat":
            chat.title = question[:50]

        chat.updated_at = func.now()

        db.commit()
        db.refresh(assistant_message)

        return {
            "chat_id": chat_id,
            "video_id": chat.video_id,
            "question": user_message,
            "answer": assistant_message
        }

    except Exception:
        db.rollback()
        raise


def delete_chat(db: Session, chat_id: int, user_id: int):  # CHANGE
    # CHANGE 4: Verify ownership before deleting
    chat = get_owned_chat(db, chat_id, user_id)

    try:
        db.delete(chat)
        db.commit()

        return {
            "message": "Chat deleted successfully",
            "chat_id": chat_id
        }

    except Exception:
        db.rollback()
        raise
