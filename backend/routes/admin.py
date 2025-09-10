from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..services.database_service import DatabaseService, get_database_service
from ..models.company import Company
from ..models.user import User

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# Pydantic models for requests/responses
class CompanyCreate(BaseModel):
    # Core fields (חובה)
    name: str
    domain: Optional[str] = None
    api_key: Optional[str] = None
    brand_aliases: Optional[List[str]] = None
    timezone: str = 'Asia/Jerusalem'
    locale: str = 'he-IL'
    currency: str = 'ILS'
    business_type: str = 'B2B'  # B2B or B2C
    
    # Brand Voice
    brand_voice: Optional[Dict[str, Any]] = None
    
    # Value proposition
    one_line_value: Optional[str] = None
    
    # ICP
    icp: Optional[Dict[str, Any]] = None
    
    # Pain points
    pain_points: Optional[List[str]] = None
    
    # Products
    products: Optional[List[Dict[str, Any]]] = None
    
    # Pricing Policy
    pricing_policy: Optional[Dict[str, Any]] = None
    
    # CTA
    cta_type: str = 'booking_link'
    booking_link: Optional[str] = None
    meeting_length_min: int = 15
    
    # Qualification Rules
    qualification_rules: Optional[Dict[str, Any]] = None
    
    # Objections Playbook
    objections_playbook: Optional[Dict[str, str]] = None
    
    # Handoff Rules
    handoff_rules: Optional[Dict[str, Any]] = None
    
    # Plus fields (אופציונלי)
    differentiators: Optional[List[str]] = None
    competitors_map: Optional[Dict[str, str]] = None
    discovery_questions: Optional[List[str]] = None
    faq_kb_refs: Optional[List[Dict[str, Any]]] = None
    case_studies: Optional[List[Dict[str, Any]]] = None
    refund_sla_policy: Optional[str] = None
    language_prefs: Optional[Dict[str, Any]] = None
    quote_long_mode: Optional[Dict[str, Any]] = None
    sensitive_topics: Optional[List[str]] = None
    
    # Pro fields (אופציונלי)
    consent_texts: Optional[Dict[str, str]] = None
    pii_allowed: Optional[List[str]] = None
    regional_rules: Optional[List[Dict[str, Any]]] = None
    lead_scoring: Optional[Dict[str, Any]] = None
    analytics_goals: Optional[List[str]] = None
    update_cadence: Optional[str] = None
    policy_version: Optional[str] = None
    owner: Optional[str] = None
    
    # Custom fields for company-specific data collection
    custom_fields: Optional[Dict[str, Any]] = None
    
    # Legacy fields (for backward compatibility)
    custom_prompt: Optional[str] = None
    handoff_message: Optional[str] = None
    max_conversations: int = 1000

class CompanyResponse(BaseModel):
    id: int
    name: str
    domain: Optional[str]
    is_active: bool
    
    # Core fields
    brand_aliases: Optional[List[str]]
    timezone: str
    locale: str
    currency: str
    business_type: str
    
    # Brand Voice
    brand_voice: Optional[Dict[str, Any]]
    
    # Value proposition
    one_line_value: Optional[str]
    
    # ICP
    icp: Optional[Dict[str, Any]]
    
    # Pain points
    pain_points: Optional[List[str]]
    
    # Products
    products: Optional[List[Dict[str, Any]]]
    
    # Pricing Policy
    pricing_policy: Optional[Dict[str, Any]]
    
    # CTA
    cta_type: str
    booking_link: Optional[str]
    meeting_length_min: int
    
    # Qualification Rules
    qualification_rules: Optional[Dict[str, Any]]
    
    # Objections Playbook
    objections_playbook: Optional[Dict[str, str]]
    
    # Handoff Rules
    handoff_rules: Optional[Dict[str, Any]]
    
    # Plus fields
    differentiators: Optional[List[str]]
    competitors_map: Optional[Dict[str, str]]
    discovery_questions: Optional[List[str]]
    faq_kb_refs: Optional[List[Dict[str, Any]]]
    case_studies: Optional[List[Dict[str, Any]]]
    refund_sla_policy: Optional[str]
    language_prefs: Optional[Dict[str, Any]]
    quote_long_mode: Optional[Dict[str, Any]]
    sensitive_topics: Optional[List[str]]
    
    # Pro fields
    consent_texts: Optional[Dict[str, str]]
    pii_allowed: Optional[List[str]]
    regional_rules: Optional[List[Dict[str, Any]]]
    lead_scoring: Optional[Dict[str, Any]]
    analytics_goals: Optional[List[str]]
    update_cadence: Optional[str]
    policy_version: Optional[str]
    owner: Optional[str]
    
    # Custom fields for company-specific data collection
    custom_fields: Optional[Dict[str, Any]]
    
    # Legacy fields
    custom_prompt: Optional[str]
    handoff_message: Optional[str]
    max_conversations: int

