from typing import List, Dict, Optional
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreateRequest, VALID_STATUSES


class TicketService:
    def __init__(self):
        self.tickets: Dict[str, Ticket] = {}
        self.counter = 0

    def _next_id(self) -> str:
        self.counter += 1
        return f"IT-{self.counter:06d}"

    def create_ticket(self, request: TicketCreateRequest) -> Ticket:
        ticket_id = self._next_id()
        ticket = Ticket(
            ticket_id=ticket_id,
            user_query=request.user_query.strip(),
            category=request.category.strip(),
            subcategory=request.subcategory.strip(),
            priority=request.priority.strip(),
            confidence=request.confidence,
            reason=request.reason.strip(),
            status="Open",
        )
        self.tickets[ticket_id] = ticket
        return ticket

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return self.tickets.get(ticket_id)

    def list_tickets(self) -> List[Ticket]:
        return list(self.tickets.values())

    def update_status(self, ticket_id: str, new_status: str) -> Optional[Ticket]:
        ticket = self.tickets.get(ticket_id)
        if ticket is None:
            return None
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow().isoformat()
        return ticket


from datetime import datetime

ticket_service = TicketService()
