from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Message(Base, TimestampMixin):
    """Message model for storing individual chat messages"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # LLM metadata
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    execution_path = Column(JSON, nullable=True)  # LangGraph execution path
    
    # Business logic
    is_handoff = Column(Boolean, default=False)
    handoff_reason = Column(String(255), nullable=True)
    additional_data = Column(JSON, nullable=True)  # Additional info
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(role='{self.role}', conversation_id={self.conversation_id})>"
