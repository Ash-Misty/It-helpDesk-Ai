from fastapi import APIRouter, HTTPException
from app.schemas.memory import (
    MemoryEntryCreate,
    MemoryEntryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
)
from app.memory.memory_manager import memory_manager

router = APIRouter()


@router.post("/memory", response_model=dict)
def create_memory(entry: MemoryEntryCreate):
    result = memory_manager.store_memory(
        ticket_id=entry.ticket_id,
        issue_summary=entry.issue_summary,
        category=entry.category,
        solution=entry.solution,
        outcome=entry.outcome,
    )
    return result


@router.get("/memory", response_model=dict)
def list_memories():
    return memory_manager.get_all_memories()


@router.get("/memory/{ticket_id}", response_model=dict)
def get_ticket_memories(ticket_id: str):
    return memory_manager.get_ticket_memories(ticket_id)


@router.post("/memory/search", response_model=MemorySearchResponse)
def search_memories(request: MemorySearchRequest):
    result = memory_manager.retrieve_relevant_memories(
        query=request.query,
        category=request.category,
        top_k=request.top_k,
    )
    return MemorySearchResponse(**result)
