from app.tools.base import BaseTool, ToolResult
import time


class CreateDiagnosticReportTool(BaseTool):
    name = "create_diagnostic_report"
    description = "Generates a diagnostic summary of the current troubleshooting session including prior tool results, current state, and recommendations."
    safe = True
    simulated = True
    input_schema = {"type": "object", "properties": {}, "required": []}

    def execute(self, arguments: dict) -> ToolResult:
        start = time.perf_counter()
        try:
            result = {
                "report_type": "diagnostic_summary",
                "findings": "Simulated diagnostic report. No actual system data was collected.",
                "recommendations": [
                    "Verify user credentials",
                    "Check network connectivity",
                    "Review application logs",
                ],
                "severity": "unknown",
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
