"""
Task Agent Runner for AI Chatbot.

Handles conversation with OpenAI and tool invocation for task management.
"""

import json
from typing import List, Dict, Any
from openai import OpenAI

from .config import get_agent_config, SYSTEM_PROMPT
from ..mcp.server import tool_registry
from ..mcp import tools  # Import to ensure tools are registered


class TaskAgent:
    """
    AI Agent for task management conversations.

    Uses OpenAI's function calling to invoke MCP tools for task operations.
    """

    def __init__(self, user_id: str):
        """
        Initialize the agent with user context.

        Args:
            user_id: The ID of the user interacting with the agent
        """
        self.user_id = user_id
        self.config = get_agent_config()
        # Support OpenAI-compatible APIs (Qwen, Groq, etc.)
        client_kwargs = {"api_key": self.config.api_key}
        if self.config.api_base_url:
            client_kwargs["base_url"] = self.config.api_base_url
        self.client = OpenAI(**client_kwargs)

    def run(self, messages: List[Dict[str, str]]) -> str:
        """
        Process a conversation and return the agent's response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys

        Returns:
            The agent's response text
        """
        # Prepare messages with system prompt
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages

        # Get tools for function calling
        tools_list = tool_registry.get_openai_tools()

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=full_messages,
                tools=tools_list if tools_list else None,
                tool_choice="auto" if tools_list else None,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )

            return self._process_response(response, full_messages)

        except Exception as e:
            return f"I apologize, but I encountered an error processing your request. Please try again."

    def _process_response(self, response, messages: List[Dict[str, str]]) -> str:
        """
        Process OpenAI response, handling tool calls if present.

        Args:
            response: OpenAI API response
            messages: Current conversation messages

        Returns:
            Final response text after processing any tool calls
        """
        choice = response.choices[0]
        message = choice.message

        # If no tool calls, return the content directly
        if not message.tool_calls:
            return message.content or "I understand. How can I help you with your tasks?"

        # Process tool calls
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        # Execute each tool call
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            # Inject user_id into all tool calls for security
            arguments["user_id"] = self.user_id

            # Execute the tool
            result = tool_registry.execute(tool_name, **arguments)

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        # Get final response after tool execution
        try:
            final_response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            return final_response.choices[0].message.content or "Done!"
        except Exception as e:
            return "I completed the operation but encountered an error generating the response."


def run_agent(messages: List[Dict[str, str]], user_id: str) -> str:
    """
    Convenience function to run the agent with a conversation.

    Args:
        messages: List of conversation messages
        user_id: The user's ID for tool invocation

    Returns:
        The agent's response
    """
    agent = TaskAgent(user_id)
    return agent.run(messages)
