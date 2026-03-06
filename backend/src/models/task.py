from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from typing import TYPE_CHECKING
    from .user import User


class TaskBase(SQLModel):
    title: str = Field(nullable=False, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: uuid.UUID = Field(foreign_key="user.id")


class Task(TaskBase, table=True):
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: "User" = Relationship(back_populates="tasks")


class TaskCreate(SQLModel):
    title: str = Field(nullable=False, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskRead(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    completed: Optional[bool] = Field(default=None)