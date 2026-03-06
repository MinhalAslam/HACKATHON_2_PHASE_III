# Data Model: Todo AI Chatbot

**Feature**: 001-ai-chatbot
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document defines the database entities required for the AI Chatbot feature. Two new entities are introduced: `Conversation` and `Message`. These extend the existing schema without modifying the `User` or `Task` tables.

---

## Entity Relationship Diagram

```
┌──────────────┐       ┌────────────────┐       ┌─────────────┐
│    User      │       │  Conversation  │       │   Message   │
├──────────────┤       ├────────────────┤       ├─────────────┤
│ id (PK)      │──1:N──│ id (PK)        │──1:N──│ id (PK)     │
│ email        │       │ user_id (FK)   │       │ conv_id(FK) │
│ ...          │       │ title          │       │ role        │
└──────────────┘       │ created_at     │       │ content     │
       │               │ updated_at     │       │ created_at  │
       │               └────────────────┘       └─────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│    Task      │
├──────────────┤
│ id (PK)      │
│ user_id (FK) │
│ title        │
│ completed    │
│ ...          │
└──────────────┘
```

---

## Entity: Conversation

Represents a chat session between a user and the AI assistant.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid4() | Unique identifier |
| `user_id` | UUID | NOT NULL, FOREIGN KEY → User(id), ON DELETE CASCADE | Owner of the conversation |
| `title` | VARCHAR(200) | NULLABLE | Optional title (auto-generated or user-provided) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | When conversation started |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT now() | Last activity timestamp |

### Indexes

- `idx_conversation_user_id` on `user_id` - For listing user's conversations
- `idx_conversation_updated_at` on `updated_at` - For sorting by recency

### Relationships

- **User**: Many-to-One (many conversations belong to one user)
- **Message**: One-to-Many (one conversation has many messages)

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class ConversationBase(SQLModel):
    title: Optional[str] = Field(default=None, max_length=200)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)


class Conversation(ConversationBase, table=True):
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationCreate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=200)


class ConversationRead(ConversationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConversationSummary(SQLModel):
    id: uuid.UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
```

---

## Entity: Message

Represents a single message in a conversation. Messages are immutable after creation.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid4() | Unique identifier |
| `conversation_id` | UUID | NOT NULL, FOREIGN KEY → Conversation(id), ON DELETE CASCADE | Parent conversation |
| `role` | VARCHAR(20) | NOT NULL, CHECK IN ('user', 'assistant') | Who sent the message |
| `content` | TEXT | NOT NULL | Message text content |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | When message was created |

### Indexes

- `idx_message_conversation_id` on `conversation_id` - For loading conversation history
- `idx_message_created_at` on `created_at` - For ordering messages

### Relationships

- **Conversation**: Many-to-One (many messages belong to one conversation)

### Immutability Constraint

Messages have **no `updated_at` field** and **no update endpoint**. Once created, message content cannot be modified. This is enforced at the application level by not exposing update operations.

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from enum import Enum
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageBase(SQLModel):
    role: MessageRole
    content: str = Field(nullable=False)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True)


class Message(MessageBase, table=True):
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageCreate(SQLModel):
    content: str = Field(nullable=False, min_length=1)


class MessageRead(MessageBase):
    id: uuid.UUID
    created_at: datetime
```

---

## User Model Updates

The existing `User` model requires a new relationship to conversations.

### Addition to User Model

```python
# In backend/src/models/user.py, add to User class:

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation

class User(UserBase, table=True):
    # ... existing fields ...

    # Add this relationship
    conversations: List["Conversation"] = Relationship(back_populates="user")
```

---

## Database Migration

### Migration Script (Alembic-style)

```python
"""Add conversation and message tables for AI chatbot

Revision ID: 001_add_chat_tables
Create Date: 2026-02-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create conversation table
    op.create_table(
        'conversation',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('idx_conversation_user_id', 'conversation', ['user_id'])
    op.create_index('idx_conversation_updated_at', 'conversation', ['updated_at'])

    # Create message table
    op.create_table(
        'message',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('conversation.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='ck_message_role'),
    )
    op.create_index('idx_message_conversation_id', 'message', ['conversation_id'])
    op.create_index('idx_message_created_at', 'message', ['created_at'])


def downgrade():
    op.drop_table('message')
    op.drop_table('conversation')
```

---

## Validation Rules

### Conversation

| Rule | Enforcement |
|------|-------------|
| User must exist | Foreign key constraint |
| Title max 200 chars | Field max_length |
| User can only access own conversations | Application-level query filter |

### Message

| Rule | Enforcement |
|------|-------------|
| Conversation must exist | Foreign key constraint |
| Role must be 'user' or 'assistant' | Check constraint + Enum |
| Content cannot be empty | Field nullable=False, min_length=1 |
| Messages are immutable | No update endpoint exposed |

---

## Query Patterns

### Get User's Conversations (sorted by recent activity)

```python
def get_user_conversations(session: Session, user_id: UUID) -> List[Conversation]:
    return session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()
```

### Get Conversation with Messages

```python
def get_conversation_with_messages(
    session: Session,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Tuple[Conversation, List[Message]]]:
    conversation = session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)  # Ownership check
    ).first()

    if not conversation:
        return None

    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    return conversation, messages
```

### Create Message (enforces immutability by design)

```python
def create_message(
    session: Session,
    conversation_id: UUID,
    role: MessageRole,
    content: str
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
```

---

## Data Integrity Guarantees

1. **User Isolation**: All queries filter by `user_id` from JWT token
2. **Cascade Delete**: Deleting a user removes all conversations and messages
3. **Referential Integrity**: Foreign keys prevent orphaned records
4. **Message Immutability**: No UPDATE operations exposed in API
5. **Conversation Ownership**: Enforced at query level, not just API level
