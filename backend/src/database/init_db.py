from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")  # Fallback to SQLite for testing

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

def create_tables():
    """
    Creates all database tables based on the SQLModel definitions.
    This function should be called when initializing the application.
    """
    print("Creating database tables...")
    print(f"Using database URL: {DATABASE_URL}")

    # Import all models to ensure they're registered with SQLModel
    from src.models.user import User  # noqa: F401
    from src.models.task import Task  # noqa: F401

    # Create all tables
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def drop_tables():
    """
    Drops all database tables (use with caution!).
    """
    print("Dropping database tables...")
    SQLModel.metadata.drop_all(bind=engine)
    print("Database tables dropped successfully!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_tables()
    else:
        create_tables()