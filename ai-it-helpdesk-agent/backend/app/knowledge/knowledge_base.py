from typing import Dict, Any, Optional, List
from app.schemas.knowledge import KnowledgeDocument


KNOWLEDGE_DOCUMENTS: list[KnowledgeDocument] = [
    KnowledgeDocument(
        document_id="KB-001",
        title="VPN Connection Troubleshooting",
        category="VPN",
        subcategory="VPN Connection",
        symptoms=[
            "VPN client fails to connect",
            "VPN disconnects frequently",
            "VPN authentication error",
        ],
        possible_causes=[
            "Internet connection unavailable",
            "Incorrect VPN credentials",
            "VPN service is down",
            "Client configuration issue",
            "Firewall blocking VPN traffic",
        ],
        troubleshooting_steps=[
            "Verify internet connectivity by opening a web browser.",
            "Restart the VPN client application.",
            "Verify VPN server address and credentials.",
            "Check if the VPN service is operational via status page.",
            "Temporarily disable firewall to test connectivity.",
            "Update VPN client to the latest version.",
        ],
        verification_steps=[
            "Confirm VPN connection is established.",
            "Verify access to internal resources through VPN.",
        ],
        escalation_notes="Escalate if credentials are confirmed correct but connection still fails after all steps.",
    ),
    KnowledgeDocument(
        document_id="KB-002",
        title="VPN Credential Troubleshooting",
        category="VPN",
        subcategory="VPN Credentials",
        symptoms=[
            "VPN authentication failed",
            "Invalid username or password",
            "Certificate error",
        ],
        possible_causes=[
            "Expired password",
            "Account locked",
            "Certificate expired",
            "MFA not configured",
        ],
        troubleshooting_steps=[
            "Verify username format (DOMAIN\\\\username).",
            "Check if password has expired.",
            "Verify MFA enrollment status.",
            "Check certificate validity in the VPN client.",
        ],
        verification_steps=[
            "Successful VPN authentication.",
            "Access to internal resources confirmed.",
        ],
        escalation_notes="Escalate to identity management if account is locked or MFA is broken.",
    ),
    KnowledgeDocument(
        document_id="KB-003",
        title="Network Connectivity Troubleshooting",
        category="Network",
        subcategory="Internet Connectivity",
        symptoms=[
            "Cannot access websites",
            "No internet connection",
            "Slow internet speed",
        ],
        possible_causes=[
            "Internet service outage",
            "Network cable unplugged",
            "Wi-Fi disconnected",
            "DNS server issue",
            "Router/modem failure",
        ],
        troubleshooting_steps=[
            "Check physical network cable connections.",
            "Restart the router and modem.",
            "Verify Wi-Fi connection and signal strength.",
            "Flush DNS cache: ipconfig /flushdns.",
            "Try accessing a different network (mobile hotspot).",
        ],
        verification_steps=[
            "Websites load successfully.",
            "Ping to external IP succeeds.",
        ],
        escalation_notes="Escalate if the entire office/network segment is affected.",
    ),
    KnowledgeDocument(
        document_id="KB-004",
        title="DNS Resolution Troubleshooting",
        category="Network",
        subcategory="DNS",
        symptoms=[
            "Cannot resolve domain names",
            "Sites load by IP but not by name",
            "DNS server not responding",
        ],
        possible_causes=[
            "DNS server down",
            "DNS cache corruption",
            "Incorrect DNS configuration",
            "Hosts file misconfiguration",
        ],
        troubleshooting_steps=[
            "Flush DNS cache: ipconfig /flushdns.",
            "Check DNS server settings: ipconfig /all.",
            "Try using public DNS (8.8.8.8 or 1.1.1.1).",
            "Ping the DNS server to verify reachability.",
        ],
        verification_steps=[
            "nslookup example.com returns valid IP.",
            "Websites load by domain name.",
        ],
        escalation_notes="Escalate if DNS servers are unreachable from multiple devices.",
    ),
    KnowledgeDocument(
        document_id="KB-005",
        title="Printer Troubleshooting",
        category="Printer",
        subcategory="Printer Offline",
        symptoms=[
            "Printer shows offline",
            "Print jobs stuck in queue",
            "Printer not found on network",
        ],
        possible_causes=[
            "Printer powered off",
            "Network cable unplugged",
            "Print spooler service stopped",
            "Driver issue",
            "Printer out of paper or toner",
        ],
        troubleshooting_steps=[
            "Verify printer is powered on and has paper/toner.",
            "Check network cable or Wi-Fi connection.",
            "Restart the print spooler service.",
            "Clear stuck print jobs from the queue.",
            "Reinstall or update printer drivers.",
        ],
        verification_steps=[
            "Printer shows online status.",
            "Test page prints successfully.",
        ],
        escalation_notes="Escalate if hardware error codes are displayed on the printer.",
    ),
    KnowledgeDocument(
        document_id="KB-006",
        title="Email Troubleshooting",
        category="Email",
        subcategory="Email Access",
        symptoms=[
            "Cannot send or receive email",
            "Email client shows authentication error",
            "Email sync issues",
        ],
        possible_causes=[
            "Incorrect email settings",
            "Password expired",
            "Mail server down",
            "Storage quota exceeded",
            "Spam filter blocking messages",
        ],
        troubleshooting_steps=[
            "Verify email client settings (IMAP/SMTP/Exchange).",
            "Check password and account lock status.",
            "Verify mail server is operational.",
            "Check mailbox quota usage.",
            "Review spam/junk folder for missing messages.",
        ],
        verification_steps=[
            "Send and receive test email successfully.",
            "Calendar sync works if applicable.",
        ],
        escalation_notes="Escalate if mail server is confirmed down for multiple users.",
    ),
    KnowledgeDocument(
        document_id="KB-007",
        title="Operating System Troubleshooting",
        category="Operating System",
        subcategory="System Performance",
        symptoms=[
            "Computer running slowly",
            "System crashes or freezes",
            "Blue screen errors",
        ],
        possible_causes=[
            "Low disk space",
            "Insufficient RAM",
            "Outdated drivers",
            "Malware infection",
            "Overheating",
        ],
        troubleshooting_steps=[
            "Check available disk space.",
            "Check CPU and memory usage in Task Manager.",
            "Run disk cleanup and remove temporary files.",
            "Update drivers and Windows updates.",
            "Run antivirus scan.",
        ],
        verification_steps=[
            "System boots without errors.",
            "Performance improves after cleanup.",
        ],
        escalation_notes="Escalate if blue screen errors persist or data loss is suspected.",
    ),
    KnowledgeDocument(
        document_id="KB-008",
        title="Hardware Troubleshooting",
        category="Hardware",
        subcategory="Desktop",
        symptoms=[
            "Computer will not turn on",
            "Peripheral not detected",
            "Strange noises from hardware",
        ],
        possible_causes=[
            "Power supply failure",
            "Loose cable connections",
            "Failing hard drive",
            "Overheating",
            "Faulty peripheral",
        ],
        troubleshooting_steps=[
            "Check power cables and outlet.",
            "Listen for beep codes during boot.",
            "Check disk space and SMART status.",
            "Verify peripheral connections.",
            "Test with alternate cables or ports.",
        ],
        verification_steps=[
            "Device powers on successfully.",
            "All peripherals detected and functional.",
        ],
        escalation_notes="Escalate if hardware replacement is suspected.",
    ),
    KnowledgeDocument(
        document_id="KB-009",
        title="Software Application Troubleshooting",
        category="Software",
        subcategory="Application Crash",
        symptoms=[
            "Application crashes on startup",
            "Application freezes",
            "Error messages in application",
        ],
        possible_causes=[
            "Corrupted installation",
            "Missing dependencies",
            "Incompatible version",
            "Insufficient permissions",
            "Conflicting software",
        ],
        troubleshooting_steps=[
            "Restart the application.",
            "Run as administrator.",
            "Check for application updates.",
            "Reinstall the application.",
            "Check Windows Event Viewer for error details.",
        ],
        verification_steps=[
            "Application starts without errors.",
            "Core functionality works as expected.",
        ],
        escalation_notes="Escalate if application is business-critical and reinstallation does not help.",
    ),
    KnowledgeDocument(
        document_id="KB-010",
        title="Security Incident Response",
        category="Security",
        subcategory="Unauthorized Access",
        symptoms=[
            "Suspicious account activity",
            "Unknown login locations",
            "Password changed without knowledge",
        ],
        possible_causes=[
            "Phishing attack",
            "Weak password compromised",
            "Session hijacking",
            "Malware infection",
        ],
        troubleshooting_steps=[
            "Verify user identity through secondary channel.",
            "Check active sessions and login history.",
            "Force password reset immediately.",
            "Scan system for malware.",
            "Enable MFA if not already enabled.",
        ],
        verification_steps=[
            "Only authorized sessions remain active.",
            "User can log in with new credentials.",
        ],
        escalation_notes="ALWAYS escalate security incidents to the security team immediately. Do not attempt to investigate independently.",
    ),
]


