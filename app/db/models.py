
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    query_count = Column(Integer, default=0)
    pdf_upload_count = Column(Integer, default=0)
    last_activity_date = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="documents")

class InviteCode(Base):
    __tablename__ = "invite_codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)