from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models.company_user import CompanyUser
from ..models.company import Company
from ..config import get_settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for company authentication"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def authenticate_company_user(db: Session, email: str, password: str) -> Optional[CompanyUser]:
        """Authenticate a company user"""
        user = db.query(CompanyUser).filter(CompanyUser.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

# Factory function
def get_auth_service() -> AuthService:
    """Get auth service instance"""
    return AuthService()
