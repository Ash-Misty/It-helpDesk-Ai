import pytest
from app.memory.memory_repository import MemoryRepository, memory_repository
from app.memory.memory_manager import MemoryManager, memory_manager


@pytest.fixture(autouse=True)
def clean_repo():
    memory_repository.clear()
    yield


class TestMemoryRepository:
    def test_store_and_retrieve(self):
        entry = memory_repository.store(
            ticket_id="IT-001",
            issue_summary="VPN not connecting",
            category="VPN",
            solution="Restarted VPN client",
            outcome="Resolved",
        )
        assert entry.memory_id.startswith("MEM-")
        assert entry.ticket_id == "IT-001"
        assert entry.category == "VPN"

        loaded = memory_repository.get(entry.memory_id)
        assert loaded is not None
        assert loaded.solution == "Restarted VPN client"

    def test_get_by_ticket(self):
        memory_repository.store("IT-001", "VPN issue", "VPN", "Restart", "Resolved")
        memory_repository.store("IT-001", "Another VPN issue", "VPN", "Reinstall", "Resolved")
        memory_repository.store("IT-002", "Printer issue", "Printer", "Check cable", "Resolved")

        ticket_memories = memory_repository.get_by_ticket("IT-001")
        assert len(ticket_memories) == 2
        assert all(m.ticket_id == "IT-001" for m in ticket_memories)

    def test_get_by_category(self):
        memory_repository.store("IT-001", "VPN issue", "VPN", "Restart", "Resolved")
        memory_repository.store("IT-002", "Printer issue", "Printer", "Check cable", "Resolved")

        vpn_memories = memory_repository.get_by_category("VPN")
        assert len(vpn_memories) == 1
        assert vpn_memories[0].category == "VPN"

    def test_search_relevant_memories(self):
        memory_repository.store("IT-001", "VPN not connecting", "VPN", "Restart client", "Resolved")
        memory_repository.store("IT-002", "Printer offline", "Printer", "Check cable", "Resolved")

        results = memory_repository.search("VPN connection issue", top_k=5)
        assert len(results) >= 1
        assert results[0].category == "VPN"

    def test_search_no_results(self):
        results = memory_repository.search("completely unrelated topic xyz", top_k=5)
        assert len(results) == 0

    def test_list_all(self):
        memory_repository.store("IT-001", "VPN issue", "VPN", "Fix", "Resolved")
        memory_repository.store("IT-002", "Printer issue", "Printer", "Fix", "Resolved")
        all_memories = memory_repository.list_all()
        assert len(all_memories) == 2

    def test_clear(self):
        memory_repository.store("IT-001", "VPN issue", "VPN", "Fix", "Resolved")
        memory_repository.clear()
        assert len(memory_repository.list_all()) == 0


class TestMemoryManager:
    def test_store_memory(self):
        result = memory_manager.store_memory(
            ticket_id="IT-001",
            issue_summary="VPN not connecting",
            category="VPN",
            solution="Restarted VPN client",
            outcome="Resolved",
        )
        assert result["success"] is True
        assert "memory" in result
        assert result["memory"]["category"] == "VPN"

    def test_retrieve_relevant_memories(self):
        memory_manager.store_memory("IT-001", "VPN not connecting", "VPN", "Restart", "Resolved")
        memory_manager.store_memory("IT-002", "Printer offline", "Printer", "Check cable", "Resolved")

        result = memory_manager.retrieve_relevant_memories("VPN connection issue", top_k=5)
        assert result["success"] is True
        assert result["count"] >= 1
        assert result["memories"][0]["category"] == "VPN"

    def test_retrieve_by_category(self):
        memory_manager.store_memory("IT-001", "VPN not connecting", "VPN", "Restart", "Resolved")
        memory_manager.store_memory("IT-002", "Printer offline", "Printer", "Check cable", "Resolved")

        result = memory_manager.retrieve_relevant_memories("printer", category="Printer", top_k=5)
        assert result["count"] == 1
        assert result["memories"][0]["category"] == "Printer"

    def test_get_ticket_memories(self):
        memory_manager.store_memory("IT-001", "VPN issue 1", "VPN", "Fix 1", "Resolved")
        memory_manager.store_memory("IT-001", "VPN issue 2", "VPN", "Fix 2", "Resolved")
        memory_manager.store_memory("IT-002", "Printer issue", "Printer", "Fix", "Resolved")

        result = memory_manager.get_ticket_memories("IT-001")
        assert result["count"] == 2
        assert all(m["ticket_id"] == "IT-001" for m in result["memories"])

    def test_build_memory_context(self):
        memory_manager.store_memory("IT-001", "VPN not connecting", "VPN", "Restart", "Resolved")
        context = memory_manager.build_memory_context("My VPN is not connecting", category="VPN")
        assert "VPN" in context
        assert "Restart" in context

    def test_build_memory_context_empty(self):
        context = memory_manager.build_memory_context("completely new issue")
        assert context == ""

    def test_get_all_memories(self):
        memory_manager.store_memory("IT-001", "VPN issue", "VPN", "Fix", "Resolved")
        memory_manager.store_memory("IT-002", "Printer issue", "Printer", "Fix", "Resolved")
        result = memory_manager.get_all_memories()
        assert result["count"] == 2
