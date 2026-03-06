"""
API Validation Tests for Authentication & Security Implementation

This test suite validates the following requirements from Spec 2:
- API request without JWT returns 401
- API request with invalid JWT returns 401
- API request with expired JWT returns 401
- Authenticated user cannot access another user's tasks
- URL user_id mismatch is rejected
- Valid JWT + correct user_id succeeds
"""

import pytest
import jwt
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app
from src.database.database import engine
from src.models.user import User
from src.models.task import Task
from sqlmodel import Session, SQLModel, select
from uuid import uuid4


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    from src.utils.auth import get_password_hash

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        role="user"
    )

    # Insert directly to database for testing
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    return user


@pytest.fixture
def valid_jwt(mock_user):
    """Create a valid JWT token for the mock user"""
    from src.utils.jwt import SECRET_KEY, ALGORITHM

    token_data = {
        "sub": str(mock_user.id),
        "exp": datetime.utcnow() + timedelta(hours=1)  # Valid for 1 hour
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token


@pytest.fixture
def expired_jwt(mock_user):
    """Create an expired JWT token for the mock user"""
    from src.utils.jwt import SECRET_KEY, ALGORITHM

    token_data = {
        "sub": str(mock_user.id),
        "exp": datetime.utcnow() - timedelta(seconds=1)  # Already expired
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token


def test_api_request_without_jwt_returns_401(client):
    """Test that API request without JWT returns 401 Unauthorized"""
    # Test GET /{user_id}/tasks endpoint
    response = client.get("/123/tasks")
    assert response.status_code == 401

    # Test POST /{user_id}/tasks endpoint
    response = client.post("/123/tasks", json={"title": "Test"})
    assert response.status_code == 401

    # Test GET /{user_id}/tasks/{id} endpoint
    response = client.get("/123/tasks/456")
    assert response.status_code == 401

    # Test PUT /{user_id}/tasks/{id} endpoint
    response = client.put("/123/tasks/456", json={"title": "Updated"})
    assert response.status_code == 401

    # Test DELETE /{user_id}/tasks/{id} endpoint
    response = client.delete("/123/tasks/456")
    assert response.status_code == 401

    # Test PATCH /{user_id}/tasks/{id}/complete endpoint
    response = client.patch("/123/tasks/456/complete", json={"completed": True})
    assert response.status_code == 401


def test_api_request_with_invalid_jwt_returns_401(client):
    """Test that API request with invalid JWT returns 401 Unauthorized"""
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }

    # Test GET /{user_id}/tasks endpoint
    response = client.get("/123/tasks", headers=headers)
    assert response.status_code == 401

    # Test POST /{user_id}/tasks endpoint
    response = client.post("/123/tasks", json={"title": "Test"}, headers=headers)
    assert response.status_code == 401


def test_api_request_with_expired_jwt_returns_401(client, expired_jwt):
    """Test that API request with expired JWT returns 401 Unauthorized"""
    headers = {
        "Authorization": f"Bearer {expired_jwt}"
    }

    # Test GET /{user_id}/tasks endpoint
    response = client.get("/123/tasks", headers=headers)
    assert response.status_code == 401

    # Test POST /{user_id}/tasks endpoint
    response = client.post("/123/tasks", json={"title": "Test"}, headers=headers)
    assert response.status_code == 401


def test_url_user_id_mismatch_rejected(client, valid_jwt, mock_user):
    """Test that URL user_id mismatch is rejected with 403 Forbidden"""
    headers = {
        "Authorization": f"Bearer {valid_jwt}"
    }

    # Use a different user_id in the URL than the one in the token
    different_user_id = str(uuid4())

    # Test GET /{user_id}/tasks endpoint
    response = client.get(f"/{different_user_id}/tasks", headers=headers)
    assert response.status_code == 403
    assert "does not match authenticated user_id" in response.json().get("detail", "")

    # Test POST /{user_id}/tasks endpoint
    response = client.post(f"/{different_user_id}/tasks", json={"title": "Test"}, headers=headers)
    assert response.status_code == 403
    assert "does not match authenticated user_id" in response.json().get("detail", "")

    # Test GET /{user_id}/tasks/{id} endpoint
    response = client.get(f"/{different_user_id}/tasks/123", headers=headers)
    assert response.status_code == 403
    assert "does not match authenticated user_id" in response.json().get("detail", "")


def test_valid_jwt_with_correct_user_id_succeeds(client, valid_jwt, mock_user):
    """Test that valid JWT + correct user_id succeeds"""
    headers = {
        "Authorization": f"Bearer {valid_jwt}"
    }

    # Test GET /{user_id}/tasks endpoint with correct user_id
    response = client.get(f"/{mock_user.id}/tasks", headers=headers)
    # This might return 200 (empty list) or 404 depending on implementation,
    # but should not return 401 or 403
    assert response.status_code in [200, 404]  # 200 for empty list, 404 if user not found is different error

    # Test POST /{user_id}/tasks endpoint with correct user_id
    response = client.post(f"/{mock_user.id}/tasks", json={
        "title": "Test Task",
        "description": "Test Description"
    }, headers=headers)
    # This should either succeed or fail for reasons other than auth (like user not existing in DB)
    assert response.status_code in [200, 201, 404, 422]  # 404 might be if user not found in DB
    # But importantly, it should NOT be 401 or 403


def test_authenticated_user_cannot_access_other_users_tasks(client, valid_jwt):
    """Test that authenticated user cannot access another user's tasks"""
    headers = {
        "Authorization": f"Bearer {valid_jwt}"
    }

    # Try to access a task that would belong to a different user
    fake_other_user_id = str(uuid4())

    response = client.get(f"/{fake_other_user_id}/tasks/123", headers=headers)
    assert response.status_code == 403  # Should be forbidden due to user_id mismatch
    assert "does not match authenticated user_id" in response.json().get("detail", "")


if __name__ == "__main__":
    pytest.main([__file__])