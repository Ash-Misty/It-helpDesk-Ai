from typing import Dict, Any, Optional, List
from app.memory.memory_repository import memory_repository


class MemoryManager:
    def __init__(self, repository=None):
        self._repo = repository if repository is not None else memory_repository

    def store_memory(
        self,
        ticket_id: str,
        issue_summary: str,
        category: str,
        solution: str,
        outcome: str,
    ) -> Dict[str, Any]:
        entry = self._repo.store(
            ticket_id=ticket_id,
            issue_summary=issue_summary,
            category=category,
            solution=solution,
            outcome=outcome,
        )
        return {
            "success": True,
            "memory": entry.to_dict(),
        }

    def retrieve_relevant_memories(
        self, query: str, category: Optional[str] = None, top_k: int = 3
    ) -> Dict[str, Any]:
        if category:
            candidates = self._repo.get_by_category(category)
        else:
            candidates = self._repo.list_all()

        query_words = set(w.lower() for w in query.split() if len(w) > 2)
        if not query_words:
            return {
                "success": True,
                "query": query,
                "count": 0,
                "memories": [],
            }

        scored: list[tuple[float, dict]] = []
        for entry in candidates:
            haystack = f"{entry.issue_summary} {entry.category} {entry.solution} {entry.outcome}".lower()
            haystack_words = set(w for w in haystack.split() if len(w) > 2)
            overlap = len(query_words & haystack_words)
            if overlap > 0:
                scored.append((overlap, entry.to_dict()))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [entry for score, entry in scored[:top_k] if score > 0]
        return {
            "success": True,
            "query": query,
            "count": len(results),
            "memories": results,
        }

    def get_ticket_memories(self, ticket_id: str) -> Dict[str, Any]:
        entries = self._repo.get_by_ticket(ticket_id)
        return {
            "success": True,
            "ticket_id": ticket_id,
            "count": len(entries),
            "memories": [e.to_dict() for e in entries],
        }

    def get_all_memories(self) -> Dict[str, Any]:
        entries = self._repo.list_all()
        return {
            "success": True,
            "count": len(entries),
            "memories": [e.to_dict() for e in entries],
        }

    def build_memory_context(
        self, query: str, category: Optional[str] = None, max_memories: int = 2
    ) -> str:
        result = self.retrieve_relevant_memories(query, category=category, top_k=max_memories)
        memories = result.get("memories", [])
        if not memories:
            return ""
        lines = ["Relevant past memories:"]
        for m in memories:
            lines.append(f"- [{m['category']}] {m['issue_summary']}. Solution: {m['solution']}. Outcome: {m['outcome']}.")
        return "\n".join(lines)


memory_manager = MemoryManager()