class KnowledgeBase:
    def __init__(self, documents: Optional[List[KnowledgeDocument]] = None):
        self._docs: dict[str, KnowledgeDocument] = {}
        self._by_category: dict[str, list[str]] = {}
        if documents:
            for doc in documents:
                self.index_document(doc)

    def index_document(self, doc: KnowledgeDocument) -> None:
        self._docs[doc.document_id] = doc
        cat = doc.category.lower().strip()
        self._by_category.setdefault(cat, []).append(doc.document_id)

    def get(self, document_id: str) -> Optional[KnowledgeDocument]:
        return self._docs.get(document_id)

    def get_by_category(self, category: str) -> list[KnowledgeDocument]:
        cat = category.lower().strip()
        ids = self._by_category.get(cat, [])
        return [self._docs[mid] for mid in ids if mid in self._docs]

    def search(self, query: str, category: Optional[str] = None, limit: int = 5) -> list[dict]:
        query_words = set(w.lower() for w in query.split() if len(w) > 2)
        if not query_words:
            return []

        candidates = list(self._docs.values())
        if category:
            candidates = [d for d in candidates if d.category.lower() == category.lower()]

        scored: list[tuple[float, KnowledgeDocument]] = []
        for doc in candidates:
            haystack = " ".join([
                doc.title, doc.category, doc.subcategory,
                " ".join(doc.symptoms), " ".join(doc.possible_causes),
                " ".join(doc.troubleshooting_steps),
            ]).lower()
            haystack_words = set(w for w in haystack.split() if len(w) > 2)
            overlap = len(query_words & haystack_words)
            if overlap > 0:
                scored.append((overlap, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for _, doc in scored[:limit]:
            results.append({
                "document_id": doc.document_id,
                "title": doc.title,
                "category": doc.category,
                "subcategory": doc.subcategory,
                "symptoms": doc.symptoms,
                "possible_causes": doc.possible_causes,
                "troubleshooting_steps": doc.troubleshooting_steps,
                "verification_steps": doc.verification_steps,
                "escalation_notes": doc.escalation_notes,
                "score": _normalize_score(scored[0][0] if scored else 0),
            })
        return results

    def list_all(self) -> list[dict]:
        return [d.model_dump() for d in self._docs.values()]

    def count(self) -> int:
        return len(self._docs)


def _normalize_score(raw_score: float) -> float:
    return min(round(raw_score / 10.0, 2), 1.0)


knowledge_base = KnowledgeBase(KNOWLEDGE_DOCUMENTS)
