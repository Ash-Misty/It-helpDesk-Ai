import pytest
from app.knowledge.knowledge_base import KnowledgeBase, knowledge_base


class TestKnowledgeBase:
    def test_initial_document_count(self):
        assert knowledge_base.count() >= 8

    def test_get_document(self):
        doc = knowledge_base.get("KB-001")
        assert doc is not None
        assert doc.title == "VPN Connection Troubleshooting"
        assert doc.category == "VPN"

    def test_get_nonexistent_document(self):
        doc = knowledge_base.get("KB-999")
        assert doc is None

    def test_get_by_category(self):
        vpn_docs = knowledge_base.get_by_category("VPN")
        assert len(vpn_docs) >= 1
        for d in vpn_docs:
            assert d.category == "VPN"

    def test_search_vpn(self):
        results = knowledge_base.search("VPN not connecting", limit=5)
        assert len(results) >= 1
        assert results[0]["category"] == "VPN"

    def test_search_printer(self):
        results = knowledge_base.search("printer offline not printing", limit=5)
        assert len(results) >= 1
        categories = [r["category"] for r in results]
        assert "Printer" in categories

    def test_search_network(self):
        results = knowledge_base.search("internet connectivity dns", limit=5)
        assert len(results) >= 1
        categories = [r["category"] for r in results]
        assert any(c in ("Network", "VPN") for c in categories)

    def test_search_email(self):
        results = knowledge_base.search("email not sending receiving", limit=5)
        assert len(results) >= 1
        categories = [r["category"] for r in results]
        assert "Email" in categories

    def test_search_security(self):
        results = knowledge_base.search("unauthorized access account hacked", limit=5)
        assert len(results) >= 1
        categories = [r["category"] for r in results]
        assert "Security" in categories

    def test_search_with_category_filter(self):
        results = knowledge_base.search("issue", category="VPN", limit=5)
        assert all(r["category"] == "VPN" for r in results)

    def test_search_no_results(self):
        results = knowledge_base.search("zzzqqqxxx_a1b2c3 nonsense", limit=5)
        assert len(results) == 0

    def test_search_returns_score(self):
        results = knowledge_base.search("VPN connection", limit=3)
        assert len(results) >= 1
        assert "score" in results[0]
        assert 0 <= results[0]["score"] <= 1

    def test_list_all(self):
        docs = knowledge_base.list_all()
        assert len(docs) >= 8
        for d in docs:
            assert "document_id" in d
            assert "title" in d
            assert "category" in d

    def test_document_structure(self):
        doc = knowledge_base.get("KB-001")
        assert doc is not None
        assert hasattr(doc, "symptoms")
        assert hasattr(doc, "possible_causes")
        assert hasattr(doc, "troubleshooting_steps")
        assert hasattr(doc, "verification_steps")
        assert len(doc.troubleshooting_steps) >= 3

    def test_all_categories_present(self):
        docs = knowledge_base.list_all()
        categories = {d["category"] for d in docs}
        expected = {"VPN", "Network", "Printer", "Email", "Operating System", "Hardware", "Software", "Security"}
        assert expected.issubset(categories)
