from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Ticket:
    ticket_id: str
    user_query: str
    category: str
    subcategory: str
    priority: str
    confidence: float
    reason: str
    status: str = "Open"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
