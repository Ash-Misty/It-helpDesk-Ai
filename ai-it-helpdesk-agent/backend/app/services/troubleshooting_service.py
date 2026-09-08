from typing import Dict, Any, List, Optional
from app.agents.helpdesk_agent import helpdesk_agent
from app.tools.executor import tool_executor
from app.tools.registry import tool_registry
from app.services.state_service import state_service
from app.services.ticket_service import ticket_service
from app.tools.base import ToolResult
from app.memory.memory_manager import memory_manager
from app.rag.pipeline import rag_pipeline
from app.schemas.troubleshooting import VALID_TROUBLESHOOT_ACTIONS


MAX_AGENT_ITERATIONS = 5
MAX_TOOL_CALLS = 5


class TroubleshootingService:
    def __init__(
        self,
        max_iterations: int = MAX_AGENT_ITERATIONS,
        max_tool_calls: int = MAX_TOOL_CALLS,
    ):
        self._max_iterations = max_iterations
        self._max_tool_calls = max_tool_calls
        self._tool_executor = tool_executor

    def _get_ticket_dict(self, ticket) -> Dict[str, Any]:
        return {
            "ticket_id": ticket.ticket_id,
            "user_query": ticket.user_query,
            "category": ticket.category,
            "subcategory": ticket.subcategory,
            "priority": ticket.priority,
            "confidence": ticket.confidence,
            "reason": ticket.reason,
            "status": ticket.status,
        }

    def _normalize_tool_result(self, tool_result: ToolResult) -> Dict[str, Any]:
        return {
            "tool_name": tool_result.tool_name,
            "success": tool_result.success,
            "result": tool_result.result,
            "error": tool_result.error,
            "execution_time_ms": tool_result.execution_time_ms,
            "simulated": tool_result.simulated,
            "timestamp": tool_result.timestamp,
        }

    def _retrieve_context(self, ticket: Dict[str, Any]) -> tuple[list[dict], str]:
        user_query = ticket.get("user_query", "")
        category = ticket.get("category", "")
        rag_result = rag_pipeline.search(query=user_query, top_k=3, category=category)
        rag_docs = rag_result.get("results", [])

        memory_result = memory_manager.retrieve_relevant_memories(
            query=user_query, category=category, top_k=2
        )
        memories = memory_result.get("memories", [])
        memory_context = memory_manager.build_memory_context(
            query=user_query, category=category, max_memories=2
        )
        return rag_docs, memory_context, memories

    def start(self, ticket_id: str) -> Dict[str, Any]:
        ticket = ticket_service.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError("Ticket not found")

        state = state_service.get_state(ticket_id)
        if state is None:
            init_result = state_service.initialize_state(ticket_id)
            state = init_result["state"]

        current_stage = state.get("current_stage", "")
        if current_stage in ("escalation_required", "resolved"):
            return self._build_response(
                ticket_id, state, [{"type": "no_action", "detail": f"Ticket is already in stage: {current_stage}"}],
                current_stage, [], [], next_action="no_action",
            )

        ticket_dict = self._get_ticket_dict(ticket)

        rag_docs, memory_context, memories = self._retrieve_context(ticket_dict)

        state_service.update_stage(ticket_id, "troubleshooting")

        actions: List[Dict[str, Any]] = []
        actions.append({
            "type": "context_retrieved",
            "detail": f"Retrieved {len(rag_docs)} knowledge documents and {len(memories)} relevant memories.",
            "data": {
                "rag_count": len(rag_docs),
                "memory_count": len(memories),
                "rag_titles": [d.get("title", "") for d in rag_docs],
            },
        })

        iteration = 0
        tool_calls_count = len(state_service.get_state(ticket_id).get("tool_results", []))

        while iteration < self._max_iterations:
            iteration += 1
            state_context = state_service.get_agent_context(ticket_id)

            decision = helpdesk_agent.decide_tool_use(
                ticket_dict,
                state_context=state_context,
                available_tools=tool_registry.list_tool_names(),
                previous_tool_results=None,
            )

            if not decision.get("success"):
                actions.append({
                    "type": "error",
                    "detail": "Agent decision failed. Awaiting user input.",
                })
                return self._build_response(
                    ticket_id, state, actions, "error",
                    rag_docs, memories, next_action="no_action",
                )

            tool_decision = decision.get("tool_decision", {})
            action = tool_decision.get("action", "no_action")
            tool_name = tool_decision.get("tool_name")
            arguments = tool_decision.get("arguments", {})

            if action == "call_tool" and tool_name and tool_calls_count < self._max_tool_calls:
                actions.append({
                    "type": "tool_call",
                    "tool": tool_name,
                    "arguments": arguments,
                    "reason": tool_decision.get("reason", ""),
                })

                state_service.record_tool_call(ticket_id, tool_name, arguments or {})
                tool_result = self._tool_executor.execute_tool(tool_name, arguments or {})
                result_record = self._normalize_tool_result(tool_result)

                state_service.record_tool_result(
                    ticket_id,
                    tool_name,
                    tool_result.success,
                    tool_result.result,
                    error=tool_result.error,
                    execution_time_ms=tool_result.execution_time_ms,
                    simulated=tool_result.simulated,
                )

                state = state_service.get_state(ticket_id)
                tool_calls_count += 1

                actions.append({
                    "type": "tool_result",
                    "tool": tool_name,
                    "success": tool_result.success,
                    "result": tool_result.result,
                    "error": tool_result.error,
                    "timestamp": tool_result.timestamp,
                    "execution_time_ms": tool_result.execution_time_ms,
                })

                if not tool_result.success:
                    actions.append({
                        "type": "tool_error",
                        "tool": tool_name,
                        "error": tool_result.error,
                    })
                    return self._build_response(
                        ticket_id, state, actions, "tool_error",
                        rag_docs, memories, next_action="no_action",
                    )

            elif action == "ask_information":
                actions.append({
                    "type": "ask_information",
                    "reason": tool_decision.get("reason", ""),
                })
                try:
                    state_service.update_stage(ticket_id, "awaiting_information")
                except ValueError:
                    pass
                state = state_service.get_state(ticket_id)
                return self._build_response(
                    ticket_id, state, actions, "requires_user_input",
                    rag_docs, memories, next_action="ask_information",
                )

            elif action == "escalate":
                actions.append({
                    "type": "escalate",
                    "reason": tool_decision.get("reason", ""),
                })
                try:
                    state_service.update_stage(ticket_id, "escalation_required")
                except ValueError:
                    pass
                state = state_service.get_state(ticket_id)
                return self._build_response(
                    ticket_id, state, actions, "escalated",
                    rag_docs, memories, next_action="escalate",
                )

            elif action == "recommend_solution":
                actions.append({
                    "type": "recommend_solution",
                    "reason": tool_decision.get("reason", ""),
                })
                try:
                    state_service.update_stage(ticket_id, "verifying")
                except ValueError:
                    pass
                state = state_service.get_state(ticket_id)
                return self._build_response(
                    ticket_id, state, actions, "solution_recommended",
                    rag_docs, memories, next_action="recommend_solution",
                )

            elif action == "resolve":
                actions.append({
                    "type": "resolve",
                    "reason": tool_decision.get("reason", ""),
                })
                try:
                    state_service.update_stage(ticket_id, "resolved")
                except ValueError:
                    pass
                state = state_service.get_state(ticket_id)
                return self._build_response(
                    ticket_id, state, actions, "completed",
                    rag_docs, memories, next_action="resolve",
                )

            else:
                actions.append({
                    "type": "no_action",
                    "reason": tool_decision.get("reason", "No action determined."),
                })
                state = state_service.get_state(ticket_id)
                return self._build_response(
                    ticket_id, state, actions, "awaiting_user",
                    rag_docs, memories, next_action="no_action",
                )

        state = state_service.get_state(ticket_id)
        return self._build_response(
            ticket_id, state, actions, "max_iterations_reached",
            rag_docs, memories, next_action="no_action",
        )

    def continue_troubleshooting(self, ticket_id: str, answer: Optional[str] = None) -> Dict[str, Any]:
        ticket = ticket_service.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError("Ticket not found")

        if answer:
            state = state_service.get_state(ticket_id)
            if state:
                unanswered = [
                    q for q in state.get("questions_asked", [])
                    if not any(a.get("question") == q for a in state.get("user_answers", []))
                ]
                if unanswered:
                    state_service.add_answer(ticket_id, unanswered[0], answer)

        return self.start(ticket_id)

    def _build_response(
        self, ticket_id: str, state: dict, actions: list,
        status: str, rag_docs: list, memories: list, next_action: str,
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": status,
            "plan": state.get("current_plan", []),
            "completed_steps": state.get("completed_steps", []),
            "current_step_index": state.get("current_step_index", 0),
            "actions": actions,
            "next_action": next_action,
            "retrieved_knowledge": rag_docs,
            "memories_used": memories,
            "state": state,
        }


troubleshooting_service = TroubleshootingService()
