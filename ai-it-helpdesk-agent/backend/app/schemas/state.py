from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.schemas.agent import AgentDecision


class WorkflowStage(str, Enum):
    CREATED = "created"
    ANALYZING = "analyzing"
    AWAITING_INFORMATION = "awaiting_information"
    PLANNING = "planning"
    TROUBLESHOOTING = "troubleshooting"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    ESCALATION_REQUIRED = "escalation_required"


class StateStatus(str, Enum):
    ACTIVE = "active"
    WAITING_FOR_USER = "waiting_for_user"
    COMPLETED = "completed"
    ESCALATED = "escalated"


STAGE_TO_STATUS = {
    WorkflowStage.CREATED: StateStatus.ACTIVE,
    WorkflowStage.ANALYZING: StateStatus.ACTIVE,
    WorkflowStage.AWAITING_INFORMATION: StateStatus.WAITING_FOR_USER,
    WorkflowStage.PLANNING: StateStatus.ACTIVE,
    WorkflowStage.TROUBLESHOOTING: StateStatus.ACTIVE,
    WorkflowStage.VERIFYING: StateStatus.ACTIVE,
    WorkflowStage.RESOLVED: StateStatus.COMPLETED,
    WorkflowStage.ESCALATION_REQUIRED: StateStatus.ESCALATED,
}


VALID_TRANSITIONS = {
    WorkflowStage.CREATED: {
        WorkflowStage.ANALYZING,
        WorkflowStage.ESCALATION_REQUIRED,
    },
    WorkflowStage.ANALYZING: {
        WorkflowStage.AWAITING_INFORMATION,
        WorkflowStage.PLANNING,
        WorkflowStage.ESCALATION_REQUIRED,
    },
    WorkflowStage.AWAITING_INFORMATION: {
        WorkflowStage.PLANNING,
        WorkflowStage.TROUBLESHOOTING,
        WorkflowStage.ESCALATION_REQUIRED,
    },
    WorkflowStage.PLANNING: {
        WorkflowStage.TROUBLESHOOTING,
        WorkflowStage.AWAITING_INFORMATION,
        WorkflowStage.ESCALATION_REQUIRED,
    },
    WorkflowStage.TROUBLESHOOTING: {
        WorkflowStage.VERIFYING,
        WorkflowStage.AWAITING_INFORMATION,
        WorkflowStage.ESCALATION_REQUIRED,
    },
    WorkflowStage.VERIFYING: {
        WorkflowStage.RESOLVED,
        WorkflowStage.TROUBLESHOOTING,
        WorkflowStage.ESCALATION_REQUIRED,
    },
    WorkflowStage.RESOLVED: set(),
    WorkflowStage.ESCALATION_REQUIRED: set(),
}


class UserAnswer(BaseModel):
    question: str
    answer: str
    answered_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ToolResultRecord(BaseModel):
    tool_name: str
    success: bool
    result: dict = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: float = 0
    simulated: bool = True
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentState(BaseModel):
    ticket_id: str
    user_query: str
    category: str
    subcategory: str
    priority: str
    current_stage: WorkflowStage = WorkflowStage.CREATED
    agent_decision: Optional[AgentDecision] = None
    questions_asked: List[str] = Field(default_factory=list)
    user_answers: List[UserAnswer] = Field(default_factory=list)
    current_plan: List[str] = Field(default_factory=list)
    completed_steps: List[str] = Field(default_factory=list)
    current_step_index: int = 0
    last_action: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    tool_results: List[ToolResultRecord] = Field(default_factory=list)
    status: StateStatus = StateStatus.ACTIVE
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @validator("current_stage", pre=True)
    def validate_stage(cls, v):
        if isinstance(v, WorkflowStage):
            return v
        if isinstance(v, str):
            return WorkflowStage(v)
        raise ValueError(f"Invalid stage: {v}")

    @validator("status", pre=True)
    def validate_status(cls, v):
        if isinstance(v, StateStatus):
            return v
        if isinstance(v, str):
            return StateStatus(v)
        raise ValueError(f"Invalid status: {v}")

    def is_valid_transition(self, new_stage: WorkflowStage) -> bool:
        if new_stage == self.current_stage:
            return True
        allowed = VALID_TRANSITIONS.get(self.current_stage, set())
        return new_stage in allowed

    class Config:
        use_enum_values = True
        json_encoders = {
            WorkflowStage: lambda v: v.value,
            StateStatus: lambda v: v.value,
        }
