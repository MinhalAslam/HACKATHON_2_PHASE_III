"""
MCP Tool Registry for AI Chatbot.

Provides a registry for MCP tools that can be called by the AI agent.
Tools are registered with schemas that describe their parameters.
"""

from typing import Dict, Any, Callable, List
from dataclasses import dataclass, field


@dataclass
class ToolDefinition:
    """Definition of an MCP tool for OpenAI function calling."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., Dict[str, Any]]


class MCPToolRegistry:
    """
    Registry for MCP tools that can be called by the AI agent.

    Tools are registered with their schemas and handlers.
    The registry provides methods to get tool definitions for OpenAI
    and to execute tools by name.
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., Dict[str, Any]]
    ) -> None:
        """Register a tool with its schema and handler."""
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler
        )

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get a tool definition by name."""
        return self._tools.get(name)

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools formatted for OpenAI function calling.

        Returns a list of tool definitions in OpenAI's expected format.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            }
            for tool in self._tools.values()
        ]

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with the given arguments.

        Returns the tool's result as a dictionary.
        Raises KeyError if tool is not found.
        """
        tool = self._tools.get(name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{name}' not found"
            }

        try:
            return tool.handler(**kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())


# Global registry instance
tool_registry = MCPToolRegistry()
