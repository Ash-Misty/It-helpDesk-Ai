from typing import Optional
from pydantic import BaseModel, Field


class MemoryEntryCreate(BaseModel):
    ticket_id: str = Field(..., min_length=1)
    issue_summary: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    solution: str = Field(..., min_length=1)
    outcome: str = Field(..., min_length=1)


class MemoryEntryResponse(BaseModel):
    memory_id: str
    ticket_id: str
    issue_summary: str
    category: str
    solution: str
    outcome: str


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    category: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)


class MemorySearchResponse(BaseModel):
    success: bool
    query: str
    count: int
    memories: list[dict]
