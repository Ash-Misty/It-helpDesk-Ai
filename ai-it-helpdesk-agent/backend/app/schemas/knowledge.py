from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    document_id: str
    title: str
    category: str
    subcategory: str
    symptoms: list[str]
    possible_causes: list[str]
    troubleshooting_steps: list[str]
    verification_steps: list[str]
    escalation_notes: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "KB-001",
                "title": "VPN Connection Troubleshooting",
                "category": "VPN",
                "subcategory": "VPN Connection",
                "symptoms": ["VPN client fails to connect"],
                "possible_causes": ["Internet unavailable", "Incorrect credentials"],
                "troubleshooting_steps": ["Check internet connection", "Check VPN client status"],
                "verification_steps": ["Confirm VPN connection is established"],
                "escalation_notes": "Escalate if credentials are confirmed correct but connection still fails.",
            }
        }


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    category: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)
