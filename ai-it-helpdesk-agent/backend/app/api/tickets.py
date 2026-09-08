from fastapi import APIRouter, HTTPException
from app.schemas.ticket import (
    TicketCreateRequest,
    TicketCreateResponse,
    TicketResponse,
    TicketListResponse,
    TicketUpdateStatusRequest,
)
from app.services.ticket_service import ticket_service

router = APIRouter()


def _ticket_response(ticket) -> TicketResponse:
    return TicketResponse(
        ticket_id=ticket.ticket_id,
        user_query=ticket.user_query,
        category=ticket.category,
        subcategory=ticket.subcategory,
        priority=ticket.priority,
        confidence=ticket.confidence,
        reason=ticket.reason,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


@router.post("/tickets", response_model=TicketCreateResponse)
def create_ticket(request: TicketCreateRequest):
    try:
        ticket = ticket_service.create_ticket(request)
        return TicketCreateResponse(success=True, ticket=_ticket_response(ticket))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while creating the ticket.",
        ) from exc


@router.get("/tickets", response_model=TicketListResponse)
def list_tickets():
    tickets = [_ticket_response(t) for t in ticket_service.list_tickets()]
    return TicketListResponse(success=True, tickets=tickets)


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str):
    ticket = ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return _ticket_response(ticket)


@router.patch("/tickets/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(ticket_id: str, request: TicketUpdateStatusRequest):
    ticket = ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    try:
        updated = ticket_service.update_status(ticket_id, request.status)
        if updated is None:
            raise HTTPException(status_code=404, detail="Ticket not found.")
        return _ticket_response(updated)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while updating the ticket status.",
        ) from exc
