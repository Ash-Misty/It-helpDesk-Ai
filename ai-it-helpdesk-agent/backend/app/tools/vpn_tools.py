from app.tools.base import BaseTool, ToolResult
import time
import random


class CheckVpnStatusTool(BaseTool):
    name = "check_vpn_status"
    description = "Checks the status of the VPN client to determine whether a VPN connection is active, connected, or in a failed state."
    safe = True
    simulated = True
    input_schema = {"type": "object", "properties": {}, "required": []}

    def execute(self, arguments: dict) -> ToolResult:
        start = time.perf_counter()
        try:
            connected = random.choice([True, False, False, True, False])
            if connected:
                result = {
                    "connected": True,
                    "status": "connected",
                    "server": "vpn.corporate.example.com",
                    "protocol": "OpenVPN",
                }
            else:
                result = {
                    "connected": False,
                    "status": "connection_failed",
                    "server": "vpn.corporate.example.com",
                    "error": random.choice(
                        ["authentication_failed", "server_unreachable", "certificate_error"]
                    ),
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
