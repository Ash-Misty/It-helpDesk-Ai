"""Unit tests for Module 5: Agent State Management."""
import time
import pytest
from app.services.ticket_service import ticket_service
from app.services.state_service import state_service
from app.schemas.state import (
    WorkflowStage,
    StateStatus,
)
from app.state.state_store import state_store
from app.state.transitions import is_valid_transition, get_valid_next_stages


@pytest.fixture(autouse=True)
def clean_state():
    state_store.clear()
    ticket_service.tickets.clear()
    ticket_service.counter = 0
    yield
    state_store.clear()
    ticket_service.tickets.clear()
    ticket_service.counter = 0


def _create_ticket():
    from app.schemas.ticket import TicketCreateRequest
    req = TicketCreateRequest(
        user_query="My VPN is not connecting.",
        category="VPN",
        subcategory="VPN Connection",
        priority="Medium",
        confidence=0.92,
        reason="VPN connection issue",
    )
    return ticket_service.create_ticket(req)


def test_state_initialization():
    ticket = _create_ticket()
    result = state_service.initialize_state(ticket.ticket_id)
    assert result["created"] is True
    assert result["already_exists"] is False
    assert result["state"]["ticket_id"] == ticket.ticket_id
    assert result["state"]["status"] == StateStatus.ACTIVE.value


def test_state_initialization_already_exists():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    result = state_service.initialize_state(ticket.ticket_id)
    assert result["already_exists"] is True
    assert result["created"] is False


def test_state_initialization_nonexistent_ticket():
    with pytest.raises(ValueError, match="Ticket not found"):
        state_service.initialize_state("IT-999999")


def test_get_state():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state = state_service.get_state(ticket.ticket_id)
    assert state is not None
    assert state["ticket_id"] == ticket.ticket_id


def test_get_state_nonexistent():
    state = state_service.get_state("IT-999999")
    assert state is None


def test_valid_transition():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state = state_service.update_stage(
        ticket.ticket_id, WorkflowStage.PLANNING.value
    )
    assert state["current_stage"] == WorkflowStage.PLANNING.value


def test_invalid_transition_resolved_to_troubleshooting():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state_service.update_stage(ticket.ticket_id, WorkflowStage.TROUBLESHOOTING.value)
    state_service.update_stage(ticket.ticket_id, WorkflowStage.VERIFYING.value)
    state_service.update_stage(ticket.ticket_id, WorkflowStage.RESOLVED.value)
    with pytest.raises(ValueError, match="Invalid transition"):
        state_service.update_stage(
            ticket.ticket_id, WorkflowStage.TROUBLESHOOTING.value
        )


def test_update_stage_nonexistent_state():
    with pytest.raises(ValueError, match="State not found"):
        state_service.update_stage("IT-999999", WorkflowStage.PLANNING.value)


def test_add_answer():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state = state_service.add_answer(
        ticket.ticket_id,
        "Are you connected to the internet?",
        "Yes",
    )
    assert len(state["user_answers"]) == 1
    assert state["user_answers"][0]["answer"] == "Yes"
    assert state["user_answers"][0]["question"] == "Are you connected to the internet?"
    assert state["last_action"] == "user_answer_received"


def test_add_answer_nonexistent_state():
    with pytest.raises(ValueError, match="State not found"):
        state_service.add_answer("IT-999999", "test", "yes")


def test_complete_step():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state = state_service.complete_step(ticket.ticket_id)
    assert len(state["completed_steps"]) == 1
    assert state["current_step_index"] == 1
    assert state["last_action"] == "step_completed"


def test_complete_step_duplicate_prevention():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)

    from app.state.state_store import state_store as store
    raw_state = store.get(ticket.ticket_id)
    raw_state.current_plan = ["Step A", "Step B"]
    store.update(ticket.ticket_id, raw_state)

    state_service.complete_step(ticket.ticket_id)
    assert len(store.get(ticket.ticket_id).completed_steps) == 1

    raw_state2 = store.get(ticket.ticket_id)
    raw_state2.current_step_index = 0
    store.update(ticket.ticket_id, raw_state2)

    with pytest.raises(ValueError, match="Step already completed"):
        state_service.complete_step(ticket.ticket_id)


def test_complete_step_no_more_steps():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)

    from app.state.state_store import state_store as store
    raw_state = store.get(ticket.ticket_id)
    raw_state.current_plan = ["Only step"]
    store.update(ticket.ticket_id, raw_state)

    state_service.complete_step(ticket.ticket_id)
    with pytest.raises(ValueError, match="No more steps"):
        state_service.complete_step(ticket.ticket_id)


def test_complete_step_nonexistent_state():
    with pytest.raises(ValueError, match="State not found"):
        state_service.complete_step("IT-999999")


def test_is_valid_transition():
    assert is_valid_transition(WorkflowStage.PLANNING, WorkflowStage.TROUBLESHOOTING) is True
    assert is_valid_transition(WorkflowStage.RESOLVED, WorkflowStage.TROUBLESHOOTING) is False
    assert is_valid_transition(WorkflowStage.CREATED, WorkflowStage.ANALYZING) is True


def test_get_valid_next_stages():
    next_stages = get_valid_next_stages(WorkflowStage.ANALYZING)
    assert WorkflowStage.PLANNING in next_stages
    assert WorkflowStage.AWAITING_INFORMATION in next_stages
    assert WorkflowStage.ESCALATION_REQUIRED in next_stages
    assert WorkflowStage.RESOLVED not in next_stages


def test_state_timestamps_update():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state = state_service.get_state(ticket.ticket_id)
    original_updated = state["updated_at"]

    time.sleep(0.01)

    state_service.add_answer(
        ticket.ticket_id, "test question", "test answer"
    )
    state2 = state_service.get_state(ticket.ticket_id)
    assert state2["updated_at"] != original_updated
    assert state["created_at"] == state2["created_at"]


def test_get_agent_context():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state_service.add_answer(ticket.ticket_id, "Are you connected?", "Yes")
    context = state_service.get_agent_context(ticket.ticket_id)
    assert context is not None
    assert context["ticket_id"] == ticket.ticket_id
    assert len(context["user_answers"]) == 1
    assert context["user_answers"][0]["answer"] == "Yes"
    assert "questions_asked" in context
    assert "current_plan" in context


def test_get_agent_context_nonexistent_state():
    context = state_service.get_agent_context("IT-999999")
    assert context is None


def test_state_persists_after_updates():
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state_service.add_answer(ticket.ticket_id, "Q1", "A1")
    state_service.add_answer(ticket.ticket_id, "Q2", "A2")
    state_service.complete_step(ticket.ticket_id)
    state = state_service.get_state(ticket.ticket_id)
    assert len(state["user_answers"]) == 2
    assert len(state["completed_steps"]) == 1
    assert state["current_step_index"] == 1


def test_duplicate_answer_allowed():
    """Adding the same question twice should work (both stored)."""
    ticket = _create_ticket()
    state_service.initialize_state(ticket.ticket_id)
    state_service.add_answer(ticket.ticket_id, "Q1", "A1")
    state_service.add_answer(ticket.ticket_id, "Q1", "Updated")
    state = state_service.get_state(ticket.ticket_id)
    assert len(state["user_answers"]) == 2
