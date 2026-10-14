
from fastapi import FastAPI

from backend.api.video_api import router as videos_router
from backend.database.connection import engine
from backend.database.base import Base
from backend.models.video_model import Video

from backend.models.chat_model import Chat
from backend.models.chat_message_model import ChatMessage
from backend.api.chat_api import router as chat_router
from backend.api.auth_api import router as auth_router


app = FastAPI(
    title="Video RAG AI Agent",
    description="API for video transcription, summarization, and RAG-based question answering.",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

    


app.include_router(videos_router)

app.include_router(chat_router)

app.include_router(auth_router)
