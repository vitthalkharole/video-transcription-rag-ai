
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import traceback

from backend.database.connection import get_db
from backend.models.video_model import Video
from backend.models.user_model import User
from backend.schemas.video_schema import (
    VideoResponse,
    VideoProcessRequest,
)
from backend.services.video_service import process_video
from backend.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)


@router.post(
    "/process-url",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED
)
def process_video_url(
    request: VideoProcessRequest,
    current_user: User = Depends(get_current_user),  # CHANGE 1
    db: Session = Depends(get_db)
):
    try:
        return process_video(
            db=db,
            source_url=str(request.source_url),
            language=request.language,
            user_id=current_user.id  # CHANGE 2
        )

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video processing failed"
        )
