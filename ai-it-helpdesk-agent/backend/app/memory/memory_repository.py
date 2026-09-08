from typing import Optional


class MemoryEntry:
    def __init__(
        self,
        memory_id: str,
        ticket_id: str,
        issue_summary: str,
        category: str,
        solution: str,
        outcome: str,
    ):
        self.memory_id = memory_id
        self.ticket_id = ticket_id
        self.issue_summary = issue_summary
        self.category = category
        self.solution = solution
        self.outcome = outcome

    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "ticket_id": self.ticket_id,
            "issue_summary": self.issue_summary,
            "category": self.category,
            "solution": self.solution,
            "outcome": self.outcome,
        }


class MemoryRepository:
    def __init__(self):
        self._memories: dict[str, MemoryEntry] = {}
        self._by_category: dict[str, list[str]] = {}
        self._counter = 0

    def store(self, ticket_id: str, issue_summary: str, category: str,
              solution: str, outcome: str) -> MemoryEntry:
        self._counter += 1
        memory_id = f"MEM-{self._counter:06d}"
        entry = MemoryEntry(
            memory_id=memory_id,
            ticket_id=ticket_id,
            issue_summary=issue_summary,
            category=category,
            solution=solution,
            outcome=outcome,
        )
        self._memories[memory_id] = entry
        cat = category.lower().strip()
        self._by_category.setdefault(cat, []).append(memory_id)
        return entry

    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        return self._memories.get(memory_id)

    def get_by_ticket(self, ticket_id: str) -> list[MemoryEntry]:
        return [m for m in self._memories.values() if m.ticket_id == ticket_id]

    def get_by_category(self, category: str) -> list[MemoryEntry]:
        cat = category.lower().strip()
        ids = self._by_category.get(cat, [])
        return [self._memories[mid] for mid in ids if mid in self._memories]

    def search(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        query_words = set(query.lower().split())
        scored: list[tuple[float, MemoryEntry]] = []
        for entry in self._memories.values():
            haystack = f"{entry.issue_summary} {entry.category} {entry.solution}".lower()
            haystack_words = set(haystack.split())
            overlap = len(query_words & haystack_words)
            if overlap > 0:
                scored.append((overlap, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]

    def list_all(self) -> list[MemoryEntry]:
        return list(self._memories.values())

    def clear(self):
        self._memories.clear()
        self._by_category.clear()
        self._counter = 0


memory_repository = MemoryRepository()
