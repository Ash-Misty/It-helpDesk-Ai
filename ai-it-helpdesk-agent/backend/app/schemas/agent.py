from typing import Optional
from pydantic import BaseModel, Field, field_validator


VALID_NEXT_ACTIONS = [
    "ask_information",
    "troubleshoot",
    "recommend_solution",
    "escalate",
    "resolve",
]

VALID_TOOL_ACTIONS = [
    "call_tool",
    "ask_information",
    "recommend_solution",
    "escalate",
    "resolve",
    "no_action",
]


class AgentDecision(BaseModel):
    understanding: str
    problem_type: str
    next_action: str
    requires_more_information: bool
    questions: list[str]
    initial_plan: list[str]
    can_auto_resolve: bool
    should_escalate: bool
    reason: str

    @field_validator("next_action")
    @classmethod
    def validate_next_action(cls, value):
        if value not in VALID_NEXT_ACTIONS:
            raise ValueError(f"next_action must be one of {VALID_NEXT_ACTIONS}")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "understanding": "The user is unable to establish a VPN connection.",
                "problem_type": "VPN connectivity",
                "next_action": "troubleshoot",
                "requires_more_information": True,
                "questions": [
                    "Are you connected to the internet?",
                    "Are you receiving an error message when connecting to the VPN?",
                ],
                "initial_plan": [
                    "Verify internet connectivity",
                    "Check VPN client status",
                    "Check VPN authentication",
                    "Retry VPN connection",
                ],
                "can_auto_resolve": True,
                "should_escalate": False,
                "reason": "The issue appears to be a common VPN connectivity problem that can initially be investigated through standard troubleshooting.",
            }
        }


class AgentAnalyzeRequest(BaseModel):
    ticket_id: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "IT-000001"
            }
        }


class AgentAnalyzeResponse(BaseModel):
    success: bool
    ticket_id: str
    agent_decision: AgentDecision


class ToolDecision(BaseModel):
    action: str = Field(..., description="The action the agent has decided to take.")
    tool_name: Optional[str] = Field(
        default=None,
        description="The name of the tool to call, if action is 'call_tool'.",
    )
    arguments: dict = Field(
        default_factory=dict,
        description="Arguments to pass to the selected tool.",
    )
    reason: str = Field(..., description="Concise reason for the decision.")

    @field_validator("action")
    @classmethod
    def validate_action(cls, value):
        if value not in VALID_TOOL_ACTIONS:
            raise ValueError(
                f"action must be one of {VALID_TOOL_ACTIONS}, got '{value}'"
            )
        return value

    model_config = {"extra": "forbid", "json_schema_extra": {
        "example": {
            "action": "call_tool",
            "tool_name": "check_vpn_status",
            "arguments": {},
            "reason": "The ticket concerns a VPN connection failure and the VPN status should be checked first.",
        }
    }}


class AgentExecuteResponse(BaseModel):
    success: bool
    ticket_id: str
    status: str
    actions: list
    next_action: str
    state: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "ticket_id": "IT-000001",
                "status": "in_progress",
                "actions": [
                    {"type": "tool_call", "tool": "check_internet_connection"},
                    {"type": "tool_result", "result": {"connected": True, "latency_ms": 42}},
                    {"type": "tool_call", "tool": "check_vpn_status"},
                ],
                "next_action": "ask_information",
                "state": None,
            }
        }
