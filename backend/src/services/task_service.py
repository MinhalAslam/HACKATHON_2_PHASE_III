from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from ..models.task import Task, TaskCreate, TaskUpdate
from ..models.user import User
from fastapi import HTTPException, status


class TaskService:
    """
    Service layer for task-related business logic and operations.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_tasks_by_user(self, user_id: UUID) -> List[Task]:
        """Get all tasks for a specific user."""
        statement = select(Task).where(Task.user_id == user_id)
        return self.session.exec(statement).all()

    def create_task(self, task_create: TaskCreate, user_id: UUID) -> Task:
        """Create a new task for a user."""
        # Create the task with the provided data and user association
        db_task = Task(**task_create.model_dump(), user_id=user_id)

        self.session.add(db_task)
        self.session.commit()
        self.session.refresh(db_task)
        return db_task

    def get_task_by_id(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """Get a specific task by ID for a specific user."""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return self.session.exec(statement).first()

    def update_task(self, task_id: UUID, task_update: TaskUpdate, user_id: UUID) -> Optional[Task]:
        """Update a task for a specific user."""
        db_task = self.get_task_by_id(task_id, user_id)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update task fields
        task_data = task_update.model_dump(exclude_unset=True)
        for field, value in task_data.items():
            setattr(db_task, field, value)

        self.session.add(db_task)
        self.session.commit()
        self.session.refresh(db_task)
        return db_task

    def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete a task for a specific user."""
        db_task = self.get_task_by_id(task_id, user_id)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        self.session.delete(db_task)
        self.session.commit()
        return True

    def toggle_task_completion(self, task_id: UUID, completed: bool, user_id: UUID) -> Optional[Task]:
        """Toggle the completion status of a task."""
        db_task = self.get_task_by_id(task_id, user_id)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update completion status
        db_task.completed = completed

        self.session.add(db_task)
        self.session.commit()
        self.session.refresh(db_task)
        return db_task