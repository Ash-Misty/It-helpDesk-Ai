import pytest
from app.rag.vector_store import VectorStore, vector_store
from app.rag.retriever import Retriever, retriever
from app.rag.pipeline import RAGPipeline, rag_pipeline
from app.knowledge.knowledge_base import knowledge_base


class TestVectorStore:
    def test_build_index(self):
        docs = knowledge_base.list_all()[:3]
        vs = VectorStore()
        vs.build_index(docs)
        assert vs.is_built is True
        assert vs.count == 3

    def test_search_returns_results(self):
        docs = knowledge_base.list_all()
        vs = VectorStore()
        vs.build_index(docs)
        results = vs.search("VPN not connecting", top_k=3)
        assert len(results) >= 1
        assert "score" in results[0]

    def test_search_relevance(self):
        docs = knowledge_base.list_all()
        vs = VectorStore()
        vs.build_index(docs)
        vpn_results = vs.search("VPN connection problem", top_k=3)
        if vpn_results:
            assert "VPN" in vpn_results[0].get("category", "") or "VPN" in vpn_results[0].get("title", "")

    def test_add_document(self):
        docs = knowledge_base.list_all()[:2]
        vs = VectorStore()
        vs.build_index(docs)
        assert vs.count == 2
        vs.add_document({
            "document_id": "TEST-1",
            "title": "Test Document",
            "category": "Test",
            "troubleshooting_steps": ["Step 1", "Step 2"],
        })
        assert vs.count == 3


class TestRetriever:
    def test_retriever_search(self):
        results = retriever.search("VPN connection issue", top_k=3)
        assert len(results) >= 1
        for r in results:
            assert "document_id" in r
            assert "title" in r

    def test_retriever_category_filter(self):
        results = retriever.search("printer", top_k=3, category="Printer")
        if results:
            assert all(r["category"] == "Printer" for r in results)

    def test_retriever_builds_index_on_first_use(self):
        from app.rag.vector_store import VectorStore as VS
        fresh = VS()
        fresh_retriever = Retriever(store=fresh)
        results = fresh_retriever.search("VPN issue", top_k=2)
        assert fresh.is_built is True


class TestRAGPipeline:
    def test_search(self):
        result = rag_pipeline.search("My VPN is not connecting", top_k=3)
        assert result["success"] is True
        assert result["query"] == "My VPN is not connecting"
        assert len(result["results"]) >= 1

    def test_search_printer(self):
        result = rag_pipeline.search("My printer is not printing", top_k=3)
        assert result["success"] is True
        categories = [r["category"] for r in result["results"]]
        assert "Printer" in categories

    def test_build_context(self):
        context = rag_pipeline.build_context("VPN connection problem", top_k=2)
        assert len(context) > 0
        assert "VPN" in context or "retrieved" in context.lower()

    def test_build_context_empty_query(self):
        context = rag_pipeline.build_context("zzzqqqxxx_a1b2c3 nonsense", top_k=2)
        assert context == ""
