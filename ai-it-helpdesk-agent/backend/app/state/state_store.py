from typing import Dict, Optional
from threading import Lock
from app.schemas.state import AgentState


class InMemoryStateStore:
    def __init__(self):
        self._states: Dict[str, AgentState] = {}
        self._lock = Lock()

    def create(self, state: AgentState) -> AgentState:
        with self._lock:
            self._states[state.ticket_id] = state
            return state

    def get(self, ticket_id: str) -> Optional[AgentState]:
        with self._lock:
            state = self._states.get(ticket_id)
            return state.model_copy(deep=True) if state else None

    def update(self, ticket_id: str, state: AgentState) -> AgentState:
        with self._lock:
            self._states[ticket_id] = state
            return state.model_copy(deep=True)

    def exists(self, ticket_id: str) -> bool:
        with self._lock:
            return ticket_id in self._states

    def delete(self, ticket_id: str) -> bool:
        with self._lock:
            return self._states.pop(ticket_id, None) is not None

    def all(self) -> list[AgentState]:
        with self._lock:
            return [s.model_copy(deep=True) for s in self._states.values()]

    def clear(self):
        with self._lock:
            self._states.clear()


state_store = InMemoryStateStore()
