import pytest
from app.schemas.agent import ToolDecision, VALID_TOOL_ACTIONS
from app.tools.base import BaseTool, ToolResult
from app.tools.registry import ToolRegistry
from app.tools.executor import ToolExecutor


class _AlwaysFailTool(BaseTool):
    name = "fail_tool"
    description = "A tool that always fails."
    safe = True
    simulated = True
    input_schema = {"type": "object", "properties": {}, "required": []}

    def execute(self, arguments):
        raise RuntimeError("Simulated failure.")


class _AlwaysOkTool(BaseTool):
    name = "ok_tool"
    description = "A tool that always succeeds."
    safe = True
    simulated = True
    input_schema = {
        "type": "object",
        "properties": {
            "value": {"type": "string", "minLength": 1, "maxLength": 10},
        },
        "required": ["value"],
    }

    def execute(self, arguments):
        return ToolResult(
            tool_name=self.name,
            success=True,
            result={"echo": arguments.get("value", "")},
        )


@pytest.fixture
def fresh_registry():
    reg = ToolRegistry()
    reg.register(_AlwaysOkTool())
    reg.register(_AlwaysFailTool())
    return reg


@pytest.fixture
def executor(fresh_registry):
    return ToolExecutor(registry=fresh_registry)


class TestToolRegistration:
    def test_register_and_retrieve(self, fresh_registry):
        tool = fresh_registry.get("ok_tool")
        assert tool is not None
        assert tool.name == "ok_tool"

    def test_has_registered_tool(self, fresh_registry):
        assert fresh_registry.has("ok_tool") is True
        assert fresh_registry.has("nonexistent") is False

    def test_unregister_tool(self, fresh_registry):
        assert fresh_registry.unregister("ok_tool") is True
        assert fresh_registry.has("ok_tool") is False
        assert fresh_registry.unregister("ok_tool") is False

    def test_list_tool_names(self, fresh_registry):
        names = fresh_registry.list_tool_names()
        assert "ok_tool" in names
        assert "fail_tool" in names

    def test_list_tool_descriptions(self, fresh_registry):
        descs = fresh_registry.list_tools()
        for d in descs:
            assert "name" in d
            assert "description" in d
            assert "safe" in d
            assert "simulated" in d
            assert "input_schema" in d

    def test_clear_registry(self, fresh_registry):
        fresh_registry.clear()
        assert len(fresh_registry.list_tool_names()) == 0

    def test_global_registry_has_seven_tools(self):
        from app.tools.registry import tool_registry
        from app.tools import initialize_tools
        initialize_tools()
        names = tool_registry.list_tool_names()
        assert "check_internet_connection" in names
        assert "check_dns_status" in names
        assert "check_vpn_status" in names
        assert "check_system_status" in names
        assert "check_disk_space" in names
        assert "check_application_status" in names
        assert "create_diagnostic_report" in names
        assert len(names) == 7


class TestToolDiscovery:
    def test_get_returns_none_for_unknown(self, fresh_registry):
        assert fresh_registry.get("does_not_exist") is None

    def test_describe_returns_metadata(self, fresh_registry):
        tool = fresh_registry.get("ok_tool")
        desc = tool.describe()
        assert desc["name"] == "ok_tool"
        assert desc["safe"] is True
        assert desc["simulated"] is True
        assert "properties" in desc["input_schema"]


class TestValidToolExecution:
    def test_execute_valid_tool(self, executor):
        result = executor.execute_tool("ok_tool", {"value": "hello"})
        assert result.success is True
        assert result.result == {"echo": "hello"}
        assert result.tool_name == "ok_tool"
        assert result.simulated is True
        assert result.execution_time_ms >= 0

    def test_execute_no_args_tool(self, executor):
        result = executor.execute_tool("fail_tool", {})
        assert result.success is False
        assert "Simulated failure" in (result.error or "")

    def test_result_has_timestamp(self, executor):
        result = executor.execute_tool("ok_tool", {"value": "test"})
        assert result.timestamp is not None
        assert len(result.timestamp) > 0

    def test_result_is_pydantic_model(self, executor):
        result = executor.execute_tool("ok_tool", {"value": "test"})
        assert isinstance(result, ToolResult)
        dump = result.model_dump()
        assert "tool_name" in dump
        assert "success" in dump
        assert "result" in dump


class TestUnknownTool:
    def test_unknown_tool_returns_failure(self, executor):
        result = executor.execute_tool("nonexistent_tool", {})
        assert result.success is False
        assert "not registered" in (result.error or "")

    def test_unknown_tool_does_not_execute(self, executor):
        result = executor.execute_tool("__import__('os').system('echo hack')", {})
        assert result.success is False


