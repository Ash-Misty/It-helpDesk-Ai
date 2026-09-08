from typing import Optional
from pydantic import BaseModel, Field


VALID_TROUBLESHOOT_ACTIONS = [
    "retrieve_knowledge",
    "call_tool",
    "ask_information",
    "recommend_solution",
    "verify",
    "resolve",
    "escalate",
    "no_action",
]


class TroubleshootingStartRequest(BaseModel):
    ticket_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)


class TroubleshootingContinueRequest(BaseModel):
    ticket_id: str = Field(..., min_length=1)
    answer: Optional[str] = None


class TroubleshootingAction(BaseModel):
    type: str
    detail: str = ""
    data: Optional[dict] = None


class TroubleshootingResponse(BaseModel):
    success: bool
    ticket_id: str
    status: str
    plan: list[str]
    completed_steps: list[str]
    current_step_index: int
    actions: list[dict]
    next_action: str
    retrieved_knowledge: list[dict]
    memories_used: list[dict]
    state: Optional[dict] = None
