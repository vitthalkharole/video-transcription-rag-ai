from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String(100),nullable=False,unique=True,index=True)
    email = Column(String(255),nullable=False,unique=False,index=True)
    hashed_password = Column(String(255),nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    videos =relationship("Video",back_populates="user")