class TestInvalidArguments:
    def test_missing_required_argument(self, executor):
        result = executor.execute_tool("ok_tool", {})
        assert result.success is False
        assert "Missing required" in (result.error or "")

    def test_wrong_type_argument(self, fresh_registry, executor):
        result = executor.execute_tool("ok_tool", {"value": 12345})
        assert result.success is False
        assert "must be a string" in (result.error or "")

    def test_string_too_short(self, executor):
        result = executor.execute_tool("ok_tool", {"value": ""})
        assert result.success is False
        assert "at least" in (result.error or "")

    def test_string_too_long(self, executor):
        result = executor.execute_tool("ok_tool", {"value": "a" * 11})
        assert result.success is False
        assert "at most" in (result.error or "")

    def test_unknown_argument_rejected(self, executor):
        result = executor.execute_tool("ok_tool", {"value": "test", "extra": "bad"})
        assert result.success is False
        assert "Unknown argument" in (result.error or "")

    def test_non_dict_arguments(self, executor):
        result = executor.execute_tool("ok_tool", "not a dict")
        assert result.success is False
        assert "must be" in (result.error or "")

    def test_none_arguments_allowed(self, executor):
        result = executor.execute_tool("fail_tool", None)
        assert result.success is False
        assert "Simulated failure" in (result.error or "")

    def test_real_tool_dns_validation(self):
        from app.tools.executor import tool_executor
        result = tool_executor.execute_tool("check_dns_status", {})
        assert result.success is False
        assert "domain" in (result.error or "")

    def test_real_tool_dns_wrong_type(self):
        from app.tools.executor import tool_executor
        result = tool_executor.execute_tool("check_dns_status", {"domain": 123})
        assert result.success is False

    def test_real_tool_application_validation(self):
        from app.tools.executor import tool_executor
        result = tool_executor.execute_tool("check_application_status", {})
        assert result.success is False
        assert "application" in (result.error or "")


class TestToolFailure:
    def test_tool_exception_caught(self, executor):
        result = executor.execute_tool("fail_tool", {})
        assert result.success is False
        assert result.error is not None
        assert "Simulated failure" in result.error or "failed" in result.error.lower()

    def test_failure_includes_metadata(self, executor):
        result = executor.execute_tool("fail_tool", {})
        assert result.tool_name == "fail_tool"
        assert result.execution_time_ms >= 0
        assert result.simulated is True


class TestToolValidation:
    def test_tool_name_must_be_in_registry(self, executor):
        result = executor.execute_tool("rm -rf /", {})
        assert result.success is False

    def test_arguments_validated_before_execution(self, executor):
        result = executor.execute_tool("ok_tool", {"value": "test"})
        assert result.success is True
        bad = executor.execute_tool("ok_tool", {"value": "x" * 200})
        assert bad.success is False

    def test_base_tool_validate_passes_valid(self, fresh_registry):
        tool = fresh_registry.get("ok_tool")
        valid, error = tool.validate_arguments({"value": "hello"})
        assert valid is True
        assert error is None

    def test_base_tool_validate_fails_missing_required(self, fresh_registry):
        tool = fresh_registry.get("ok_tool")
        valid, error = tool.validate_arguments({})
        assert valid is False
        assert "Missing required" in error

    def test_base_tool_validate_fails_unknown_field(self, fresh_registry):
        tool = fresh_registry.get("ok_tool")
        valid, error = tool.validate_arguments({"value": "hello", "bad_field": "x"})
        assert valid is False
        assert "Unknown argument" in error

    def test_base_tool_validate_fails_type(self, fresh_registry):
        tool = fresh_registry.get("ok_tool")
        valid, error = tool.validate_arguments({"value": 123})
        assert valid is False
        assert "must be a string" in error


class TestToolDecisionSchema:
    def test_valid_call_tool_decision(self):
        d = ToolDecision(
            action="call_tool",
            tool_name="check_vpn_status",
            arguments={},
            reason="Testing VPN status.",
        )
        assert d.action == "call_tool"
        assert d.tool_name == "check_vpn_status"

    def test_invalid_action_rejected(self):
        with pytest.raises(Exception):
            ToolDecision(action="delete_file", tool_name="x", arguments={}, reason="nope")

    def test_call_tool_without_tool_name_is_valid_schema(self):
        d = ToolDecision(action="call_tool", tool_name=None, arguments={}, reason="test")
        assert d.action == "call_tool"
        assert d.tool_name is None

    def test_no_tool_name_for_non_call_action(self):
        d = ToolDecision(action="ask_information", tool_name=None, arguments={}, reason="need info")
        assert d.action == "ask_information"

    def test_extra_fields_rejected(self):
        with pytest.raises(Exception):
            ToolDecision(action="no_action", tool_name=None, arguments={}, reason="ok", extra_field="bad")

    def test_all_valid_actions_accepted(self):
        for action in VALID_TOOL_ACTIONS:
            if action == "call_tool":
                d = ToolDecision(action=action, tool_name="check_vpn", arguments={}, reason="test")
            else:
                d = ToolDecision(action=action, tool_name=None, arguments={}, reason="test")
            assert d.action == action


class TestToolExecutorDescriptions:
    def test_get_tool_descriptions(self, executor):
        descs = executor.get_tool_descriptions()
        assert len(descs) >= 2
        for d in descs:
            assert "name" in d
            assert "description" in d

    def test_get_tool_names(self, executor):
        names = executor.get_tool_names()
        assert "ok_tool" in names
        assert "fail_tool" in names

    def test_get_tool_descriptions_for_model(self):
        from app.tools.executor import tool_executor
        descs = tool_executor.get_tool_descriptions_for_model()
        assert len(descs) == 7
        for d in descs:
            assert "name" in d
            assert "parameters" in d
            assert "safe" in d
            assert "simulated" in d
