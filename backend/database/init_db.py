from .connection import init_db, get_db
from ..services.database_service import DatabaseService
import uuid

def create_sample_data():
    """Create sample data for testing"""
    # No sample data needed - we only want 'מועדון גלישה גאולה'
    return None, None, None

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    
    print("Creating sample data...")
    company, user, conversation = create_sample_data()
    
    print("Database initialization complete!")
    print(f"Company: {company.name}")
    print(f"User: {user.name}")
    print(f"Conversation: {conversation.session_id}")
