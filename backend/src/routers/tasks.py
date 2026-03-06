from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from ..database.database import get_session
from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate
from ..models.user import User
from ..utils.auth import get_current_user, get_current_user_id, verify_url_user_id_matches_token
from ..services.task_service import TaskService

router = APIRouter()


@router.get("/tasks", response_model=List[TaskRead])
def read_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve all tasks for a specific user.
    """
    # Verify that the URL user_id matches the authenticated user_id
    verify_url_user_id_matches_token(user_id, current_user_id)

    # Convert string IDs to UUID for comparison
    user_uuid = UUID(user_id)

    # Use service layer
    task_service = TaskService(session)
    tasks = task_service.get_tasks_by_user(user_uuid)
    return tasks


@router.post("/tasks", response_model=TaskRead)
def create_task(
    user_id: str,
    task: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.
    """
    # Verify that the URL user_id matches the authenticated user_id
    verify_url_user_id_matches_token(user_id, current_user_id)

    # Convert string IDs to UUID for comparison
    user_uuid = UUID(user_id)

    # Use service layer
    task_service = TaskService(session)
    db_task = task_service.create_task(task, user_uuid)
    return db_task


@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(
    user_id: str,
    task_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific task by ID.
    """
    # Verify that the URL user_id matches the authenticated user_id
    verify_url_user_id_matches_token(user_id, current_user_id)

    # Convert string IDs to UUID for comparison
    user_uuid = UUID(user_id)

    # Use service layer
    task_service = TaskService(session)
    task = task_service.get_task_by_id(task_id, user_uuid)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: str,
    task_id: UUID,
    task_update: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Update an existing task.
    """
    # Verify that the URL user_id matches the authenticated user_id
    verify_url_user_id_matches_token(user_id, current_user_id)

    # Convert string IDs to UUID for comparison
    user_uuid = UUID(user_id)

    # Use service layer
    task_service = TaskService(session)
    db_task = task_service.update_task(task_id, task_update, user_uuid)
    return db_task


@router.delete("/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete a task.
    """
    # Verify that the URL user_id matches the authenticated user_id
    verify_url_user_id_matches_token(user_id, current_user_id)

    # Convert string IDs to UUID for comparison
    user_uuid = UUID(user_id)

    # Use service layer
    task_service = TaskService(session)
    task_service.delete_task(task_id, user_uuid)
    return {"message": "Task deleted successfully"}


@router.patch("/tasks/{task_id}/complete")
def toggle_task_completion(
    user_id: str,
    task_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status.
    Frontend sends PATCH without body - backend auto-toggles.
    """
    # Verify that the URL user_id matches the authenticated user_id
    verify_url_user_id_matches_token(user_id, current_user_id)

    # Convert string IDs to UUID for comparison
    user_uuid = UUID(user_id)

    # Get the task first to toggle its current state
    task_service = TaskService(session)
    task = task_service.get_task_by_id(task_id, user_uuid)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Toggle the completion status
    new_status = not task.completed
    db_task = task_service.toggle_task_completion(task_id, new_status, user_uuid)
    return db_task