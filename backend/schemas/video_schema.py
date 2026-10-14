from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict


class VideoCreate(BaseModel):
    source_url: HttpUrl


class VideoProcessRequest(BaseModel):
    source_url: HttpUrl
    language: str = "english"


class VideoResponse(BaseModel):
    id: int
    source_url: str
    title: str | None = None
    status: str

    transcript: str | None = None
    summary: str | None = None
    action_items: str | None = None
    key_decisions: str | None = None
    open_questions: str | None = None

    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class VideoUpdate(BaseModel):
    title: str
    status: str


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    video_id: int
    question: str
    answer: str