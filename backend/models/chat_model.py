from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.database.base import Base



class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer,primary_key=True,index=True)
    video_id = Column(Integer,ForeignKey("videos.id",ondelete="CASCADE"),
                      nullable=False,index=True)
    title = Column(String(255),nullable=False,default="New Chat")
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    video = relationship("Video")

    messages = relationship(
        "ChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChatMessage.created_at"
    )

    
