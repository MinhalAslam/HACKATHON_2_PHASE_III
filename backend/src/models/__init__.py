# Import all models to ensure they are registered with SQLModel
# This prevents circular import issues with relationships
from .user import User, UserCreate, UserLogin, UserRead, UserUpdate, UserRole
from .task import Task, TaskCreate, TaskRead, TaskUpdate
from .conversation import Conversation, ConversationCreate, ConversationRead, ConversationSummary
from .message import Message, MessageCreate, MessageRead, MessageRole

__all__ = [
    "User",
    "UserCreate",
    "UserLogin",
    "UserRead",
    "UserUpdate",
    "UserRole",
    "Task",
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
    "Conversation",
    "ConversationCreate",
    "ConversationRead",
    "ConversationSummary",
    "Message",
    "MessageCreate",
    "MessageRead",
    "MessageRole",
]
