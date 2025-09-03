from .connection import get_db
from ..services.database_service import DatabaseService
from ..services.auth_service import AuthService
import uuid

def create_first_company_user():
    """Create the first company user for testing"""
    db = next(get_db())
    db_service = DatabaseService(db)
    auth_service = AuthService()
    
    # No need to create example company - we only want 'מועדון גלישה גאולה'
    company = None
    
    # Check if company user exists
    existing_user = db_service.get_company_user_by_email("admin@example.com")
    if existing_user:
        print("Company user already exists!")
        return existing_user
    
    # Create company user
    password = "admin123"  # Change this in production!
    password_hash = auth_service.get_password_hash(password)
    
    company_user = db_service.create_company_user(
        company_id=company.id,
        email="admin@example.com",
        password_hash=password_hash,
        name="Admin User",
        role="admin"
    )
    
    print(f"Created company user: {company_user.email}")
    print(f"Password: {password}")
    print(f"Company: {company.name}")
    
    return company_user

if __name__ == "__main__":
    print("Creating first company user...")
    user = create_first_company_user()
    print("Done!")
