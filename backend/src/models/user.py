from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime
from enum import Enum
from pydantic import computed_field

if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)
    role: UserRole = Field(default=UserRole.user)


class User(UserBase, table=True):
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

    # Relationship to conversations (Phase III)
    conversations: List["Conversation"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(SQLModel):
    email: Optional[str] = None