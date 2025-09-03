from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models.company import Company
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.company_user import CompanyUser
from ..database.connection import get_db

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Company operations
    def create_company(self, name: str, domain: str, api_key: str, **kwargs) -> Company:
        """Create a new company"""
        company = Company(
            name=name,
            domain=domain,
            api_key=api_key,
            **kwargs
        )
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def get_company_by_domain(self, domain: str) -> Optional[Company]:
        """Get company by domain"""
        return self.db.query(Company).filter(Company.domain == domain).first()
    
    def get_company_by_api_key(self, api_key: str) -> Optional[Company]:
        """Get company by API key"""
        return self.db.query(Company).filter(Company.api_key == api_key).first()
    
    def get_company(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    # User operations
    def create_user(self, company_id: int, external_id: str, **kwargs) -> User:
        """Create a new user"""
        user = User(
            company_id=company_id,
            external_id=external_id,
            **kwargs
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_external_id(self, company_id: int, external_id: str) -> Optional[User]:
        """Get user by external ID within a company"""
        return self.db.query(User).filter(
            User.company_id == company_id,
            User.external_id == external_id
        ).first()
    
    # Company User operations
    def create_company_user(self, company_id: int, email: str, password_hash: str, name: str, role: str = "admin") -> CompanyUser:
        """Create a new company user"""
        company_user = CompanyUser(
            company_id=company_id,
            email=email,
            password_hash=password_hash,
            name=name,
            role=role
        )
        self.db.add(company_user)
        self.db.commit()
        self.db.refresh(company_user)
        return company_user
    
    def get_company_user_by_email(self, email: str) -> Optional[CompanyUser]:
        """Get company user by email"""
        return self.db.query(CompanyUser).filter(CompanyUser.email == email).first()
    
    def get_company_users(self, company_id: int) -> List[CompanyUser]:
        """Get all company users for a company"""
        return self.db.query(CompanyUser).filter(CompanyUser.company_id == company_id).all()
    
    # Conversation operations
    def create_conversation(self, company_id: int, user_id: int, session_id: str, channel: str, **kwargs) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            company_id=company_id,
            user_id=user_id,
            session_id=session_id,
            channel=channel,
            **kwargs
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_conversation_by_session(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID"""
        return self.db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    # Message operations
    def create_message(self, conversation_id: int, role: str, content: str, **kwargs) -> Message:
        """Create a new message"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            **kwargs
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        """Get all messages for a conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()

# Factory function
def get_database_service() -> DatabaseService:
    """Get database service instance"""
    db = next(get_db())
    return DatabaseService(db)
