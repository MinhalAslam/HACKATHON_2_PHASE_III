from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool
from typing import Generator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")  # Fallback to SQLite for testing

# Create the engine with proper connection pooling for serverless databases
# Use NullPool for serverless databases like Neon to avoid connection pool issues
engine = create_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool,  # No connection pooling for serverless
    connect_args={
        "connect_timeout": 10,
    } if "postgresql" in DATABASE_URL else {}
)

def get_session() -> Generator[Session, None, None]:
    """Get a database session with proper error handling"""
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise