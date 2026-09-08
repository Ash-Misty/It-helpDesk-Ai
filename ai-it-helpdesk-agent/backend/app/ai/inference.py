import re
import json
from typing import Dict, Any, Optional, List
from app.ai.model import model_loader
from app.schemas.agent import VALID_NEXT_ACTIONS, VALID_TOOL_ACTIONS


SECURITY_KEYWORDS = [
    "hacked", "unauthorized", "breach", "compromised", "security", "someone accessed",
    "strange activity", "suspicious", "stolen", "phishing", "malware", "virus"
]

CRITICAL_KEYWORDS = [
    "server down", "production", "entire company", "everyone", "all users",
    "data loss", "critical", "emergency", "urgent", "outage"
]

COMMON_QUESTIONS = {
    "VPN": [
        "Are you connected to the internet?",
        "Are you receiving an error message?",
        "Have you tried restarting the VPN client?"
    ],
    "Password": [
        "Are you trying to reset your password?",
        "Do you have access to your registered email?"
    ],
    "Printer": [
        "Is the printer powered on?",
        "Is the printer connected to the network?",
        "Is there a paper jam?"
    ],
    "Network": [
        "Can you access other websites?",
        "Are other devices on the same network affected?",
        "Have you tried restarting your router?"
    ],
    "Hardware": [
        "What device are you using?",
        "When did the issue start?",
        "Have you made any recent changes?"
    ],
    "Software": [
        "What application is affected?",
        "When did the issue start?",
        "Have you tried restarting the application?"
    ],
    "Email": [
        "What email client are you using?",
        "Are you receiving an error message?",
        "Can you access other websites?"
    ],
    "Security": [
        "Have you noticed any unauthorized activity?",
        "Can you describe what happened?",
        "When did you first notice this issue?"
    ],
    "default": [
        "Can you describe the issue in more detail?",
        "When did the issue start?",
        "Have you tried any troubleshooting steps already?"
    ]
}

INITIAL_PLANS = {
    "VPN": [
        "Verify internet connectivity",
        "Check VPN client configuration",
        "Verify VPN credentials",
        "Try reconnecting to VPN"
    ],
    "Password": [
        "Verify user identity",
        "Guide password reset process",
        "Send password reset email"
    ],
    "Printer": [
        "Check printer power and status",
        "Verify network connection",
        "Check print queue",
        "Verify printer drivers"
    ],
    "Network": [
        "Check physical connections",
        "Test network connectivity",
        "Check DNS settings",
        "Verify router/modem status"
    ],
    "Hardware": [
        "Identify affected device",
        "Check device status",
        "Verify connections",
        "Test with basic diagnostics"
    ],
    "Software": [
        "Check error logs",
        "Verify application status",
        "Test basic functionality",
        "Check for updates"
    ],
    "Email": [
        "Verify email credentials",
        "Check email server status",
        "Test email sync",
        "Check spam folder"
    ],
    "Security": [
        "Verify user identity",
        "Check account activity",
        "Escalate to security team immediately",
        "Preserve audit logs"
    ],
    "default": [
        "Gather additional information",
        "Check recent changes",
        "Verify basic connectivity",
        "Consult documentation"
    ]
}


