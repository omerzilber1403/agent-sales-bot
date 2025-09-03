from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
from ..config import get_settings

# Database URL
DB_PATH = Path("data/agent.db")
DB_PATH.parent.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH.absolute()}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    poolclass=StaticPool,
    echo=True  # Log SQL queries
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from backend.models.base import Base
    # Import all models to ensure they're registered
    from backend.models.company import Company
    from backend.models.user import User
    from backend.models.conversation import Conversation
    from backend.models.message import Message
    from backend.models.company_user import CompanyUser
    
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DB_PATH.absolute()}")