class UserCreate(BaseModel):
    company_id: int
    external_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    company_id: int
    external_id: str
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    is_active: bool

# Company routes
@router.post("/companies", response_model=CompanyResponse)
def create_company(
    company: CompanyCreate,
    db_service: DatabaseService = Depends(get_database_service)
):
    """Create a new company with advanced configuration"""
    try:
        # Generate API key if not provided
        if not company.api_key:
            import secrets
            company.api_key = f"ak_{secrets.token_urlsafe(32)}"
        
        # Generate domain if not provided
        if not company.domain:
            import re
            import uuid
            safe_name = re.sub(r'[^a-zA-Z0-9]', '', company.name.lower())
            # If no safe characters, use a random string
            if not safe_name:
                safe_name = f"company_{uuid.uuid4().hex[:8]}"
            company.domain = f"{safe_name}.example.com"
        
        # Create company with all fields
        db_company = Company(
            name=company.name,
            domain=company.domain,
            api_key=company.api_key,
            brand_aliases=company.brand_aliases,
            timezone=company.timezone,
            locale=company.locale,
            currency=company.currency,
            business_type=company.business_type,
            brand_voice=company.brand_voice,
            one_line_value=company.one_line_value,
            icp=company.icp,
            pain_points=company.pain_points,
            products=company.products,
            pricing_policy=company.pricing_policy,
            cta_type=company.cta_type,
            booking_link=company.booking_link,
            meeting_length_min=company.meeting_length_min,
            qualification_rules=company.qualification_rules,
            objections_playbook=company.objections_playbook,
            handoff_rules=company.handoff_rules,
            differentiators=company.differentiators,
            competitors_map=company.competitors_map,
            discovery_questions=company.discovery_questions,
            faq_kb_refs=company.faq_kb_refs,
            case_studies=company.case_studies,
            refund_sla_policy=company.refund_sla_policy,
            language_prefs=company.language_prefs,
            quote_long_mode=company.quote_long_mode,
            sensitive_topics=company.sensitive_topics,
            consent_texts=company.consent_texts,
            pii_allowed=company.pii_allowed,
            regional_rules=company.regional_rules,
            lead_scoring=company.lead_scoring,
            analytics_goals=company.analytics_goals,
            update_cadence=company.update_cadence,
            policy_version=company.policy_version,
            owner=company.owner,
            custom_fields=company.custom_fields,
            custom_prompt=company.custom_prompt,
            handoff_message=company.handoff_message,
            max_conversations=company.max_conversations
        )
        
        db_service.db.add(db_company)
        db_service.db.commit()
        db_service.db.refresh(db_company)
        
        return CompanyResponse(
            id=db_company.id,
            name=db_company.name,
            domain=db_company.domain,
            is_active=db_company.is_active,
            brand_aliases=db_company.brand_aliases,
            timezone=db_company.timezone,
            locale=db_company.locale,
            currency=db_company.currency,
            business_type=db_company.business_type,
            brand_voice=db_company.brand_voice,
            one_line_value=db_company.one_line_value,
            icp=db_company.icp,
            pain_points=db_company.pain_points,
            products=db_company.products,
            pricing_policy=db_company.pricing_policy,
            cta_type=db_company.cta_type,
            booking_link=db_company.booking_link,
            meeting_length_min=db_company.meeting_length_min,
            qualification_rules=db_company.qualification_rules,
            objections_playbook=db_company.objections_playbook,
            handoff_rules=db_company.handoff_rules,
            differentiators=db_company.differentiators,
            competitors_map=db_company.competitors_map,
            discovery_questions=db_company.discovery_questions,
            faq_kb_refs=db_company.faq_kb_refs,
            case_studies=db_company.case_studies,
            refund_sla_policy=db_company.refund_sla_policy,
            language_prefs=db_company.language_prefs,
            quote_long_mode=db_company.quote_long_mode,
            sensitive_topics=db_company.sensitive_topics,
            consent_texts=db_company.consent_texts,
            pii_allowed=db_company.pii_allowed,
            regional_rules=db_company.regional_rules,
            lead_scoring=db_company.lead_scoring,
            analytics_goals=db_company.analytics_goals,
            update_cadence=db_company.update_cadence,
            policy_version=db_company.policy_version,
            owner=db_company.owner,
            custom_fields=db_company.custom_fields,
            custom_prompt=db_company.custom_prompt,
            handoff_message=db_company.handoff_message,
            max_conversations=db_company.max_conversations
        )
    except Exception as e:
        db_service.db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/companies", response_model=List[CompanyResponse])
