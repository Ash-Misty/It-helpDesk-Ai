from datetime import datetime
from typing import Dict, Any, Optional
from app.schemas.state import (
    AgentState,
    UserAnswer,
    WorkflowStage,
    StateStatus,
    ToolCall,
    ToolResultRecord,
    STAGE_TO_STATUS,
)
from app.state.state_store import state_store
from app.state.transitions import is_valid_transition


class StateManager:
    def __init__(self):
        self._store = state_store

    def _now(self) -> str:
        return datetime.utcnow().isoformat()

    def _to_stage(self, value) -> WorkflowStage:
        if isinstance(value, WorkflowStage):
            return value
        return WorkflowStage(value)

    def _to_status(self, value) -> StateStatus:
        if isinstance(value, StateStatus):
            return value
        return StateStatus(value)

    def _update_timestamp(self, state: AgentState) -> AgentState:
        state.updated_at = self._now()
        return state

    def initialize(self, ticket_id: str) -> Dict[str, Any]:
        existing = self._store.get(ticket_id)
        if existing is not None:
            return {
                "created": False,
                "already_exists": True,
                "state": existing.model_dump(),
            }

        ticket = ticket_service.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError("Ticket not found")

        agent_result = helpdesk_agent.analyze_ticket({
            "ticket_id": ticket.ticket_id,
            "user_query": ticket.user_query,
            "category": ticket.category,
            "subcategory": ticket.subcategory,
            "priority": ticket.priority,
            "confidence": ticket.confidence,
            "reason": ticket.reason,
            "status": ticket.status,
        })

        decision = agent_result.get("agent_decision")
        questions = decision.get("questions", []) if decision else []
        plan = decision.get("initial_plan", []) if decision else []

        agent_decision_obj = None
        if decision:
            from app.schemas.agent import AgentDecision
            try:
                agent_decision_obj = AgentDecision(**decision)
            except Exception:
                pass

        next_action = decision.get("next_action") if decision else "troubleshoot"

        if next_action == "escalate":
            stage = WorkflowStage.ESCALATION_REQUIRED
        elif next_action == "ask_information":
            stage = WorkflowStage.AWAITING_INFORMATION
        elif next_action == "resolve":
            stage = WorkflowStage.RESOLVED
        elif next_action == "recommend_solution":
            stage = WorkflowStage.PLANNING
        else:
            stage = WorkflowStage.PLANNING

        state = AgentState(
            ticket_id=ticket_id,
            user_query=ticket.user_query,
            category=ticket.category,
            subcategory=ticket.subcategory,
            priority=ticket.priority,
            current_stage=stage,
            agent_decision=agent_decision_obj,
            questions_asked=questions,
            current_plan=plan,
            current_step_index=0,
            last_action="agent_analysis",
            status=STAGE_TO_STATUS.get(stage, StateStatus.ACTIVE),
            created_at=self._now(),
            updated_at=self._now(),
        )

        self._store.create(state)

        return {
            "created": True,
            "already_exists": False,
            "state": state.model_dump(),
        }

    def get_state(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        state = self._store.get(ticket_id)
        if state is None:
            return None
        return state.model_dump()

    def update_stage(self, ticket_id: str, new_stage: str) -> Dict[str, Any]:
        state = self._store.get(ticket_id)
        if state is None:
            raise ValueError("State not found")

        target = WorkflowStage(new_stage)
        current = self._to_stage(state.current_stage)

        if not is_valid_transition(current, target):
            raise ValueError(
                f"Invalid transition from {current.value} to {target.value}"
            )

        state.current_stage = target
        state.status = STAGE_TO_STATUS.get(target, StateStatus.ACTIVE)
        state.last_action = f"stage_transition:{target.value}"
        self._update_timestamp(state)

        self._store.update(ticket_id, state)
        return state.model_dump()

    def add_answer(
        self, ticket_id: str, question: str, answer: str
    ) -> Dict[str, Any]:
        state = self._store.get(ticket_id)
        if state is None:
            raise ValueError("State not found")

        user_answer = UserAnswer(question=question, answer=answer)
        state.user_answers.append(user_answer)

        if question not in state.questions_asked:
            state.questions_asked.append(question)

        state.last_action = "user_answer_received"
        self._update_timestamp(state)
        self._store.update(ticket_id, state)
        return state.model_dump()

    def complete_step(self, ticket_id: str) -> Dict[str, Any]:
        state = self._store.get(ticket_id)
        if state is None:
            raise ValueError("State not found")

        if state.current_step_index >= len(state.current_plan):
            raise ValueError("No more steps to complete")

        current_step = state.current_plan[state.current_step_index]
        if current_step in state.completed_steps:
            raise ValueError(f"Step already completed: {current_step}")

        state.completed_steps.append(current_step)
        state.current_step_index += 1
        state.last_action = "step_completed"
        self._update_timestamp(state)
        self._store.update(ticket_id, state)
        return state.model_dump()

    def update_agent_decision(
        self, ticket_id: str, decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        state = self._store.get(ticket_id)
        if state is None:
            raise ValueError("State not found")

        from app.schemas.agent import AgentDecision
        try:
            agent_decision_obj = AgentDecision(**decision)
            state.agent_decision = agent_decision_obj

            if decision.get("questions") and isinstance(decision["questions"], list):
                for q in decision["questions"]:
                    if q not in state.questions_asked:
                        state.questions_asked.append(q)

            if decision.get("initial_plan") and isinstance(decision["initial_plan"], list):
                state.current_plan = decision["initial_plan"]
                state.current_step_index = 0

            state.last_action = "agent_reanalysis"
        except Exception:
            state.last_action = "agent_reanalysis_failed"

        self._update_timestamp(state)
        self._store.update(ticket_id, state)
        return state.model_dump()

    def record_tool_call(
        self, ticket_id: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        state = self._store.get(ticket_id)
        if state is None:
            raise ValueError("State not found")

        tool_call = ToolCall(tool_name=tool_name, arguments=arguments)
        state.tool_calls.append(tool_call)
        state.last_action = f"tool_call:{tool_name}"
        self._update_timestamp(state)
        self._store.update(ticket_id, state)
        return state.model_dump()

    def record_tool_result(
        self,
        ticket_id: str,
        tool_name: str,
        success: bool,
        result: Dict[str, Any],
        error: Optional[str] = None,
        execution_time_ms: float = 0,
        simulated: bool = True,
    ) -> Dict[str, Any]:
        state = self._store.get(ticket_id)
        if state is None:
            raise ValueError("State not found")

        tool_result = ToolResultRecord(
            tool_name=tool_name,
            success=success,
            result=result,
            error=error,
            execution_time_ms=execution_time_ms,
            simulated=simulated,
        )
        state.tool_results.append(tool_result)
        state.last_action = f"tool_result:{tool_name}"
        self._update_timestamp(state)
        self._store.update(ticket_id, state)
        return state.model_dump()

    def get_agent_context(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        state = self._store.get(ticket_id)
        if state is None:
            return None

        current_stage = self._to_stage(state.current_stage)
        current_status = self._to_status(state.status)

        context = {
            "ticket_id": state.ticket_id,
            "user_query": state.user_query,
            "category": state.category,
            "subcategory": state.subcategory,
            "priority": state.priority,
            "current_stage": current_stage.value,
            "current_plan": state.current_plan,
            "completed_steps": state.completed_steps,
            "current_step_index": state.current_step_index,
            "questions_asked": state.questions_asked,
            "user_answers": [a.model_dump() for a in state.user_answers],
            "last_action": state.last_action,
            "status": current_status.value,
            "tool_calls": [t.model_dump() for t in state.tool_calls],
            "tool_results": [t.model_dump() for t in state.tool_results],
        }
        return context


from app.services.ticket_service import ticket_service
from app.agents.helpdesk_agent import helpdesk_agent

state_manager = StateManager()
