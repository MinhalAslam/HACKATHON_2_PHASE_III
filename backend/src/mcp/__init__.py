"""
MCP (Model Context Protocol) package for AI Chatbot.

This package provides MCP tools for task management operations
that the AI agent can invoke to interact with the task database.
"""

from .server import tool_registry, MCPToolRegistry
from .tools import (
    create_task,
    list_tasks,
    get_task,
    update_task,
    complete_task,
    delete_task,
    register_tools,
)

__all__ = [
    "tool_registry",
    "MCPToolRegistry",
    "create_task",
    "list_tasks",
    "get_task",
    "update_task",
    "complete_task",
    "delete_task",
    "register_tools",
]
