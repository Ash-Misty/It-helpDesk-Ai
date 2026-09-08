from typing import Dict, Any, Optional
from app.state.state_manager import state_manager


class StateService:
    def __init__(self):
        self._manager = state_manager

    def initialize_state(self, ticket_id: str) -> Dict[str, Any]:
        return self._manager.initialize(ticket_id)

    def get_state(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        return self._manager.get_state(ticket_id)

    def update_stage(self, ticket_id: str, new_stage: str) -> Dict[str, Any]:
        return self._manager.update_stage(ticket_id, new_stage)

    def add_answer(
        self, ticket_id: str, question: str, answer: str
    ) -> Dict[str, Any]:
        return self._manager.add_answer(ticket_id, question, answer)

    def complete_step(self, ticket_id: str) -> Dict[str, Any]:
        return self._manager.complete_step(ticket_id)

    def update_agent_decision(
        self, ticket_id: str, decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._manager.update_agent_decision(ticket_id, decision)

    def get_agent_context(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        return self._manager.get_agent_context(ticket_id)

    def record_tool_call(
        self, ticket_id: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._manager.record_tool_call(ticket_id, tool_name, arguments)

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
        return self._manager.record_tool_result(
            ticket_id, tool_name, success, result, error, execution_time_ms, simulated
        )


state_service = StateService()
