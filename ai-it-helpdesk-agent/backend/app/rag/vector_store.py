import threading
from typing import Optional
import numpy as np
from app.rag.embeddings import embedding_service


class VectorStore:
    def __init__(self):
        self._embeddings: list[np.ndarray] = []
        self._documents: list[dict] = []
        self._lock = threading.Lock()
        self._built = False

    def _l2_normalize(self, vec: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm

    def build_index(self, documents: list[dict]) -> None:
        texts = []
        for doc in documents:
            combined = " ".join([
                doc.get("title", ""),
                doc.get("category", ""),
                doc.get("subcategory", ""),
                " ".join(doc.get("symptoms", [])),
                " ".join(doc.get("possible_causes", [])),
                " ".join(doc.get("troubleshooting_steps", [])),
            ])
            texts.append(combined)

        vectors = embedding_service.embed_batch(texts)
        with self._lock:
            self._embeddings = [self._l2_normalize(v) for v in vectors]
            self._documents = list(documents)
            self._built = True

    def add_document(self, document: dict) -> None:
        text = " ".join([
            document.get("title", ""),
            document.get("category", ""),
            document.get("subcategory", ""),
            " ".join(document.get("symptoms", [])),
            " ".join(document.get("possible_causes", [])),
            " ".join(document.get("troubleshooting_steps", [])),
        ])
        vec = embedding_service.embed(text)
        vec = self._l2_normalize(vec)
        with self._lock:
            self._embeddings.append(vec)
            self._documents.append(document)
            self._built = True

    def search(self, query: str, top_k: int = 3, min_score: float = 0.3) -> list[dict]:
        if not self._built:
            return []

        query_vec = embedding_service.embed(query)
        query_vec = self._l2_normalize(query_vec)

        with self._lock:
            if not self._embeddings:
                return []
            matrix = np.array(self._embeddings, dtype=np.float32)
            scores = matrix @ query_vec

        mask = scores >= min_score
        filtered_indices = np.where(mask)[0]
        filtered_scores = scores[filtered_indices]

        sorted_order = np.argsort(filtered_scores)[::-1]
        top_indices = filtered_indices[sorted_order][:top_k]

        results = []
        for idx in top_indices:
            doc = self._documents[idx]
            doc_copy = dict(doc)
            doc_copy["score"] = float(scores[idx])
            results.append(doc_copy)
        return results

    @property
    def is_built(self) -> bool:
        return self._built

    @property
    def count(self) -> int:
        return len(self._documents)


vector_store = VectorStore()
