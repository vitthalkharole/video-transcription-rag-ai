
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.dependencies.auth import get_current_user  # CHANGE
from backend.models.user_model import User  # CHANGE

from backend.schemas.chat_schema import (
    ChatCreateRequest,
    ChatResponse,
    ChatDetailResponse,
    ChatMessageRequest,
    ChatTurnResponse,
)

from backend.services.chat_service import (
    create_chat,
    list_chats,
    get_chat,
    send_message,
    delete_chat,
)

router = APIRouter(tags=["Chat"])


# 1. Create a conversation
@router.post(
    "/videos/{video_id}/chats",
    response_model=ChatResponse,
    status_code=201,
)
def create_video_chat(
    video_id: int,
    request: ChatCreateRequest,
    current_user: User = Depends(get_current_user),  # CHANGE
    db: Session = Depends(get_db),
):
    return create_chat(
        db=db,
        video_id=video_id,
        title=request.title,
        user_id=current_user.id,  # CHANGE
    )


# 2. List conversations for a video
@router.get(
    "/videos/{video_id}/chats",
    response_model=list[ChatResponse],
)
def get_video_chats(
    video_id: int,
    current_user: User = Depends(get_current_user),  # CHANGE
    db: Session = Depends(get_db),
):
    return list_chats(
        db=db,
        video_id=video_id,
        user_id=current_user.id,  # CHANGE
    )


# 3. Retrieve a conversation and its messages
@router.get(
    "/chats/{chat_id}",
    response_model=ChatDetailResponse,
)
def get_chat_history(
    chat_id: int,
    current_user: User = Depends(get_current_user),  # CHANGE
    db: Session = Depends(get_db),
):
    return get_chat(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,  # CHANGE
    )


# 4. Send a question in a conversation
@router.post(
    "/chats/{chat_id}/messages",
    response_model=ChatTurnResponse,
)
def create_chat_message(
    chat_id: int,
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),  # CHANGE
    db: Session = Depends(get_db),
):
    return send_message(
        db=db,
        chat_id=chat_id,
        question=request.question,
        user_id=current_user.id,  # CHANGE
    )


# 5. Delete a conversation
@router.delete("/chats/{chat_id}")
def remove_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),  # CHANGE
    db: Session = Depends(get_db),
):
    return delete_chat(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,  # CHANGE
    )
