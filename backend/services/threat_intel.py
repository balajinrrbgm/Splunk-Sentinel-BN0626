"""
Threat Intelligence Service — Enrichment of indicators with threat context.
"""
import logging

logger = logging.getLogger(__name__)

# Demo threat intelligence database
KNOWN_MALICIOUS_IPS = {
    "185.220.101.42": {
        "type": "Tor Exit Node",
        "threat_level": "high",
        "first_seen": "2023-06-15",
        "tags": ["tor", "anonymization", "brute_force"],
        "reputation_score": 15,
    },
    "91.198.174.20": {
        "type": "Known Scanner",
        "threat_level": "medium",
        "first_seen": "2024-01-10",
        "tags": ["scanner", "web_attacks", "sql_injection"],
        "reputation_score": 25,
    },
    "203.0.113.50": {
        "type": "C2 Server",
        "threat_level": "critical",
        "first_seen": "2024-08-22",
        "tags": ["c2", "exfiltration", "apt"],
        "reputation_score": 5,
    },
}


class ThreatIntelService:
    """Threat intelligence enrichment service."""

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode

    def enrich_ip(self, ip: str) -> dict:
        """Enrich an IP address with threat intelligence."""
        if ip in KNOWN_MALICIOUS_IPS:
            return {
                "ip": ip,
                "known_malicious": True,
                **KNOWN_MALICIOUS_IPS[ip],
            }
        return {
            "ip": ip,
            "known_malicious": False,
            "threat_level": "unknown",
            "reputation_score": 50,
        }

    def enrich_indicators(self, indicators: list[str]) -> list[dict]:
        """Enrich a list of indicators."""
        return [self.enrich_ip(ip) for ip in indicators]
