
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ChatCreateRequest(BaseModel):
    title: str = Field(
        default="New Chat",
        min_length=1,
        max_length=255
    )


class ChatResponse(BaseModel):
    id: int
    video_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )


class ChatMessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatDetailResponse(ChatResponse):
    messages: list[ChatMessageResponse]


class ChatTurnResponse(BaseModel):
    chat_id: int
    video_id: int
    question: ChatMessageResponse
    answer: ChatMessageResponse

