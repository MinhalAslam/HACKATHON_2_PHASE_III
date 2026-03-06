"""
Conversation model for AI Chatbot.

Represents a chat session between a user and the AI assistant.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class ConversationBase(SQLModel):
    """Base conversation fields shared across schemas."""
    title: Optional[str] = Field(default=None, max_length=200)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)


class Conversation(ConversationBase, table=True):
    """Conversation database model."""
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ConversationCreate(SQLModel):
    """Schema for creating a conversation."""
    title: Optional[str] = Field(default=None, max_length=200)


class ConversationRead(ConversationBase):
    """Schema for reading a conversation."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConversationSummary(SQLModel):
    """Schema for conversation list with summary info."""
    id: uuid.UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message_preview: Optional[str] = None
