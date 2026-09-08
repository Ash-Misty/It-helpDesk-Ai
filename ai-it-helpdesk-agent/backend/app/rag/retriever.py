from typing import Optional
from app.rag.vector_store import vector_store
from app.knowledge.knowledge_base import knowledge_base


class Retriever:
    def __init__(self, store=None):
        self._store = store if store is not None else vector_store

    def ensure_index(self) -> None:
        if not self._store.is_built:
            docs = knowledge_base.list_all()
            self._store.build_index(docs)

    def search(self, query: str, top_k: int = 3, category: Optional[str] = None, min_score: float = 0.3) -> list[dict]:
        self.ensure_index()
        if category:
            filtered = knowledge_base.get_by_category(category)
            if filtered:
                temp_docs = [d.model_dump() if hasattr(d, "model_dump") else d for d in filtered]
                temp_store = vector_store.__class__()
                temp_store.build_index(temp_docs)
                return temp_store.search(query, top_k=top_k, min_score=min_score)
        return self._store.search(query, top_k=top_k, min_score=min_score)


retriever = Retriever()
