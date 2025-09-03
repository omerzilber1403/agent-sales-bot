from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """User model for multi-tenant support"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    external_id = Column(String(255), nullable=False)  # WhatsApp number, email, etc.
    name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Customer profiling fields
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    location = Column(String(255), nullable=True)
    occupation = Column(String(255), nullable=True)
    interests = Column(JSON, nullable=True)  # List of interests
    budget_range = Column(String(50), nullable=True)  # low, medium, high
    family_status = Column(String(50), nullable=True)  # single, married, parent
    preferred_contact = Column(String(50), nullable=True)  # phone, email, whatsapp
    
    # Customer journey tracking
    first_contact_date = Column(Date, nullable=True)
    last_contact_date = Column(Date, nullable=True)
    total_interactions = Column(Integer, default=0)
    conversion_stage = Column(String(50), default="new")  # new, interested, qualified, customer
    
    # Preferences and notes
    preferences = Column(JSON, nullable=True)  # Product preferences, communication style
    notes = Column(String(1000), nullable=True)  # Internal notes about the customer
    
    # Sales conversation tracking
    reason_for_interest = Column(String(500), nullable=True)  # Why they came to us
    specific_need = Column(String(500), nullable=True)  # What specific need they have
    
    # Relationships
    company = relationship("Company", back_populates="users")
    conversations = relationship("Conversation", back_populates="user")
    
    def __repr__(self):
        return f"<User(external_id='{self.external_id}', company_id={self.company_id})>"
