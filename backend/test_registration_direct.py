#!/usr/bin/env python3
"""
Direct test of registration endpoint to identify errors
"""
import sys
import traceback
from src.database.database import get_session
from src.models import UserCreate, User, Task  # Import both models together
from src.routers.auth import register_user

def test_registration():
    """Test registration directly"""
    try:
        print("Testing direct registration...")

        # Get a database session
        session_gen = get_session()
        session = next(session_gen)

        # Create test user data
        user_data = UserCreate(
            email="directtest@example.com",
            password="testpass123"
        )

        # Call the registration function
        result = register_user(user_data, session)

        print(f"Success! User created: {result.email}")
        print(f"User ID: {result.id}")

        session.close()

    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_registration()
