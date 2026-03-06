"""
MCP Tools for Task Management.

These tools are called by the AI agent to perform task operations.
Each tool accepts user_id for ownership verification and returns
structured responses.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlmodel import Session, select

from ..models.task import Task, TaskCreate, TaskUpdate
from ..services.task_service import TaskService
from ..database.session import get_session
from .server import tool_registry


def _serialize_task(task: Task) -> Dict[str, Any]:
    """Serialize a task to a dictionary for tool responses."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }


def create_task(user_id: str, title: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: The ID of the user creating the task
        title: The title of the task
        description: Optional description for the task

    Returns:
        Dictionary with success status and created task or error
    """
    try:
        with next(get_session()) as session:
            service = TaskService(session)
            task_data = TaskCreate(title=title, description=description or "")
            task = service.create_task(task_data, UUID(user_id))
            return {
                "success": True,
                "task": _serialize_task(task),
                "message": f"Task '{title}' created successfully."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }


def list_tasks(user_id: str, status: Optional[str] = None) -> Dict[str, Any]:
    """
    List all tasks for the user, optionally filtered by status.

    Args:
        user_id: The ID of the user
        status: Optional filter - "completed", "incomplete", or None for all

    Returns:
        Dictionary with success status and list of tasks or error
    """
    try:
        with next(get_session()) as session:
            service = TaskService(session)
            tasks = service.get_tasks_by_user(UUID(user_id))

            # Filter by status if specified
            if status == "completed":
                tasks = [t for t in tasks if t.completed]
            elif status == "incomplete":
                tasks = [t for t in tasks if not t.completed]

            if not tasks:
                return {
                    "success": True,
                    "tasks": [],
                    "message": "No tasks found." if status is None else f"No {status} tasks found."
                }

            return {
                "success": True,
                "tasks": [_serialize_task(t) for t in tasks],
                "message": f"Found {len(tasks)} task(s)."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}"
        }


def get_task(user_id: str, task_id: Optional[str] = None, title_search: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a specific task by ID or search by title.

    Args:
        user_id: The ID of the user
        task_id: Optional task ID to retrieve directly
        title_search: Optional title substring to search for

    Returns:
        Dictionary with success status and task(s) or error
    """
    try:
        with next(get_session()) as session:
            service = TaskService(session)

            if task_id:
                task = service.get_task_by_id(UUID(task_id), UUID(user_id))
                if task:
                    return {
                        "success": True,
                        "task": _serialize_task(task),
                        "message": f"Found task: {task.title}"
                    }
                return {
                    "success": False,
                    "error": "Task not found."
                }

            if title_search:
                tasks = service.get_tasks_by_user(UUID(user_id))
                matches = [t for t in tasks if title_search.lower() in t.title.lower()]

                if not matches:
                    return {
                        "success": False,
                        "error": f"No tasks found matching '{title_search}'."
                    }

                if len(matches) == 1:
                    return {
                        "success": True,
                        "task": _serialize_task(matches[0]),
                        "message": f"Found task: {matches[0].title}"
                    }

                return {
                    "success": True,
                    "tasks": [_serialize_task(t) for t in matches],
                    "message": f"Found {len(matches)} matching tasks. Please specify which one."
                }

            return {
                "success": False,
                "error": "Please provide either task_id or title_search."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get task: {str(e)}"
        }


def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a task's title or description.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        title: Optional new title
        description: Optional new description

    Returns:
        Dictionary with success status and updated task or error
    """
    try:
        if not title and description is None:
            return {
                "success": False,
                "error": "Please provide title or description to update."
            }

        with next(get_session()) as session:
            service = TaskService(session)
            update_data = TaskUpdate()
            if title:
                update_data.title = title
            if description is not None:
                update_data.description = description

            task = service.update_task(UUID(task_id), update_data, UUID(user_id))
            return {
                "success": True,
                "task": _serialize_task(task),
                "message": f"Task updated successfully."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }


def complete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed (or toggle completion).

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to complete

    Returns:
        Dictionary with success status and updated task or error
    """
    try:
        with next(get_session()) as session:
            service = TaskService(session)
            task = service.get_task_by_id(UUID(task_id), UUID(user_id))

            if not task:
                return {
                    "success": False,
                    "error": "Task not found."
                }

            # Toggle completion status
            new_status = not task.completed
            updated_task = service.toggle_task_completion(UUID(task_id), new_status, UUID(user_id))

            status_text = "completed" if new_status else "marked as incomplete"
            return {
                "success": True,
                "task": _serialize_task(updated_task),
                "message": f"Task '{updated_task.title}' {status_text}."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}"
        }


def delete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Delete a task.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to delete

    Returns:
        Dictionary with success status or error
    """
    try:
        with next(get_session()) as session:
            service = TaskService(session)
            task = service.get_task_by_id(UUID(task_id), UUID(user_id))

            if not task:
                return {
                    "success": False,
                    "error": "Task not found."
                }

            task_title = task.title
            service.delete_task(UUID(task_id), UUID(user_id))

            return {
                "success": True,
                "message": f"Task '{task_title}' deleted successfully."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }


def register_tools():
    """Register all MCP tools with the registry."""

    tool_registry.register(
        name="create_task",
        description="Create a new task with a title and optional description.",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID (UUID format)"
                },
                "title": {
                    "type": "string",
                    "description": "The title of the task"
                },
                "description": {
                    "type": "string",
                    "description": "Optional description for the task"
                }
            },
            "required": ["user_id", "title"]
        },
        handler=create_task
    )

    tool_registry.register(
        name="list_tasks",
        description="List all tasks for the user, optionally filtered by completion status.",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID (UUID format)"
                },
                "status": {
                    "type": "string",
                    "enum": ["completed", "incomplete"],
                    "description": "Optional filter: 'completed' or 'incomplete'"
                }
            },
            "required": ["user_id"]
        },
        handler=list_tasks
    )

    tool_registry.register(
        name="get_task",
        description="Get a specific task by ID or search by title.",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID (UUID format)"
                },
                "task_id": {
                    "type": "string",
                    "description": "The task ID to retrieve"
                },
                "title_search": {
                    "type": "string",
                    "description": "Search tasks by title (partial match)"
                }
            },
            "required": ["user_id"]
        },
        handler=get_task
    )

    tool_registry.register(
        name="update_task",
        description="Update a task's title or description.",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID (UUID format)"
                },
                "task_id": {
                    "type": "string",
                    "description": "The task ID to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title for the task"
                },
                "description": {
                    "type": "string",
                    "description": "New description for the task"
                }
            },
            "required": ["user_id", "task_id"]
        },
        handler=update_task
    )

    tool_registry.register(
        name="complete_task",
        description="Mark a task as completed or toggle its completion status.",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID (UUID format)"
                },
                "task_id": {
                    "type": "string",
                    "description": "The task ID to complete"
                }
            },
            "required": ["user_id", "task_id"]
        },
        handler=complete_task
    )

    tool_registry.register(
        name="delete_task",
        description="Delete a task permanently.",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID (UUID format)"
                },
                "task_id": {
                    "type": "string",
                    "description": "The task ID to delete"
                }
            },
            "required": ["user_id", "task_id"]
        },
        handler=delete_task
    )


# Register tools on module import
register_tools()
