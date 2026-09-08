from app.tools.registry import tool_registry
from app.tools.network_tools import CheckInternetConnectionTool, CheckDnsStatusTool
from app.tools.vpn_tools import CheckVpnStatusTool
from app.tools.system_tools import (
    CheckSystemStatusTool,
    CheckDiskSpaceTool,
    CheckApplicationStatusTool,
)
from app.tools.diagnostic_tools import CreateDiagnosticReportTool


def initialize_tools():
    tool_registry.register(CheckInternetConnectionTool())
    tool_registry.register(CheckDnsStatusTool())
    tool_registry.register(CheckVpnStatusTool())
    tool_registry.register(CheckSystemStatusTool())
    tool_registry.register(CheckDiskSpaceTool())
    tool_registry.register(CheckApplicationStatusTool())
    tool_registry.register(CreateDiagnosticReportTool())


initialize_tools()
