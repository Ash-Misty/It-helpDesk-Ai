import time
import threading
from typing import Dict, Any, Optional, List
from app.tools.base import ToolResult
from app.tools.registry import tool_registry


class ToolExecutor:
    def __init__(self, registry=None, timeout_seconds: float = 30.0):
        self._registry = registry if registry is not None else tool_registry
        self._timeout_seconds = timeout_seconds

    def execute_tool(
        self, tool_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        if not self._registry.has(tool_name):
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result={},
                error=f"Unknown tool: '{tool_name}' is not registered.",
                execution_time_ms=0,
                simulated=False,
            )

        tool = self._registry.get(tool_name)
        args = arguments if arguments is not None else {}

        if not isinstance(args, dict):
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result={},
                error="Arguments must be a JSON object (dictionary).",
                execution_time_ms=0,
                simulated=tool.simulated,
            )

        valid, error = tool.validate_arguments(args)
        if not valid:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result={},
                error=f"Invalid arguments: {error}",
                execution_time_ms=0,
                simulated=tool.simulated,
            )

        start = time.perf_counter()
        try:
            result = self._execute_with_timeout(tool, args)
            elapsed = (time.perf_counter() - start) * 1000
            if result.execution_time_ms == 0:
                result.execution_time_ms = round(elapsed, 2)
            return result
        except TimeoutError as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result={},
                error=f"Tool execution timed out after {self._timeout_seconds}s: {exc}",
                execution_time_ms=round(elapsed, 2),
                simulated=tool.simulated,
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result={},
                error=f"Tool execution failed: {exc}",
                execution_time_ms=round(elapsed, 2),
                simulated=tool.simulated,
            )

    def _execute_with_timeout(self, tool, args: Dict[str, Any]) -> ToolResult:
        result_container: Dict[str, Any] = {}

        def _run():
            try:
                result_container["result"] = tool.execute(args)
            except Exception as exc:
                result_container["exception"] = exc

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=self._timeout_seconds)

        if thread.is_alive():
            raise TimeoutError(
                f"Tool '{tool.name}' did not complete within {self._timeout_seconds} seconds."
            )

        if "exception" in result_container:
            raise result_container["exception"]

        if "result" not in result_container:
            raise RuntimeError("Tool execution returned no result.")

        return result_container["result"]

    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        return self._registry.list_tools()

    def get_tool_names(self) -> List[str]:
        return self._registry.list_tool_names()

    def get_tool_descriptions_for_model(self) -> List[Dict[str, Any]]:
        descriptions: List[Dict[str, Any]] = []
        for tool in self._registry.list_tools():
            descriptions.append({
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool.get("input_schema", {}),
                "safe": tool["safe"],
                "simulated": tool["simulated"],
            })
        return descriptions


tool_executor = ToolExecutor()