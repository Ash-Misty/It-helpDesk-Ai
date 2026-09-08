from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from app.schemas.state import AgentState, WorkflowStage
from app.services.state_service import state_service
from app.services.ticket_service import ticket_service

router = APIRouter()


@router.post("/state/{ticket_id}/initialize")
def initialize_state(ticket_id: str):
    try:
        result = state_service.initialize_state(ticket_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    if result.get("already_exists"):
        return {
            "success": True,
            "already_exists": True,
            "message": "State already initialized for this ticket.",
            "state": result["state"],
        }
    return {
        "success": True,
        "already_exists": False,
        "message": "State initialized successfully.",
        "state": result["state"],
    }


@router.get("/state/{ticket_id}")
def get_state(ticket_id: str):
    state = state_service.get_state(ticket_id)
    if state is None:
        raise HTTPException(status_code=404, detail="State not found.")
    return {"success": True, "state": state}


@router.patch("/state/{ticket_id}/stage")
def update_stage(
    ticket_id: str,
    current_stage: str = Body(..., embed=True),
):
    try:
        state = state_service.update_stage(ticket_id, current_stage)
        return {"success": True, "state": state}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/state/{ticket_id}/answer")
def add_answer(
    ticket_id: str,
    question: str = Body(..., embed=True),
    answer: str = Body(..., embed=True),
):
    try:
        state = state_service.add_answer(ticket_id, question, answer)
        return {"success": True, "state": state}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while adding the answer.",
        ) from exc


@router.post("/state/{ticket_id}/complete-step")
def complete_step(ticket_id: str):
    try:
        state = state_service.complete_step(ticket_id)
        return {"success": True, "state": state}
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while completing the step.",
        ) from exc


@router.post("/state/{ticket_id}/update-decision")
def update_agent_decision(
    ticket_id: str,
    decision: Dict[str, Any] = Body(...),
):
    try:
        state = state_service.update_agent_decision(ticket_id, decision)
        return {"success": True, "state": state}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while updating the decision.",
        ) from exc
