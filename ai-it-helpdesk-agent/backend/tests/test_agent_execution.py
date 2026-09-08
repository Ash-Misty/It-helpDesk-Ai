import pytest
from app.services.ticket_service import ticket_service
from app.services.state_service import state_service
from app.services.agent_execution_service import AgentExecutionService, MAX_TOOL_CALLS
from app.state.state_store import state_store
from app.tools.registry import tool_registry
from app.tools import initialize_tools


def _create_ticket(user_query="My VPN is not connecting.", category="VPN",
                   subcategory="VPN Connection", priority="Medium"):
    from app.schemas.ticket import TicketCreateRequest
    req = TicketCreateRequest(
        user_query=user_query,
        category=category,
        subcategory=subcategory,
        priority=priority,
        confidence=0.92,
        reason="VPN connection issue",
    )
    return ticket_service.create_ticket(req)


@pytest.fixture(autouse=True)
def clean_all():
    state_store.clear()
    ticket_service.tickets.clear()
    ticket_service.counter = 0
    if not tool_registry.has("check_internet_connection"):
        initialize_tools()
    yield
    state_store.clear()
    ticket_service.tickets.clear()
    ticket_service.counter = 0


class TestAgentToolSelection:
    def test_vpn_ticket_selects_internet_then_vpn(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        assert result["success"] is True
        tool_actions = [a for a in result["actions"] if a["type"] == "tool_call"]
        assert len(tool_actions) >= 1

        first_tool = tool_actions[0]["tool"]
        assert first_tool == "check_internet_connection"

        if len(tool_actions) >= 2:
            second_tool = tool_actions[1]["tool"]
            assert second_tool == "check_vpn_status"

    def test_security_ticket_escalates(self):
        ticket = _create_ticket(
            user_query="I think someone accessed my account.",
            category="Security",
            subcategory="Unauthorized Access",
            priority="High",
        )
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        assert result["status"] == "escalated"
        escalate_actions = [a for a in result["actions"] if a["type"] == "escalate"]
        assert len(escalate_actions) == 1
        assert result["next_action"] == "escalate"

    def test_critical_ticket_escalates(self):
        ticket = _create_ticket(
            user_query="Our production server is down.",
            category="Operating System",
            subcategory="System Crash",
            priority="Critical",
        )
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        assert result["status"] == "escalated"
        assert result["next_action"] == "escalate"

    def test_unknown_issue_asks_information(self):
        ticket = _create_ticket(
            user_query="Something is wrong with my computer.",
            category="Other",
            subcategory="Unknown Issue",
            priority="Low",
        )
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        assert result["status"] == "requires_user_input"
        ask_actions = [a for a in result["actions"] if a["type"] == "ask_information"]
        assert len(ask_actions) == 1

    def test_internet_issue_selects_relevant_tools(self):
        ticket = _create_ticket(
            user_query="I cannot access the internet.",
            category="Network",
            subcategory="Internet Connectivity",
            priority="Medium",
        )
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        tool_actions = [a for a in result["actions"] if a["type"] == "tool_call"]
        assert len(tool_actions) >= 1
        assert tool_actions[0]["tool"] == "check_internet_connection"

    def test_does_not_force_single_tool(self):
        ticket = _create_ticket(
            user_query="My VPN keeps disconnecting.",
            category="VPN",
            subcategory="VPN Connection",
            priority="Medium",
        )
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        tool_actions = [a for a in result["actions"] if a["type"] == "tool_call"]
        tools_used = set(a["tool"] for a in tool_actions)
        assert "check_internet_connection" in tools_used

    def test_printer_issue_selects_application_tool(self):
        ticket = _create_ticket(
            user_query="My printer is offline.",
            category="Printer",
            subcategory="Printer Offline",
            priority="Medium",
        )
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        tool_actions = [a for a in result["actions"] if a["type"] == "tool_call"]
        assert len(tool_actions) >= 1
        assert tool_actions[0]["tool"] == "check_application_status"
        assert tool_actions[0]["arguments"]["application"] == "Print Spooler"


class TestMaxToolCalls:
    def test_max_tool_calls_limit(self):
        ticket = _create_ticket(
            user_query="My VPN is not connecting.",
            category="VPN",
            subcategory="VPN Connection",
            priority="Medium",
        )
        service = AgentExecutionService(max_tool_calls=2)
        result = service.execute(ticket.ticket_id)

        assert result["status"] == "max_tool_calls_reached"
        max_actions = [a for a in result["actions"] if a["type"] == "max_calls_reached"]
        assert len(max_actions) == 1

    def test_default_max_tool_calls_is_five(self):
        assert MAX_TOOL_CALLS == 5

    def test_state_records_all_tool_calls(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        service.execute(ticket.ticket_id)

        state = state_service.get_state(ticket.ticket_id)
        assert len(state["tool_results"]) >= 1
        assert len(state["tool_calls"]) >= 1

    def test_max_calls_exactly_reached(self):
        ticket = _create_ticket(
            user_query="My VPN is not connecting.",
            category="VPN",
            subcategory="VPN Connection",
            priority="Medium",
        )
        service = AgentExecutionService(max_tool_calls=1)
        result = service.execute(ticket.ticket_id)

        tool_actions = [a for a in result["actions"] if a["type"] == "tool_call"]
        assert len(tool_actions) == 1
        assert result["status"] == "max_tool_calls_reached"


class TestStateUpdateAfterExecution:
    def test_tool_results_stored_in_state(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        service.execute(ticket.ticket_id)

        state = state_service.get_state(ticket.ticket_id)
        assert len(state["tool_results"]) >= 1
        first_result = state["tool_results"][0]
        assert "tool_name" in first_result
        assert "success" in first_result
        assert "result" in first_result
        assert "timestamp" in first_result

    def test_tool_calls_stored_in_state(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        service.execute(ticket.ticket_id)

        state = state_service.get_state(ticket.ticket_id)
        assert len(state["tool_calls"]) >= 1
        first_call = state["tool_calls"][0]
        assert "tool_name" in first_call
        assert "arguments" in first_call
        assert "timestamp" in first_call

    def test_last_action_updated(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        service.execute(ticket.ticket_id)

        state = state_service.get_state(ticket.ticket_id)
        assert state["last_action"] is not None
        assert len(state["last_action"]) > 0

    def test_updated_at_changes_after_execution(self):
        ticket = _create_ticket()
        state_service.initialize_state(ticket.ticket_id)
        state_before = state_service.get_state(ticket.ticket_id)

        service = AgentExecutionService(max_tool_calls=5)
        service.execute(ticket.ticket_id)

        state_after = state_service.get_state(ticket.ticket_id)
        assert state_after["updated_at"] != state_before["updated_at"]

    def test_tool_history_preserved(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        service.execute(ticket.ticket_id)

        state = state_service.get_state(ticket.ticket_id)
        tool_results = state["tool_results"]
        assert len(tool_results) >= 1
        for tr in tool_results:
            assert tr["simulated"] is True

    def test_no_tools_overwrite_previous_results(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        service.execute(ticket.ticket_id)

        state_after_first = state_service.get_state(ticket.ticket_id)
        count_after_first = len(state_after_first["tool_results"])

        service.execute(ticket.ticket_id)
        state_after_second = state_service.get_state(ticket.ticket_id)
        count_after_second = len(state_after_second["tool_results"])

        assert count_after_second >= count_after_first


class TestMissingTicket:
    def test_missing_ticket_raises_error(self):
        service = AgentExecutionService(max_tool_calls=5)
        with pytest.raises(ValueError, match="Ticket not found"):
            service.execute("IT-999999")


class TestMissingState:
    def test_missing_state_auto_initializes(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        assert result["success"] is True
        assert result["ticket_id"] == ticket.ticket_id
        state = state_service.get_state(ticket.ticket_id)
        assert state is not None
        assert state["ticket_id"] == ticket.ticket_id

    def test_missing_state_creates_tool_results(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        result = service.execute(ticket.ticket_id)

        state = state_service.get_state(ticket.ticket_id)
        assert len(state["tool_results"]) >= 1


class TestMalformedModelOutput:
    def test_malformed_decision_falls_back_gracefully(self):
        from app.agents.helpdesk_agent import helpdesk_agent

        decision = helpdesk_agent.decide_tool_use(
            {"ticket_id": "IT-000001", "user_query": "test"},
            state_context=None,
            available_tools=[],
        )
        assert decision["success"] is True
        assert decision["tool_decision"]["action"] in [
            "call_tool", "ask_information", "recommend_solution",
            "escalate", "resolve", "no_action",
        ]

    def test_tool_decision_validated_through_pydantic(self):
        from app.schemas.agent import ToolDecision
        d = ToolDecision(action="no_action", tool_name=None, arguments={}, reason="test")
        dumped = d.model_dump()
        assert dumped["action"] == "no_action"
        assert dumped["tool_name"] is None

    def test_invalid_action_falls_back_to_no_action(self):
        from app.agents.helpdesk_agent import helpdesk_agent

        class FakeInference:
            def decide_next_action(self, *args, **kwargs):
                return {"action": "delete_everything", "tool_name": None, "arguments": {}, "reason": "bad"}

        original = helpdesk_agent.inference
        helpdesk_agent.inference = FakeInference()
        try:
            decision = helpdesk_agent.decide_tool_use(
                {"ticket_id": "IT-000001", "user_query": "test"},
                state_context=None,
                available_tools=[],
            )
            assert decision["success"] is True
            assert decision["tool_decision"]["action"] == "no_action"
        finally:
            helpdesk_agent.inference = original

    def test_call_tool_without_tool_name_becomes_no_action(self):
        from app.agents.helpdesk_agent import helpdesk_agent

        class FakeInference:
            def decide_next_action(self, *args, **kwargs):
                return {
                    "action": "call_tool",
                    "tool_name": None,
                    "arguments": {},
                    "reason": "trying to call a tool but no name",
                }

        original = helpdesk_agent.inference
        helpdesk_agent.inference = FakeInference()
        try:
            decision = helpdesk_agent.decide_tool_use(
                {"ticket_id": "IT-000001", "user_query": "test"},
                state_context=None,
                available_tools=[],
            )
            assert decision["success"] is True
            assert decision["tool_decision"]["action"] == "no_action"
            assert "No tool specified" in decision["tool_decision"]["reason"]
        finally:
            helpdesk_agent.inference = original


class TestAgentExecutionErrorHandling:
    def test_tool_error_recorded_in_state(self):
        from app.tools.base import ToolResult
        from app.tools.executor import ToolExecutor
        from app.tools.registry import ToolRegistry

        class FailingTool:
            name = "error_tool"
            description = "fails"
            safe = True
            simulated = True
            input_schema = {"type": "object", "properties": {}, "required": []}

            def execute(self, arguments):
                raise RuntimeError("Intentional failure")

            def validate_arguments(self, arguments):
                return True, None

            def describe(self):
                return {"name": self.name, "description": self.description,
                        "safe": self.safe, "simulated": self.simulated,
                        "input_schema": self.input_schema}

        reg = ToolRegistry()
        reg.register(FailingTool())
        exec_obj = ToolExecutor(registry=reg, timeout_seconds=5)
        result = exec_obj.execute_tool("error_tool", {})
        assert result.success is False
        assert "Intentional failure" in result.error

    def test_executor_unknown_tool_safe(self):
        from app.tools.executor import tool_executor
        result = tool_executor.execute_tool("rm -rf /", {})
        assert result.success is False
        assert result.tool_name == "rm -rf /"

    def test_tool_result_has_simulated_flag(self):
        ticket = _create_ticket()
        service = AgentExecutionService(max_tool_calls=5)
        service.execute(ticket.ticket_id)

        state = state_service.get_state(ticket.ticket_id)
        for tr in state["tool_results"]:
            assert "simulated" in tr
            assert tr["simulated"] is True

    def test_tool_result_has_execution_time(self):
        from app.tools.executor import tool_executor
        result = tool_executor.execute_tool("check_internet_connection", {})
        assert result.execution_time_ms >= 0
        assert isinstance(result.execution_time_ms, float)
