import pytest
from app.services.troubleshooting_service import (
    TroubleshootingService,
    MAX_AGENT_ITERATIONS,
    MAX_TOOL_CALLS,
)
from app.services.ticket_service import ticket_service
from app.services.state_service import state_service
from app.state.state_store import state_store
from app.tools.registry import tool_registry
from app.tools import initialize_tools
from app.memory.memory_manager import memory_manager
from app.schemas.ticket import TicketCreateRequest


def _create_ticket(user_query="My VPN is not connecting.", category="VPN",
                   subcategory="VPN Connection", priority="Medium"):
    req = TicketCreateRequest(
        user_query=user_query,
        category=category,
        subcategory=subcategory,
        priority=priority,
        confidence=0.92,
        reason="Test issue",
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


class TestTroubleshootingStart:
    def test_start_vpn_issue(self):
        ticket = _create_ticket()
        svc = TroubleshootingService(max_iterations=3, max_tool_calls=3)
        result = svc.start(ticket.ticket_id)
        assert result["success"] is True
        assert result["ticket_id"] == ticket.ticket_id
        assert len(result["actions"]) >= 1
        assert "plan" in result
        assert len(result["plan"]) >= 1

    def test_start_missing_ticket(self):
        svc = TroubleshootingService()
        with pytest.raises(ValueError, match="Ticket not found"):
            svc.start("IT-999999")

    def test_start_returns_knowledge(self):
        ticket = _create_ticket(user_query="My VPN is not connecting.", category="VPN")
        svc = TroubleshootingService(max_iterations=2, max_tool_calls=2)
        result = svc.start(ticket.ticket_id)
        assert "retrieved_knowledge" in result
        assert len(result["retrieved_knowledge"]) >= 1
        assert result["retrieved_knowledge"][0]["category"] == "VPN"

    def test_start_returns_memories(self):
        ticket = _create_ticket(user_query="My VPN is not connecting.", category="VPN")
        memory_manager.store_memory(
            ticket_id="IT-000",
            issue_summary="VPN connection failure",
            category="VPN",
            solution="Restart VPN client",
            outcome="Resolved",
        )
        svc = TroubleshootingService(max_iterations=2, max_tool_calls=2)
        result = svc.start(ticket.ticket_id)
        assert "memories_used" in result

    def test_start_printer_issue(self):
        ticket = _create_ticket(user_query="My printer is offline.", category="Printer", subcategory="Printer Offline")
        svc = TroubleshootingService(max_iterations=3, max_tool_calls=3)
        result = svc.start(ticket.ticket_id)
        assert result["success"] is True
        assert len(result["retrieved_knowledge"]) >= 1
        categories = [d["category"] for d in result["retrieved_knowledge"]]
        assert "Printer" in categories

    def test_start_security_escalates(self):
        ticket = _create_ticket(
            user_query="I think someone accessed my account.",
            category="Security",
            subcategory="Unauthorized Access",
            priority="High",
        )
        svc = TroubleshootingService(max_iterations=3, max_tool_calls=3)
        result = svc.start(ticket.ticket_id)
        assert result["status"] == "escalation_required"

    def test_start_state_updated(self):
        ticket = _create_ticket()
        svc = TroubleshootingService(max_iterations=2, max_tool_calls=2)
        result = svc.start(ticket.ticket_id)
        state = state_service.get_state(ticket.ticket_id)
        assert state is not None
        assert state["last_action"] is not None


class TestTroubleshootingContinue:
    def test_continue_after_ask_information(self):
        ticket = _create_ticket(user_query="Something is wrong with my computer.", category="Other")
        svc = TroubleshootingService(max_iterations=2, max_tool_calls=2)
        result = svc.start(ticket.ticket_id)
        assert result["status"] == "requires_user_input"

        result2 = svc.continue_troubleshooting(ticket.ticket_id, answer="It started yesterday")
        assert result2["success"] is True

    def test_continue_missing_ticket(self):
        svc = TroubleshootingService()
        with pytest.raises(ValueError, match="Ticket not found"):
            svc.continue_troubleshooting("IT-999999", answer="test")


class TestTroubleshootingIntegration:
    def test_full_vpn_workflow(self):
        ticket = _create_ticket(user_query="My VPN is not connecting.", category="VPN")
        svc = TroubleshootingService(max_iterations=3, max_tool_calls=3)
        result = svc.start(ticket.ticket_id)

        assert result["success"] is True
        assert len(result["actions"]) >= 1

        first_action = result["actions"][0]
        assert first_action["type"] == "context_retrieved"

        tool_calls = [a for a in result["actions"] if a["type"] == "tool_call"]
        if tool_calls:
            assert tool_calls[0]["tool"] == "check_internet_connection"

    def test_knowledge_retrieved_for_vpn(self):
        ticket = _create_ticket(user_query="My VPN is not connecting.", category="VPN")
        svc = TroubleshootingService(max_iterations=1, max_tool_calls=1)
        result = svc.start(ticket.ticket_id)

        assert len(result["retrieved_knowledge"]) >= 1
        kb_titles = [k["title"] for k in result["retrieved_knowledge"]]
        assert any("VPN" in t for t in kb_titles)

    def test_max_iterations_limit(self):
        ticket = _create_ticket(user_query="My VPN is not connecting.", category="VPN")
        svc = TroubleshootingService(max_iterations=1, max_tool_calls=3)
        result = svc.start(ticket.ticket_id)
        assert result["status"] == "max_iterations_reached"