def list_companies(
    db_service: DatabaseService = Depends(get_database_service)
):
    """List all companies"""
    companies = db_service.db.query(Company).all()
    return [
        CompanyResponse(
            id=c.id,
            name=c.name,
            domain=c.domain,
            is_active=c.is_active,
            brand_aliases=c.brand_aliases,
            timezone=c.timezone,
            locale=c.locale,
            currency=c.currency,
            business_type=c.business_type,
            brand_voice=c.brand_voice,
            one_line_value=c.one_line_value,
            icp=c.icp,
            pain_points=c.pain_points,
            products=c.products,
            pricing_policy=c.pricing_policy,
            cta_type=c.cta_type,
            booking_link=c.booking_link,
            meeting_length_min=c.meeting_length_min,
            qualification_rules=c.qualification_rules,
            objections_playbook=c.objections_playbook,
            handoff_rules=c.handoff_rules,
            differentiators=c.differentiators,
            competitors_map=c.competitors_map,
            discovery_questions=c.discovery_questions,
            faq_kb_refs=c.faq_kb_refs,
            case_studies=c.case_studies,
            refund_sla_policy=c.refund_sla_policy,
            language_prefs=c.language_prefs,
            quote_long_mode=c.quote_long_mode,
            sensitive_topics=c.sensitive_topics,
            consent_texts=c.consent_texts,
            pii_allowed=c.pii_allowed,
            regional_rules=c.regional_rules,
            lead_scoring=c.lead_scoring,
            analytics_goals=c.analytics_goals,
            update_cadence=c.update_cadence,
            policy_version=c.policy_version,
            owner=c.owner,
            custom_fields=c.custom_fields,
            custom_prompt=c.custom_prompt,
            handoff_message=c.handoff_message,
            max_conversations=c.max_conversations
        )
        for c in companies
    ]

# User routes
@router.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db_service: DatabaseService = Depends(get_database_service)
):
    """Create a new user"""
    try:
        db_user = db_service.create_user(
            company_id=user.company_id,
            external_id=user.external_id,
            name=user.name,
            phone=user.phone,
            email=user.email
        )
        return UserResponse(
            id=db_user.id,
            company_id=db_user.company_id,
            external_id=db_user.external_id,
            name=db_user.name,
            phone=db_user.phone,
            email=db_user.email,
            is_active=db_user.is_active
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/companies/{company_id}/users", response_model=List[UserResponse])
def list_company_users(
    company_id: int,
    db_service: DatabaseService = Depends(get_database_service)
):
    """List all users for a company"""
    users = db_service.db.query(User).filter(User.company_id == company_id).all()
    return [
        UserResponse(
            id=u.id,
            company_id=u.company_id,
            external_id=u.external_id,
            name=u.name,
            phone=u.phone,
            email=u.email,
            is_active=u.is_active
        )
        for u in users
    ]
