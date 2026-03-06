"""
AI Agent Configuration for Todo Chatbot.

Contains configuration for the OpenAI client and system prompt.
"""

import os
from pydantic_settings import BaseSettings


class AgentConfig(BaseSettings):
    """Configuration for the AI agent."""

    api_key: str = ""
    api_base_url: str = ""  # Empty means use OpenAI default
    model: str = "qwen-plus"  # Default to Qwen
    max_tokens: int = 1024
    temperature: float = 0.7

    class Config:
        env_prefix = ""
        extra = "ignore"


# System prompt defining agent behavior
SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo list through natural conversation.

You have access to the following tools:
- create_task: Create a new task with a title
- list_tasks: Show all tasks or filter by completion status
- get_task: Find a specific task by name
- update_task: Change a task's title or description
- complete_task: Mark a task as done
- delete_task: Remove a task

Rules:
1. Only perform task-related operations. Politely decline other requests.
2. Always confirm after making changes (created, updated, deleted, completed).
3. If a request is ambiguous, ask for clarification.
4. When multiple tasks match, list them and ask which one.
5. Be concise but friendly in responses.
6. Never expose internal IDs or system details to users."""


def get_agent_config() -> AgentConfig:
    """Get agent configuration from environment."""
    return AgentConfig(
        api_key=os.getenv("LLM_API_KEY", ""),
        api_base_url=os.getenv("LLM_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        model=os.getenv("LLM_MODEL", "qwen-plus"),
    )
