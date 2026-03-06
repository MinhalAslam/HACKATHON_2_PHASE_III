"""
Message model for AI Chatbot.

Represents a single chat message in a conversation.
Messages are immutable after creation.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from enum import Enum
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"


class MessageBase(SQLModel):
    """Base message fields shared across schemas."""
    role: MessageRole
    content: str = Field(nullable=False)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True)


class Message(MessageBase, table=True):
    """Message database model. Immutable after creation."""
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Note: No updated_at field - messages are immutable

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageCreate(SQLModel):
    """Schema for creating a message."""
    content: str = Field(nullable=False, min_length=1)
    role: MessageRole = MessageRole.USER


class MessageRead(MessageBase):
    """Schema for reading a message."""
    id: uuid.UUID
    created_at: datetime
