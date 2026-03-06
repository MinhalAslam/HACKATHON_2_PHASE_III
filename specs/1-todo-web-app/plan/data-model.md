# Data Model: Todo Full-Stack Web Application

## Entity Definitions

### User Entity
**Description**: Represents a registered user in the system

**Fields**:
- `id`: UUID (Primary Key)
  - Type: UUID string (generated)
  - Constraints: Unique, Not Null
  - Description: Unique identifier for the user
- `email`: String
  - Type: String(255)
  - Constraints: Unique, Not Null, Valid email format
  - Description: User's email address used for identification
- `created_at`: DateTime
  - Type: Timestamp
  - Constraints: Not Null, Auto-generated
  - Description: Time when the user account was created
- `updated_at`: DateTime
  - Type: Timestamp
  - Constraints: Not Null, Auto-updated
  - Description: Time when the user account was last updated

**Validation Rules**:
- Email must be in valid email format
- Email must be unique across all users
- ID must be a valid UUID format

### Task Entity
**Description**: Represents a todo item created by a user

**Fields**:
- `id`: UUID (Primary Key)
  - Type: UUID string (generated)
  - Constraints: Unique, Not Null
  - Description: Unique identifier for the task
- `title`: String
  - Type: String(200)
  - Constraints: Not Null, Min Length: 1
  - Description: Title or headline of the task
- `description`: Text
  - Type: Text (variable length)
  - Constraints: Optional
  - Description: Detailed description of the task
- `completed`: Boolean
  - Type: Boolean
  - Constraints: Not Null, Default: False
  - Description: Flag indicating if the task is completed
- `user_id`: UUID (Foreign Key)
  - Type: UUID string
  - Constraints: Not Null, References User.id
  - Description: ID of the user who owns this task
- `created_at`: DateTime
  - Type: Timestamp
  - Constraints: Not Null, Auto-generated
  - Description: Time when the task was created
- `updated_at`: DateTime
  - Type: Timestamp
  - Constraints: Not Null, Auto-updated
  - Description: Time when the task was last updated

**Validation Rules**:
- Title is required and must be at least 1 character
- Title must not exceed 200 characters
- user_id must reference an existing user
- completed flag can be either True or False
- Only the owner can modify the task

### JWT Token (Conceptual, not persisted)
**Description**: Authentication token structure for user identification

**Claims**:
- `sub`: Subject (user ID)
  - Type: UUID string
  - Purpose: Identifies the user principal
- `exp`: Expiration Time
  - Type: Integer (Unix timestamp)
  - Purpose: When the token expires
- `iat`: Issued At
  - Type: Integer (Unix timestamp)
  - Purpose: When the token was issued

## Relationships

### User to Task
- **Relationship Type**: One-to-Many
- **Description**: One user can have many tasks
- **Implementation**: Foreign Key from Task.user_id to User.id
- **Constraints**:
  - Cascade: No cascade deletion (tasks preserved if user deleted)
  - Referential Integrity: Task.user_id must reference valid User.id
  - Enforcement: Database-level foreign key constraint

## Database Schema (SQLModel Representation)

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class TaskBase(SQLModel):
    title: str = Field(nullable=False, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    user_id: uuid.UUID = Field(foreign_key="user.id")

class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: User = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    completed: Optional[bool] = Field(default=None)
```

## State Transitions

### Task Completion State
- **Initial State**: `completed = False`
- **Transition**: Can be toggled to `completed = True` or back to `completed = False`
- **Triggers**:
  - PATCH request to `/api/{user_id}/tasks/{id}/complete`
  - Direct PUT request to update the task
- **Guard Conditions**: User must be authenticated and own the task

## Data Validation Rules

### Business Logic Validation
- Users cannot access tasks that don't belong to them
- Task titles must be unique within a user's task list (optional, configurable)
- Tasks must be associated with a valid user
- Completed state can be toggled indefinitely

### API Level Validation
- All authenticated endpoints validate JWT presence and validity
- URL user_id must match the user ID in the JWT token
- Task operations validate ownership before execution
- Required fields are validated before database operations