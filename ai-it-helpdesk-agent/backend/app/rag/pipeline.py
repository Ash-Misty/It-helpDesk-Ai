from typing import Dict, Any, Optional
from app.rag.retriever import retriever


class RAGPipeline:
    def __init__(self, retriever_instance=None):
        self._retriever = retriever_instance if retriever_instance is not None else retriever

    def search(self, query: str, top_k: int = 3, category: Optional[str] = None) -> Dict[str, Any]:
        results = self._retriever.search(query, top_k=top_k, category=category)
        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results,
        }

    def build_context(self, query: str, top_k: int = 3, category: Optional[str] = None) -> str:
        result = self.search(query, top_k=top_k, category=category)
        results = result.get("results", [])
        if not results:
            return ""
        lines = ["Retrieved relevant knowledge base documents:"]
        for i, doc in enumerate(results, 1):
            title = doc.get("title", "Unknown")
            category = doc.get("category", "")
            steps = doc.get("troubleshooting_steps", [])
            score = doc.get("score", 0)
            lines.append(f"{i}. [{category}] {title} (relevance: {score})")
            for step in steps[:4]:
                lines.append(f"   - {step}")
        return "\n".join(lines)


rag_pipeline = RAGPipeline()
