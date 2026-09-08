from app.tools.base import BaseTool, ToolResult
import time
import random


class CheckInternetConnectionTool(BaseTool):
    name = "check_internet_connection"
    description = "Checks whether the user's device has an active internet connection by testing connectivity to a public DNS server."
    safe = True
    simulated = True
    input_schema = {"type": "object", "properties": {}, "required": []}

    def execute(self, arguments: dict) -> ToolResult:
        start = time.perf_counter()
        try:
            connected = True
            latency_ms = random.randint(10, 150)
            result = {
                "connected": connected,
                "latency_ms": latency_ms,
                "dns_server": "8.8.8.8",
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


class CheckDnsStatusTool(BaseTool):
    name = "check_dns_status"
    description = "Checks DNS resolution for a given domain to diagnose DNS-related connectivity issues."
    safe = True
    simulated = True
    input_schema = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "The domain name to resolve (e.g., 'example.com')",
                "minLength": 1,
                "maxLength": 255,
            }
        },
        "required": ["domain"],
    }

    def execute(self, arguments: dict) -> ToolResult:
        start = time.perf_counter()
        try:
            domain = arguments.get("domain", "example.com")
            if not isinstance(domain, str) or len(domain) < 1 or len(domain) > 255:
                raise ValueError("Invalid domain parameter")

            resolved = True
            resolved_ip = f"93.184.{random.randint(100, 199)}.{random.randint(10, 200)}"
            result = {
                "domain": domain,
                "resolved": resolved,
                "resolved_ip": resolved_ip,
                "dns_server": "8.8.8.8",
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
