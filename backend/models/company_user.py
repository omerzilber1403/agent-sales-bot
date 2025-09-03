from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class CompanyUser(Base, TimestampMixin):
    """Company User model for system administration"""
    __tablename__ = "company_users"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")  # admin, manager, viewer
    is_active = Column(Boolean, default=True)
    
    # Relationships
    company = relationship("Company", back_populates="company_users")
    
    def __repr__(self):
        return f"<CompanyUser(email='{self.email}', company_id={self.company_id})>"
