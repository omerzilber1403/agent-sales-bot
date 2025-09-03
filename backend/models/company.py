from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Company(Base, TimestampMixin):
    """Company model for multi-tenant support"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), unique=True, index=True)
    api_key = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    
    # Core fields (חובה)
    brand_aliases = Column(JSON, nullable=True)  # Array of brand aliases
    timezone = Column(String(50), default='Asia/Jerusalem')
    locale = Column(String(10), default='he-IL')
    currency = Column(String(3), default='ILS')
    business_type = Column(String(10), default='B2B')  # B2B or B2C
    
    # Brand Voice
    brand_voice = Column(JSON, nullable=True)  # Brand voice configuration
    
    # Value proposition
    one_line_value = Column(Text, nullable=True)
    
    # ICP (Ideal Customer Profile)
    icp = Column(JSON, nullable=True)  # Industries, company_size, buyer_roles
    
    # Pain points
    pain_points = Column(JSON, nullable=True)  # Array of pain points
    
    # Products
    products = Column(JSON, nullable=True)  # Array of products/packages
    
    # Pricing Policy
    pricing_policy = Column(JSON, nullable=True)  # Pricing configuration
    
    # CTA (Call to Action)
    cta_type = Column(String(50), default='booking_link')
    booking_link = Column(String(500), nullable=True)
    meeting_length_min = Column(Integer, default=15)
    
    # Qualification Rules
    qualification_rules = Column(JSON, nullable=True)  # BANT and qualification rules
    
    # Objections Playbook
    objections_playbook = Column(JSON, nullable=True)  # Common objections and responses
    
    # Handoff Rules
    handoff_rules = Column(JSON, nullable=True)  # When to handoff to human
    
    # Plus fields (אופציונלי)
    differentiators = Column(JSON, nullable=True)  # What makes them unique
    competitors_map = Column(JSON, nullable=True)  # Competitor analysis
    discovery_questions = Column(JSON, nullable=True)  # Training questions for bot
    faq_kb_refs = Column(JSON, nullable=True)  # FAQ knowledge base references
    case_studies = Column(JSON, nullable=True)  # Customer success stories
    refund_sla_policy = Column(Text, nullable=True)  # Refund and SLA policy
    language_prefs = Column(JSON, nullable=True)  # Language preferences
    quote_long_mode = Column(JSON, nullable=True)  # Quote template configuration
    sensitive_topics = Column(JSON, nullable=True)  # Topics to avoid
    
    # Pro fields (אופציונלי)
    consent_texts = Column(JSON, nullable=True)  # Consent text for different channels
    pii_allowed = Column(JSON, nullable=True)  # Allowed PII fields
    regional_rules = Column(JSON, nullable=True)  # Regional regulations
    lead_scoring = Column(JSON, nullable=True)  # Lead scoring rules
    analytics_goals = Column(JSON, nullable=True)  # KPI tracking
    update_cadence = Column(String(50), nullable=True)  # How often to update KB
    policy_version = Column(String(50), nullable=True)  # Policy version
    owner = Column(String(255), nullable=True)  # Company owner contact
    
    # Custom fields for company-specific data collection
    custom_fields = Column(JSON, nullable=True)  # Company-specific fields to collect from customers
    
    # Legacy fields (for backward compatibility)
    custom_prompt = Column(Text, nullable=True)
    handoff_message = Column(Text, nullable=True)
    max_conversations = Column(Integer, default=1000)
    
    # Relationships
    users = relationship("User", back_populates="company")
    conversations = relationship("Conversation", back_populates="company")
    company_users = relationship("CompanyUser", back_populates="company")
    
    def __repr__(self):
        return f"<Company(name='{self.name}', domain='{self.domain}')>"
