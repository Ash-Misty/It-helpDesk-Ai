from typing import Dict, List, Tuple


CATEGORIES: Dict[str, Dict[str, List[str]]] = {
    "Network": {
        "Internet Connectivity": [
            "internet", "connect to internet", "no internet", "internet not working",
            "cannot access internet", "online", "offline", "web pages not loading",
            "browsing", "surfing"
        ],
        "Wi-Fi": [
            "wifi", "wi-fi", "wireless", "wireless network", "wifi not working",
            "wifi disconnected", "wifi signal", "wifi issue", "wireless issue",
            "wireless not working"
        ],
        "LAN": [
            "lan", "local area network", "ethernet", "cable network", "wired network",
            "lan connection", "lan issue"
        ],
        "DNS": [
            "dns", "dns error", "dns issue", "dns problem", "cannot resolve",
            "server not found", "dns server"
        ],
        "Network Speed": [
            "slow network", "network speed", "bandwidth", "lag", "network lag",
            "slow connection", "connection speed", "network performance"
        ]
    },
    "Hardware": {
        "Laptop": [
            "laptop", "notebook", "macbook", "chromebook", "laptop issue",
            "laptop problem", "laptop not working"
        ],
        "Desktop": [
            "desktop", "pc", "computer", "workstation", "desktop issue",
            "desktop problem", "desktop not working", "tower"
        ],
        "Keyboard": [
            "keyboard", "keys not working", "keyboard not responding",
            "keyboard issue", "typing", "keys stuck", "keyboard problem"
        ],
        "Mouse": [
            "mouse", "mouse not working", "mouse issue", "cursor", "pointer",
            "mouse problem", "mouse not responding", "trackpad", "touchpad"
        ],
        "Monitor": [
            "monitor", "screen", "display", "black screen", "screen black",
            "monitor issue", "display issue", "screen not working", "blank screen",
            "monitor not working", "display not working"
        ],
        "Battery": [
            "battery", "battery not charging", "battery drain", "battery life",
            "power", "charging", "battery issue", "battery problem"
        ]
    },
    "Software": {
        "Application Crash": [
            "crash", "crashed", "crashing", "application crash", "app crash",
            "program crash", "software crash", "app closed", "app stopped"
        ],
        "Application Installation": [
            "install", "installation", "setup", "cannot install", "install failed",
            "installation error", "setup failed", "install issue"
        ],
        "Application Not Responding": [
            "not responding", "frozen", "hanging", "stuck", "application hang",
            "app not responding", "program frozen", "unresponsive"
        ],
        "Software Error": [
            "error", "bug", "glitch", "software error", "application error",
            "program error", "app error", "runtime error"
        ]
    },
    "Account & Access": {
        "Login": [
            "login", "log in", "sign in", "cannot login", "login failed",
            "login issue", "sign in failed", "logging in", "access account"
        ],
        "Password": [
            "password", "forgot password", "reset password", "password reset",
            "change password", "password expired", "password issue"
        ],
        "Account Locked": [
            "locked", "account locked", "locked out", "cannot access account",
            "account disabled", "locked account"
        ],
        "Permission": [
            "permission", "access denied", "unauthorized", "no permission",
            "access control", "permission denied", "cannot access", "restricted"
        ]
    },
    "Email": {
        "Cannot Send Email": [
            "cannot send email", "email not sending", "send email failed",
            "unable to send", "email sending issue", "compose email", "send failed"
        ],
        "Cannot Receive Email": [
            "cannot receive email", "email not receiving", "no emails",
            "not getting emails", "missing emails", "inbox empty", "email not arriving"
        ],
        "Email Login": [
            "email login", "email sign in", "outlook login", "webmail login",
            "email access", "cannot access email"
        ],
        "Email Sync": [
            "email sync", "sync issue", "not syncing", "calendar sync",
            "contacts sync", "sync error", "outlook sync"
        ]
    },
    "Security": {
        "Malware": [
            "malware", "virus", "antivirus", "infected", "trojan", "spyware",
            "ransomware", "security threat", "infected file"
        ],
        "Suspicious Activity": [
            "suspicious", "unusual activity", "strange activity", "unknown login",
            "suspicious email", "phishing attempt"
        ],
        "Phishing": [
            "phishing", "phishing email", "scam", "fraudulent", "fake email",
            "suspicious link", "social engineering"
        ],
        "Unauthorized Access": [
            "unauthorized access", "hacked", "breach", "intrusion",
            "security breach", "data breach", "compromised", "unauthorized"
        ]
    },
    "Printer": {
        "Printer Not Working": [
            "printer not working", "printer issue", "printer problem",
            "printer won't print", "printer failure", "printing not working"
        ],
        "Printing Error": [
            "print error", "printing error", "print failed", "error printing",
            "print job failed", "cannot print", "print issue"
        ],
        "Printer Connection": [
            "printer connection", "connect printer", "printer network",
            "printer setup", "add printer", "printer driver"
        ],
        "Printer Offline": [
            "printer offline", "offline printer", "printer status offline",
            "printer showing offline", "offline"
        ]
    },
    "Operating System": {
        "Windows Error": [
            "windows error", "blue screen", "bsod", "windows crash", "windows issue",
            "windows problem", "windows update", "windows update failed"
        ],
        "System Crash": [
            "system crash", "computer crash", "crash", "system restart",
            "unexpected restart", "system failure", "kernel panic"
        ],
        "Boot Problem": [
            "boot", "boot problem", "cannot boot", "boot failure", "startup issue",
            "won't start", "boot loop", "startup error"
        ],
        "System Performance": [
            "slow computer", "system slow", "performance", "slow pc",
            "system performance", "laggy", "computer slow", "running slow"
        ]
    },
    "VPN": {
        "VPN Connection": [
            "vpn connection", "vpn not connecting", "cannot connect vpn",
            "vpn issue", "vpn problem", "vpn disconnected", "vpn failed"
        ],
        "VPN Authentication": [
            "vpn authentication", "vpn login", "vpn password", "vpn credentials",
            "vpn auth", "vpn certificate"
        ],
        "VPN Access": [
            "vpn access", "cannot access vpn", "vpn blocked", "vpn denied",
            "remote access", "vpn tunnel"
        ]
    }
}

PRIORITY_KEYWORDS: Dict[str, Tuple[int, str]] = {
    "critical": (
        10,
        "server down, production down, entire company, security breach, data loss, "
        "critical system, business stopped, all users, outage, complete failure"
    ),
    "high": (
        5,
        "team, department, multiple users, cannot access, down, broken, urgent, "
        "important, production, emergency, all employees, widespread"
    ),
    "medium": (
        2,
        "cannot, not working, issue, problem, error, failed, fault, malfunction, "
        "unable to, difficulty"
    ),
    "low": (
        0,
        "wallpaper, minor, cosmetic, slow, annoyance, preference, suggestion, "
        "small, tiny, little"
    )
}
