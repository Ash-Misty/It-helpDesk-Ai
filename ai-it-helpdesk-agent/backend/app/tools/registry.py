from typing import Dict, List, Any, Optional
from app.tools.base import BaseTool, ToolResult


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        return self._tools.pop(name, None) is not None

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> List[Dict[str, Any]]:
        return [tool.describe() for tool in self._tools.values()]

    def list_tool_names(self) -> List[str]:
        return list(self._tools.keys())

    def clear(self):
        self._tools.clear()


tool_registry = ToolRegistry()
