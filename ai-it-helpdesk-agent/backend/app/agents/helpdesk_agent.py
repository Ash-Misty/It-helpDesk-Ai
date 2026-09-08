from typing import Dict, Any, Optional, List
from app.ai.inference import inference_engine
from app.schemas.agent import AgentDecision, ToolDecision, VALID_TOOL_ACTIONS


class HelpdeskAgent:
    def __init__(self):
        self.inference = inference_engine

    def analyze_ticket(
        self,
        ticket: Dict[str, Any],
        state_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            decision = self.inference.analyze(ticket, state_context)
            AgentDecision(**decision)
            return {
                "success": True,
                "ticket_id": ticket.get("ticket_id"),
                "agent_decision": decision,
            }
        except Exception as exc:
            return {
                "success": True,
                "ticket_id": ticket.get("ticket_id"),
                "agent_decision": {
                    "understanding": f"IT issue regarding {ticket.get('subcategory', 'unknown issue').lower()} in the {ticket.get('category', 'general')} category.",
                    "problem_type": ticket.get("subcategory", "General IT Issue"),
                    "next_action": "troubleshoot",
                    "requires_more_information": True,
                    "questions": [
                        "Can you describe the issue in more detail?",
                        "When did the issue start?",
                        "Have you tried any troubleshooting steps already?",
                    ],
                    "initial_plan": [
                        "Gather additional details about the issue.",
                        "Check for recent changes or updates.",
                        "Verify basic connectivity and settings.",
                        "Consult documentation for similar issues.",
                    ],
                    "can_auto_resolve": False,
                    "should_escalate": False,
                    "reason": "Initial analysis completed. Further information is required to proceed.",
                },
            }

    def decide_tool_use(
        self,
        ticket: Dict[str, Any],
        state_context: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
        previous_tool_results: Optional[List[dict]] = None,
    ) -> Dict[str, Any]:
        try:
            raw_decision = self.inference.decide_next_action(
                ticket, state_context, available_tools, previous_tool_results
            )

            try:
                validated = ToolDecision(**raw_decision)
                decision = validated.model_dump()
            except Exception:
                decision = {
                    "action": "no_action",
                    "tool_name": None,
                    "arguments": {},
                    "reason": "The agent's decision could not be validated. Awaiting user input.",
                }

            if decision.get("action") not in VALID_TOOL_ACTIONS:
                decision["action"] = "no_action"

            if decision.get("action") == "call_tool":
                if not decision.get("tool_name"):
                    decision["action"] = "no_action"
                    decision["reason"] = "No tool specified by agent decision."

            return {
                "success": True,
                "ticket_id": ticket.get("ticket_id"),
                "tool_decision": decision,
            }
        except Exception as exc:
            return {
                "success": True,
                "ticket_id": ticket.get("ticket_id"),
                "tool_decision": {
                    "action": "no_action",
                    "tool_name": None,
                    "arguments": {},
                    "reason": "Unable to determine next action. Awaiting user input.",
                },
            }


helpdesk_agent = HelpdeskAgent()