class InferenceEngine:
    def __init__(self):
        self._max_new_tokens = 512
        self._temperature = 0.2
        self._top_p = 0.9

    def _build_prompt(
        self, ticket: dict, state_context: Optional[dict] = None
    ) -> str:
        prompt = (
            "You are an IT Helpdesk Agent.\n"
            "Your job is to analyze an IT support ticket, understand the user's problem, "
            "determine the appropriate next action, and create an initial troubleshooting plan.\n"
            "Use the ticket information and current workflow state provided to make your decision.\n"
            "You must return structured output in valid JSON format.\n"
            "Do not invent technical facts.\n"
            "If important information is missing, request it.\n"
            "If the issue appears dangerous, security-related, business-critical, or requires privileged access, recommend escalation.\n"
            "Do not claim that a problem has been fixed unless there is evidence that it has been resolved.\n"
            "Do not execute tools.\n"
            "Do not access systems.\n"
            "Do not expose private reasoning.\n"
            "Return a concise explanation and a structured decision.\n\n"
            "Ticket Information:\n"
            f"- Ticket ID: {ticket.get('ticket_id', '')}\n"
            f"- User Query: {ticket.get('user_query', '')}\n"
            f"- Category: {ticket.get('category', '')}\n"
            f"- Subcategory: {ticket.get('subcategory', '')}\n"
            f"- Priority: {ticket.get('priority', '')}\n"
            f"- Confidence: {ticket.get('confidence', '')}\n"
            f"- Reason: {ticket.get('reason', '')}\n"
            f"- Status: {ticket.get('status', '')}\n"
        )

        if state_context:
            prompt += (
                "\nCurrent Workflow State:\n"
                f"- Current Stage: {state_context.get('current_stage', '')}\n"
                f"- Current Plan: {state_context.get('current_plan', [])}\n"
                f"- Completed Steps: {state_context.get('completed_steps', [])}\n"
                f"- Current Step Index: {state_context.get('current_step_index', 0)}\n"
                f"- Questions Asked: {state_context.get('questions_asked', [])}\n"
                f"- Previous Answers: {state_context.get('user_answers', [])}\n"
                f"- Last Action: {state_context.get('last_action', '')}\n"
                f"- Status: {state_context.get('status', '')}\n"
                f"- Tool Results: {state_context.get('tool_results', [])}\n"
            )

        prompt += (
            "\nReturn ONLY valid JSON in this exact format:\n"
            '{"understanding": "...", "problem_type": "...", "next_action": "ask_information|troubleshoot|recommend_solution|escalate|resolve", '
            '"requires_more_information": true/false, "questions": ["...", "..."], "initial_plan": ["...", "..."], '
            '"can_auto_resolve": true/false, "should_escalate": true/false, "reason": "..."}\n'
        )

        return prompt

    def _extract_json(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in model output.")
        return json.loads(match.group(0))

    def _validate_and_fix(self, raw: dict, ticket: dict) -> dict:
        if "next_action" not in raw or raw["next_action"] not in VALID_NEXT_ACTIONS:
            raw["next_action"] = "troubleshoot"

        if "understanding" not in raw or not raw["understanding"]:
            raw["understanding"] = (
                f"IT issue regarding {ticket.get('subcategory', 'unknown issue').lower()} "
                f"in the {ticket.get('category', 'general')} category."
            )

        if "problem_type" not in raw or not raw["problem_type"]:
            raw["problem_type"] = ticket.get("subcategory", "General IT Issue")

        if "requires_more_information" not in raw:
            raw["requires_more_information"] = False

        if "questions" not in raw or not isinstance(raw["questions"], list):
            raw["questions"] = []

        if "initial_plan" not in raw or not isinstance(raw["initial_plan"], list):
            raw["initial_plan"] = ["Gather additional information about the issue."]

        if "can_auto_resolve" not in raw:
            raw["can_auto_resolve"] = False

        if "should_escalate" not in raw:
            raw["should_escalate"] = False

        if "reason" not in raw or not raw["reason"]:
            raw["reason"] = "Initial analysis completed."

        return raw

    def _analyze_ticket_fast(
        self, ticket: dict, state_context: Optional[dict] = None
    ) -> dict:
        user_query = ticket.get("user_query", "").lower()
        category = ticket.get("category", "")
        subcategory = ticket.get("subcategory", "")
        priority = ticket.get("priority", "Medium")

        is_security = any(kw in user_query for kw in SECURITY_KEYWORDS)
        is_critical = any(kw in user_query for kw in CRITICAL_KEYWORDS) or priority in ["Critical", "High"]

        if is_security:
            next_action = "escalate"
            should_escalate = True
            can_auto_resolve = False
            questions = COMMON_QUESTIONS.get("Security", COMMON_QUESTIONS["default"])
            plan = INITIAL_PLANS.get("Security", INITIAL_PLANS["default"])
            understanding = "The user reports a potential security issue with their account or system."
        elif is_critical:
            next_action = "escalate"
            should_escalate = True
            can_auto_resolve = False
            questions = COMMON_QUESTIONS.get(category, COMMON_QUESTIONS["default"])
            plan = INITIAL_PLANS.get(category, INITIAL_PLANS["default"])
            understanding = "The user reports a critical issue requiring immediate escalation."
        else:
            next_action = "troubleshoot"
            should_escalate = False
            can_auto_resolve = True
            questions = COMMON_QUESTIONS.get(category, COMMON_QUESTIONS["default"])
            plan = INITIAL_PLANS.get(category, INITIAL_PLANS["default"])
            understanding = f"The user reports: {ticket.get('user_query', 'Unknown issue')}"

        already_answered_questions = set()
        if state_context:
            for a in state_context.get("user_answers", []):
                already_answered_questions.add(a.get("question", "").lower().strip())

        unanswered_questions = [
            q for q in questions
            if q.lower().strip() not in already_answered_questions
        ]

        requires_info = len(unanswered_questions) > 0

        return {
            "understanding": understanding,
            "problem_type": f"{category} - {subcategory}" if subcategory else category,
            "next_action": next_action,
            "requires_more_information": requires_info,
            "questions": unanswered_questions if requires_info else [],
            "initial_plan": plan,
            "can_auto_resolve": can_auto_resolve,
            "should_escalate": should_escalate,
            "reason": f"Issue classified as {category}/{subcategory}. Recommended action: {next_action}."
        }

    def decide_next_action(
        self,
        ticket: dict,
        state_context: Optional[dict] = None,
        available_tools: Optional[List[str]] = None,
        previous_tool_results: Optional[List[dict]] = None,
    ) -> dict:
        model, tokenizer = model_loader.load()
        if model is not None and tokenizer is not None:
            try:
                return self._decide_via_model(
                    ticket, state_context, available_tools, previous_tool_results
                )
            except Exception:
                pass

        return self._decide_via_rules(
            ticket, state_context, available_tools, previous_tool_results
        )

    def _decide_via_model(
        self,
        ticket: dict,
        state_context: Optional[dict] = None,
        available_tools: Optional[List[str]] = None,
        previous_tool_results: Optional[List[dict]] = None,
    ) -> dict:
        from app.schemas.agent import ToolDecision

        user_query = ticket.get("user_query", "")
        category = ticket.get("category", "")
        subcategory = ticket.get("subcategory", "")
        priority = ticket.get("priority", "Medium")

        is_security = any(kw in user_query.lower() for kw in SECURITY_KEYWORDS)
        is_critical = (
            any(kw in user_query.lower() for kw in CRITICAL_KEYWORDS)
            or priority in ["Critical", "High"]
        )

        if is_security:
            decision = ToolDecision(
                action="escalate",
                tool_name=None,
                arguments={},
                reason=(
                    "Security-related issue detected. Escalation recommended "
                    "rather than running diagnostic tools."
                ),
            )
            return decision.model_dump()

        if is_critical:
            decision = ToolDecision(
                action="escalate",
                tool_name=None,
                arguments={},
                reason=(
                    "Critical/high-priority issue. Escalation recommended "
                    "rather than running diagnostic tools."
                ),
            )
            return decision.model_dump()

        tools = available_tools or []
        tool_context = self._build_tool_context(
            tools, state_context, previous_tool_results
        )

        prompt = self._build_tool_decision_prompt(ticket, tool_context)
        _ = (model, tokenizer, prompt)

        return self._decide_via_rules(
            ticket, state_context, available_tools, previous_tool_results
        )

    def _build_tool_decision_prompt(
        self, ticket: dict, tool_context: dict
    ) -> str:
        return json.dumps({
            "ticket": ticket,
            "available_tools": tool_context.get("available_tools", []),
            "tool_results": tool_context.get("tool_results", []),
            "questions_asked": tool_context.get("questions_asked", []),
            "unanswered_questions": tool_context.get("unanswered_questions", []),
        })

    def _build_tool_context(
        self,
        available_tools: List[str],
        state_context: Optional[dict],
        previous_tool_results: Optional[List[dict]],
    ) -> dict:
        state_tool_results = []
        if state_context:
            state_tool_results = state_context.get("tool_results", [])

        merged_results = list(state_tool_results)
        if previous_tool_results:
            for r in previous_tool_results:
                if r not in merged_results:
                    merged_results.append(r)

        already_answered = set()
        questions_asked = []
        if state_context:
            questions_asked = state_context.get("questions_asked", [])
            for a in state_context.get("user_answers", []):
                already_answered.add(a.get("question", "").lower().strip())

        unanswered = [
            q for q in questions_asked if q.lower().strip() not in already_answered
        ]

        return {
            "available_tools": available_tools,
            "tool_results": merged_results,
            "questions_asked": questions_asked,
            "unanswered_questions": unanswered,
        }

    def _decide_via_rules(
        self,
        ticket: dict,
        state_context: Optional[dict] = None,
        available_tools: Optional[List[str]] = None,
        previous_tool_results: Optional[List[dict]] = None,
    ) -> dict:
        from app.schemas.agent import ToolDecision

        user_query = ticket.get("user_query", "").lower()
        category = ticket.get("category", "")
        subcategory = ticket.get("subcategory", "")
        priority = ticket.get("priority", "Medium")

        is_security = any(kw in user_query for kw in SECURITY_KEYWORDS)
        is_critical = any(kw in user_query for kw in CRITICAL_KEYWORDS) or priority in ["Critical", "High"]

        if is_security:
            decision = ToolDecision(
                action="escalate",
                tool_name=None,
                arguments={},
                reason="Security-related issue detected. Escalation recommended rather than running diagnostic tools.",
            )
            return decision.model_dump()

        if is_critical:
            decision = ToolDecision(
                action="escalate",
                tool_name=None,
                arguments={},
                reason="Critical/high-priority issue. Escalation recommended rather than running diagnostic tools.",
            )
            return decision.model_dump()

        tools = available_tools or []
        tool_context = self._build_tool_context(
            tools, state_context, previous_tool_results
        )

        ran_tools = [
            r.get("tool_name")
            for r in tool_context["tool_results"]
            if r.get("success")
        ]

        # Context-aware tool selection: try specific tools first,
        # even if there are pending questions (diagnostic tools don't need user input).
        if self._should_check_internet(user_query, category, subcategory, tools, ran_tools):
            internet_decision = self._decide_for_tool(
                "check_internet_connection",
                "The issue concerns network/VPN connectivity. Checking internet connection first.",
                tools,
                ran_tools,
            )
            if internet_decision:
                decision = ToolDecision(**internet_decision)
                return decision.model_dump()

        if self._should_check_vpn(user_query, category, tools, ran_tools):
            vpn_decision = self._decide_for_tool(
                "check_vpn_status",
                "The ticket involves a VPN connection issue. Checking VPN status.",
                tools,
                ran_tools,
            )
            if vpn_decision:
                decision = ToolDecision(**vpn_decision)
                return decision.model_dump()

        if self._should_check_dns(user_query, tools, ran_tools):
            dns_decision = {
                "action": "call_tool",
                "tool_name": "check_dns_status",
                "arguments": {"domain": "corporate.example.com"},
                "reason": "The issue may be DNS-related. Checking DNS resolution.",
            }
            if "check_dns_status" in tools and "check_dns_status" not in ran_tools:
                decision = ToolDecision(**dns_decision)
                return decision.model_dump()

        if "printer" in user_query:
            app_decision = self._decide_for_tool(
                "check_application_status",
                "Checking printer-related application status.",
                tools,
                ran_tools,
                arguments={"application": "Print Spooler"},
            )
            if app_decision:
                decision = ToolDecision(**app_decision)
                return decision.model_dump()

        if "disk" in user_query or "storage" in user_query or "space" in user_query:
            disk_decision = self._decide_for_tool(
                "check_disk_space",
                "The issue may relate to low disk space. Checking disk space.",
                tools,
                ran_tools,
            )
            if disk_decision:
                decision = ToolDecision(**disk_decision)
                return decision.model_dump()

        # After specific tools, check if we need user input before fallback tools.
        if tool_context["unanswered_questions"]:
            decision = ToolDecision(
                action="ask_information",
                tool_name=None,
                arguments={},
                reason="The agent has pending questions that need user answers before proceeding.",
            )
            return decision.model_dump()

        # Fallback diagnostic tools (system status, diagnostic report).
        if self._should_check_system_status(user_query, category, subcategory, tools, ran_tools):
            sys_decision = self._decide_for_tool(
                "check_system_status",
                "Starting with a general system status check to gather diagnostic information.",
                tools,
                ran_tools,
            )
            if sys_decision:
                decision = ToolDecision(**sys_decision)
                return decision.model_dump()

        if self._should_create_diagnostic_report(tools, ran_tools):
            report_decision = self._decide_for_tool(
                "create_diagnostic_report",
                "Sufficient diagnostic data collected. Creating a report.",
                tools,
                ran_tools,
            )
            if report_decision:
                decision = ToolDecision(**report_decision)
                return decision.model_dump()

        stage = state_context.get("current_stage", "planning") if state_context else "planning"
        completed_steps = state_context.get("completed_steps", []) if state_context else []

        if stage == "troubleshooting" and len(completed_steps) >= 1:
            decision = ToolDecision(
                action="recommend_solution",
                tool_name=None,
                arguments={},
                reason="Diagnostic tools have been run. Recommending based on collected results.",
            )
            return decision.model_dump()

        decision = ToolDecision(
            action="no_action",
            tool_name=None,
            arguments={},
            reason="No further immediate action needed. Awaiting user response.",
        )
        return decision.model_dump()

    def _should_check_internet(
        self, user_query: str, category: str, subcategory: str,
        tools: List[str], ran_tools: List[str],
    ) -> bool:
        if "check_internet_connection" not in tools or "check_internet_connection" in ran_tools:
            return False
        indicators = ["internet", "vpn", "wifi", "wireless", "network", "web"]
        return (
            any(ind in user_query for ind in indicators)
            or category in ("VPN", "Network")
        )

    def _should_check_vpn(
        self, user_query: str, category: str,
        tools: List[str], ran_tools: List[str],
    ) -> bool:
        if "check_vpn_status" not in tools or "check_vpn_status" in ran_tools:
            return False
        if "check_internet_connection" not in ran_tools:
            return False
        return "vpn" in user_query or "VPN" in category

    def _should_check_dns(
        self, user_query: str, tools: List[str], ran_tools: List[str],
    ) -> bool:
        if "check_dns_status" not in tools or "check_dns_status" in ran_tools:
            return False
        indicators = ["dns", "cannot resolve", "can't access", "not resolving"]
        return any(ind in user_query for ind in indicators)

    def _should_check_system_status(
        self, user_query: str, category: str, subcategory: str,
        tools: List[str], ran_tools: List[str],
    ) -> bool:
        if "check_system_status" not in tools or "check_system_status" in ran_tools:
            return False
        if ran_tools:
            return False
        if any(ind in user_query for ind in ["vpn", "internet", "wifi", "wireless", "dns", "network", "printer", "disk", "storage"]):
            return False
        if category in ("VPN", "Network", "Printer", "Security"):
            return False
        return True

    def _should_create_diagnostic_report(
        self, tools: List[str], ran_tools: List[str],
    ) -> bool:
        if "create_diagnostic_report" not in tools or "create_diagnostic_report" in ran_tools:
            return False
        tool_results = [r for r in ran_tools if r != "create_diagnostic_report"]
        return len(tool_results) >= 1

    def _decide_for_tool(
        self, tool_name: str, reason: str,
        tools: List[str], ran_tools: List[str],
        arguments: dict = None,
    ) -> Optional[dict]:
        if tool_name in tools and tool_name not in ran_tools:
            return {
                "action": "call_tool",
                "tool_name": tool_name,
                "arguments": arguments or {},
                "reason": reason,
            }
        return None

    def analyze(
        self, ticket: dict, state_context: Optional[dict] = None
    ) -> dict:
        return self._analyze_ticket_fast(ticket, state_context)


inference_engine = InferenceEngine()
