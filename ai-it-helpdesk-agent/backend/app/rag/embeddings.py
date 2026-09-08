import threading
from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._lock = threading.Lock()

    def _ensure_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed(self, text: str) -> np.ndarray:
        model = self._ensure_model()
        vec = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        return vec.astype(np.float32)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        model = self._ensure_model()
        vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return vecs.astype(np.float32)

    @property
    def dimension(self) -> int:
        model = self._ensure_model()
        return model.get_sentence_embedding_dimension()


embedding_service = EmbeddingService()
