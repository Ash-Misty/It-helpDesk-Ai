from typing import Dict, Any, List, Optional
from app.agents.helpdesk_agent import helpdesk_agent
from app.tools.executor import tool_executor
from app.tools.registry import tool_registry
from app.services.state_service import state_service
from app.services.ticket_service import ticket_service
from app.tools.base import ToolResult


MAX_TOOL_CALLS = 5


class AgentExecutionService:
    def __init__(self, max_tool_calls: int = MAX_TOOL_CALLS):
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

    def execute(self, ticket_id: str) -> Dict[str, Any]:
        ticket = ticket_service.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError("Ticket not found")

        state = state_service.get_state(ticket_id)
        if state is None:
            init_result = state_service.initialize_state(ticket_id)
            state = init_result["state"]

        actions: List[Dict[str, Any]] = []
        tool_calls_count = len(state.get("tool_results", []))
        available_tools = tool_registry.list_tool_names()
        ticket_dict = self._get_ticket_dict(ticket)

        final_status = "in_progress"
        final_next_action = "troubleshoot"

        while tool_calls_count < self._max_tool_calls:
            state_context = state_service.get_agent_context(ticket_id)

            decision = helpdesk_agent.decide_tool_use(
                ticket_dict,
                state_context=state_context,
                available_tools=available_tools,
                previous_tool_results=None,
            )

            if not decision.get("success"):
                actions.append({
                    "type": "error",
                    "error": "Agent decision failed. Awaiting user input.",
                })
                final_status = "error"
                break

            tool_decision = decision.get("tool_decision", {})
            action = tool_decision.get("action", "no_action")
            tool_name = tool_decision.get("tool_name")
            arguments = tool_decision.get("arguments", {})

            if action == "call_tool" and tool_name:
                actions.append({
                    "type": "tool_call",
                    "tool": tool_name,
                    "arguments": arguments,
                    "reason": tool_decision.get("reason", ""),
                    "timestamp": tool_decision.get("timestamp", None),
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
                    "simulated": tool_result.simulated,
                })

                if not tool_result.success:
                    final_status = "tool_error"
                    final_next_action = "no_action"
                    actions.append({
                        "type": "tool_error",
                        "tool": tool_name,
                        "error": tool_result.error,
                    })
                    break

            elif action == "ask_information":
                actions.append({
                    "type": "ask_information",
                    "reason": tool_decision.get("reason", ""),
                })
                final_next_action = "ask_information"
                final_status = "requires_user_input"

                try:
                    state_service.update_stage(ticket_id, "awaiting_information")
                except ValueError:
                    pass

                state = state_service.get_state(ticket_id)
                break

            elif action == "escalate":
                actions.append({
                    "type": "escalate",
                    "reason": tool_decision.get("reason", ""),
                })
                final_next_action = "escalate"
                final_status = "escalated"

                try:
                    state_service.update_stage(ticket_id, "escalation_required")
                except ValueError:
                    pass

                state = state_service.get_state(ticket_id)
                break

            elif action == "recommend_solution":
                actions.append({
                    "type": "recommend_solution",
                    "reason": tool_decision.get("reason", ""),
                })
                final_next_action = "recommend_solution"
                final_status = "solution_recommended"

                try:
                    state_service.update_stage(ticket_id, "verifying")
                except ValueError:
                    pass

                state = state_service.get_state(ticket_id)
                break

            elif action == "resolve":
                actions.append({
                    "type": "resolve",
                    "reason": tool_decision.get("reason", ""),
                })
                final_next_action = "resolve"
                final_status = "completed"

                try:
                    state_service.update_stage(ticket_id, "resolved")
                except ValueError:
                    pass

                state = state_service.get_state(ticket_id)
                break

            else:
                actions.append({
                    "type": "no_action",
                    "reason": tool_decision.get("reason", "No action determined."),
                })
                final_next_action = "no_action"
                final_status = "awaiting_user"
                break

        if tool_calls_count >= self._max_tool_calls and final_status == "in_progress":
            final_status = "max_tool_calls_reached"
            actions.append({
                "type": "max_calls_reached",
                "reason": f"Maximum tool calls ({self._max_tool_calls}) reached.",
            })

        final_state = state_service.get_state(ticket_id)

        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": final_status,
            "actions": actions,
            "next_action": final_next_action,
            "state": final_state,
        }


agent_execution_service = AgentExecutionService()
