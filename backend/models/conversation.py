from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Conversation(Base, TimestampMixin):
    """Conversation model for tracking chat sessions"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), unique=True, index=True)
    channel = Column(String(50), nullable=False)  # web, whatsapp, telegram
    status = Column(String(50), default="active")  # active, closed, handoff
    
    # Additional data
    additional_data = Column(JSON, nullable=True)  # Store additional info
    
    # Relationships
    company = relationship("Company", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    
    def __repr__(self):
        return f"<Conversation(session_id='{self.session_id}', user_id={self.user_id})>"
