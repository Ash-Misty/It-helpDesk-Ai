from app.tools.base import BaseTool, ToolResult
import time
import random


class CheckSystemStatusTool(BaseTool):
    name = "check_system_status"
    description = "Checks the overall system status including OS version, uptime, CPU usage, and available memory."
    safe = True
    simulated = True
    input_schema = {"type": "object", "properties": {}, "required": []}

    def execute(self, arguments: dict) -> ToolResult:
        start = time.perf_counter()
        try:
            result = {
                "os": "Windows 11",
                "uptime_hours": random.randint(1, 120),
                "cpu_usage_percent": round(random.uniform(5, 85), 1),
                "memory_available_gb": round(random.uniform(2, 16), 1),
                "memory_total_gb": 16,
            }
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool_name=self.name,
                success=True,
                result=result,
                execution_time_ms=round(elapsed, 2),
                simulated=True,
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(exc),
                execution_time_ms=round(elapsed, 2),
                simulated=True,
            )


class CheckDiskSpaceTool(BaseTool):
    name = "check_disk_space"
    description = "Checks available disk space on the system drive."
    safe = True
    simulated = True
    input_schema = {"type": "object", "properties": {}, "required": []}

    def execute(self, arguments: dict) -> ToolResult:
        start = time.perf_counter()
        try:
            used_gb = round(random.uniform(50, 200), 1)
            total_gb = 512
            result = {
                "drive": "C:",
                "total_gb": total_gb,
                "used_gb": used_gb,
                "free_gb": round(total_gb - used_gb, 1),
                "usage_percent": round((used_gb / total_gb) * 100, 1),
            }
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool_name=self.name,
                success=True,
                result=result,
                execution_time_ms=round(elapsed, 2),
                simulated=True,
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(exc),
                execution_time_ms=round(elapsed, 2),
                simulated=True,
            )


class CheckApplicationStatusTool(BaseTool):
    name = "check_application_status"
    description = "Checks the status of a specific application (e.g., VPN client, email client, browser) on the user's system."
    safe = True
    simulated = True
    input_schema = {
        "type": "object",
        "properties": {
            "application": {
                "type": "string",
                "description": "The name of the application to check (e.g., 'VPN Client', 'Outlook', 'Chrome')",
                "minLength": 1,
                "maxLength": 100,
            }
        },
        "required": ["application"],
    }

    def execute(self, arguments: dict) -> ToolResult:
        start = time.perf_counter()
        try:
            app_name = arguments.get("application", "Unknown")
            if not isinstance(app_name, str) or len(app_name) < 1 or len(app_name) > 100:
                raise ValueError("Invalid application parameter")

            running = random.choice([True, False, True])
            if running:
                result = {
                    "application": app_name,
                    "running": True,
                    "status": "running",
                    "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                }
            else:
                result = {
                    "application": app_name,
                    "running": False,
                    "status": "not_running",
                }
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool_name=self.name,
                success=True,
                result=result,
                execution_time_ms=round(elapsed, 2),
                simulated=True,
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(exc),
                execution_time_ms=round(elapsed, 2),
                simulated=True,
            )
