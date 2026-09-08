from fastapi import APIRouter, HTTPException
from app.schemas.agent import (
    AgentAnalyzeRequest,
    AgentAnalyzeResponse,
    AgentExecuteResponse,
)
from app.agents.helpdesk_agent import helpdesk_agent
from app.services.ticket_service import ticket_service
from app.services.agent_execution_service import agent_execution_service

router = APIRouter()


@router.post("/agent/analyze", response_model=AgentAnalyzeResponse)
def analyze_ticket(request: AgentAnalyzeRequest):
    ticket = ticket_service.get_ticket(request.ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    ticket_dict = {
        "ticket_id": ticket.ticket_id,
        "user_query": ticket.user_query,
        "category": ticket.category,
        "subcategory": ticket.subcategory,
        "priority": ticket.priority,
        "confidence": ticket.confidence,
        "reason": ticket.reason,
        "status": ticket.status,
    }

    try:
        result = helpdesk_agent.analyze_ticket(ticket_dict)
        return AgentAnalyzeResponse(**result)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="AI model is unavailable. Please try again later.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing the ticket.",
        ) from exc


@router.post("/agent/execute", response_model=AgentExecuteResponse)
def execute_agent(request: AgentAnalyzeRequest):
    ticket = ticket_service.get_ticket(request.ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    try:
        result = agent_execution_service.execute(request.ticket_id)
        return AgentExecuteResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while executing the agent.",
        ) from exc
