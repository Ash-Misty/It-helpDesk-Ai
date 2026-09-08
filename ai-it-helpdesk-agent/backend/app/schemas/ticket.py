from pydantic import BaseModel, Field, validator
from datetime import datetime


VALID_STATUSES = ["Open", "In Progress", "Resolved", "Escalated", "Closed"]


class TicketCreateRequest(BaseModel):
    user_query: str = Field(..., min_length=1, max_length=2000)
    category: str = Field(..., min_length=1)
    subcategory: str = Field(..., min_length=1)
    priority: str = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., min_length=1)

    @validator("priority")
    def validate_priority(cls, value):
        valid = ["Low", "Medium", "High", "Critical"]
        if value not in valid:
            raise ValueError(f"Priority must be one of {valid}")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "user_query": "My VPN is not connecting.",
                "category": "VPN",
                "subcategory": "VPN Connection",
                "priority": "Medium",
                "confidence": 0.92,
                "reason": "The query indicates a VPN connection problem.",
            }
        }


class TicketUpdateStatusRequest(BaseModel):
    status: str = Field(..., min_length=1)

    @validator("status")
    def validate_status(cls, value):
        if value not in VALID_STATUSES:
            raise ValueError(f"Status must be one of {VALID_STATUSES}")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "status": "In Progress"
            }
        }


class TicketResponse(BaseModel):
    ticket_id: str
    user_query: str
    category: str
    subcategory: str
    priority: str
    confidence: float
    reason: str
    status: str
    created_at: str
    updated_at: str


class TicketListResponse(BaseModel):
    success: bool
    tickets: list[TicketResponse]


class TicketCreateResponse(BaseModel):
    success: bool
    ticket: TicketResponse


class HealthResponse(BaseModel):
    status: str
