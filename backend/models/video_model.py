from sqlalchemy import Column, Integer, String, DateTime, Text,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.database.base import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    source_url = Column(String(2048), nullable=False)
    title = Column(String(255), nullable=True)
    status = Column(String(30), nullable=False, default="pending")

    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    key_decisions = Column(Text, nullable=True)
    open_questions = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


    user = relationship("User", back_populates="videos")