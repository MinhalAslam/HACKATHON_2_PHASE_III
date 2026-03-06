"""
End-to-End Testing for All User Flows

This test suite validates the complete user flows:
1. User Registration and Authentication
2. Secure Task Management
3. API Security and Authorization
"""

import pytest
import jwt
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app
from src.database.database import engine
from src.models.user import User
from src.models.task import Task
from sqlmodel import Session, select
from uuid import uuid4


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


def test_complete_user_registration_and_authentication_flow(client):
    """Test complete user registration and authentication flow"""
    # Step 1: Register a new user
    registration_data = {
        "email": "newuser@example.com",
        "password": "securepassword123"
    }

    response = client.post("/api/auth/register", json=registration_data)
    assert response.status_code == 200
    register_response = response.json()

    # Verify registration response contains user data
    assert "id" in register_response
    assert register_response["email"] == "newuser@example.com"

    user_id = register_response["id"]

    # Step 2: Login with registered credentials
    login_data = {
        "email": "newuser@example.com",
        "password": "securepassword123"
    }

    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    login_response = response.json()

    # Verify login response contains access token
    assert "access_token" in login_response
    assert login_response["token_type"] == "bearer"

    access_token = login_response["access_token"]

    # Step 3: Verify user can access their profile
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    profile_response = response.json()

    # Verify profile matches registered user
    assert profile_response["id"] == user_id
    assert profile_response["email"] == "newuser@example.com"


def test_secure_task_management_flow(client):
    """Test complete task management flow for an authenticated user"""
    # Step 1: Register and login a user
    registration_data = {
        "email": "taskuser@example.com",
        "password": "taskpassword123"
    }

    response = client.post("/api/auth/register", json=registration_data)
    assert response.status_code == 200

    login_data = {
        "email": "taskuser@example.com",
        "password": "taskpassword123"
    }

    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    login_response = response.json()
    access_token = login_response["access_token"]

    # Get user ID from profile
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    user_profile = response.json()
    user_id = user_profile["id"]

    # Step 2: Create a task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task description"
    }

    response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    assert response.status_code == 200
    created_task = response.json()

    # Verify task was created correctly
    assert created_task["title"] == "Test Task"
    assert created_task["description"] == "This is a test task description"
    assert created_task["completed"] == False
    assert created_task["user_id"] == user_id

    task_id = created_task["id"]

    # Step 3: Retrieve the task
    response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    retrieved_task = response.json()

    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Test Task"

    # Step 4: Update the task
    update_data = {
        "title": "Updated Test Task",
        "description": "Updated description",
        "completed": True
    }

    response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_task = response.json()

    assert updated_task["title"] == "Updated Test Task"
    assert updated_task["description"] == "Updated description"
    assert updated_task["completed"] == True

    # Step 5: Toggle task completion
    completion_data = {"completed": False}
    response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete", json=completion_data, headers=headers)
    assert response.status_code == 200
    toggled_task = response.json()

    assert toggled_task["completed"] == False

    # Step 6: Delete the task
    response = client.delete(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200

    # Verify task is deleted
    response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 404


def test_api_security_authorization_flow(client):
    """Test complete API security and authorization flow"""
    # Step 1: Register two different users
    user1_data = {
        "email": "user1@example.com",
        "password": "password123"
    }

    user2_data = {
        "email": "user2@example.com",
        "password": "password123"
    }

    response = client.post("/api/auth/register", json=user1_data)
    assert response.status_code == 200
    user1_profile = response.json()
    user1_id = user1_profile["id"]

    response = client.post("/api/auth/register", json=user2_data)
    assert response.status_code == 200
    user2_profile = response.json()
    user2_id = user2_profile["id"]

    # Step 2: Login as user1
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }

    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    user1_token = response.json()["access_token"]

    # Step 3: Login as user2
    login_data = {
        "email": "user2@example.com",
        "password": "password123"
    }

    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    user2_token = response.json()["access_token"]

    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # Step 4: Create a task for user1
    task_data = {
        "title": "User1's Private Task",
        "description": "This belongs to user1 only"
    }

    response = client.post(f"/api/{user1_id}/tasks", json=task_data, headers=user1_headers)
    assert response.status_code == 200
    user1_task = response.json()
    user1_task_id = user1_task["id"]

    # Step 5: Verify user1 can access their own task
    response = client.get(f"/api/{user1_id}/tasks/{user1_task_id}", headers=user1_headers)
    assert response.status_code == 200

    # Step 6: Verify user2 cannot access user1's task (even with correct URL but wrong token)
    # First, try with user2's token but user1's ID in URL - should fail
    response = client.get(f"/api/{user1_id}/tasks/{user1_task_id}", headers=user2_headers)
    assert response.status_code == 403  # Forbidden due to user_id mismatch

    # Then, try with user2's token and user2's ID in URL - should fail because task doesn't belong to user2
    response = client.get(f"/api/{user2_id}/tasks/{user1_task_id}", headers=user2_headers)
    assert response.status_code in [403, 404]  # Either forbidden or not found

    # Step 7: Test user_id mismatch protection
    # Try to access user1's endpoint with user2's token
    response = client.get(f"/api/{user1_id}/tasks", headers=user2_headers)
    assert response.status_code == 403  # Forbidden due to user_id mismatch

    response = client.get(f"/api/{user1_id}/tasks/{user1_task_id}", headers=user2_headers)
    assert response.status_code == 403  # Forbidden due to user_id mismatch

    # Step 8: Verify that requests without JWT fail
    response = client.get(f"/api/{user1_id}/tasks")
    assert response.status_code == 401  # Unauthorized


def test_end_to_end_logout_and_session_flow(client):
    """Test logout and session management flow"""
    # Step 1: Register and login user
    registration_data = {
        "email": "logoutuser@example.com",
        "password": "logoutpassword123"
    }

    response = client.post("/api/auth/register", json=registration_data)
    assert response.status_code == 200

    login_data = {
        "email": "logoutuser@example.com",
        "password": "logoutpassword123"
    }

    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 2: Verify authenticated access works
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200

    # Step 3: For this test, we can't fully test logout since it's frontend behavior,
    # but we can verify that removing the token makes requests fail
    # In real application, logout would remove the token from client storage
    response = client.get("/api/auth/me")  # No token provided
    assert response.status_code == 401  # Should fail without token


if __name__ == "__main__":
    pytest.main([__file__])