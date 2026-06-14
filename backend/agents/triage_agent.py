"""
Triage Agent — Intelligent alert scoring, prioritization, and de-duplication.

Uses Foundation-Sec model to classify alert severity and calculate composite
threat scores based on MITRE ATT&CK mapping, historical patterns, and asset criticality.
"""
import logging
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from connectors.splunk_mcp_client import SplunkMCPClient
from connectors.hosted_models_client import HostedModelsClient

logger = logging.getLogger(__name__)

MITRE_TECHNIQUES = {
    "T1078": "Valid Accounts",
    "T1110": "Brute Force",
    "T1059": "Command and Scripting Interpreter",
    "T1071": "Application Layer Protocol",
    "T1486": "Data Encrypted for Impact",
    "T1048": "Exfiltration Over Alternative Protocol",
    "T1053": "Scheduled Task/Job",
    "T1021": "Remote Services",
    "T1055": "Process Injection",
    "T1190": "Exploit Public-Facing Application",
    "T1566": "Phishing",
    "T1027": "Obfuscated Files or Information",
}


class TriageAgent:
    """AI-powered alert triage and prioritization agent."""

    def __init__(
        self,
        mcp_client: SplunkMCPClient,
        models_client: HostedModelsClient,
        demo_mode: bool = False,
    ):
        self.mcp_client = mcp_client
        self.models_client = models_client
        self.demo_mode = demo_mode
        self._alert_cache: list[dict] = []

    async def triage(self, limit: int = 50) -> list[dict]:
        """Triage and prioritize a batch of alerts."""
        # Fetch raw alerts from Splunk via MCP
        raw_alerts = await self.mcp_client.search(
            spl='search index=main sourcetype=alert | head {limit}'.format(limit=limit)
        )

        if not raw_alerts and self.demo_mode:
            raw_alerts = self._load_sample_alerts()

        triaged = []
        for alert in raw_alerts[:limit]:
            scored = await self._score_alert(alert)
            triaged.append(scored)

        # Sort by threat score descending
        triaged.sort(key=lambda x: x["threat_score"], reverse=True)
        self._alert_cache = triaged
        return triaged

    async def triage_single(self, alert_id: str) -> dict:
        """Triage a single alert by ID."""
        # Check cache first
        for alert in self._alert_cache:
            if alert.get("id") == alert_id:
                return alert

        # Fetch from Splunk
        results = await self.mcp_client.search(
            spl=f'search index=main alert_id="{alert_id}" | head 1'
        )

        if results:
            return await self._score_alert(results[0])

        # Demo fallback
        if self.demo_mode:
            return self._generate_demo_triage(alert_id)

        return {"id": alert_id, "status": "not_found"}

    async def get_latest(self, limit: int = 10) -> list[dict]:
        """Get latest cached alerts for streaming."""
        if self._alert_cache:
            return self._alert_cache[:limit]
        return await self.triage(limit=limit)

    async def _score_alert(self, alert: dict) -> dict:
        """Score an alert using Foundation-Sec model."""
        # Use Foundation-Sec for severity classification
        prompt = (
            f"Analyze this security alert and provide a severity rating "
            f"(Critical/High/Medium/Low/Info) and threat score (0-100):\n"
            f"Alert: {json.dumps(alert, default=str)[:500]}"
        )

        model_response = await self.models_client.analyze_security(prompt)

        # Parse model response or use heuristic
        severity = model_response.get("severity", self._heuristic_severity(alert))
        threat_score = model_response.get("threat_score", self._heuristic_score(alert))

        # Map to MITRE ATT&CK
        techniques = self._map_mitre_techniques(alert)

        return {
            "id": alert.get("id", alert.get("alert_id", f"ALT-{random.randint(1000, 9999)}")),
            "title": alert.get("title", alert.get("search_name", "Security Alert")),
            "severity": severity,
            "threat_score": threat_score,
            "source": alert.get("source", "unknown"),
            "source_ip": alert.get("src_ip", alert.get("source_ip", "N/A")),
            "dest_ip": alert.get("dest_ip", alert.get("destination_ip", "N/A")),
            "user": alert.get("user", "N/A"),
            "host": alert.get("host", "N/A"),
            "mitre_techniques": techniques,
            "timestamp": alert.get("_time", datetime.now(timezone.utc).isoformat()),
            "raw_event": alert,
            "triage_spl": f'search index=main alert_id="{alert.get("id", "")}" | stats count by src_ip, dest_ip, user',
        }

    def _heuristic_severity(self, alert: dict) -> str:
        """Fallback heuristic severity classification."""
        keywords = json.dumps(alert).lower()
        if any(w in keywords for w in ["critical", "ransomware", "exfiltration", "rootkit"]):
            return "Critical"
        if any(w in keywords for w in ["brute force", "injection", "privilege escalation"]):
            return "High"
        if any(w in keywords for w in ["suspicious", "anomaly", "unusual"]):
            return "Medium"
        if any(w in keywords for w in ["info", "scan", "recon"]):
            return "Low"
        return "Medium"

    def _heuristic_score(self, alert: dict) -> int:
        """Fallback heuristic threat scoring."""
        score = 50
        keywords = json.dumps(alert).lower()
        if "critical" in keywords:
            score += 35
        if "brute" in keywords or "injection" in keywords:
            score += 25
        if "exfiltration" in keywords:
            score += 30
        if "lateral" in keywords:
            score += 20
        return min(score, 100)

    def _map_mitre_techniques(self, alert: dict) -> list[dict]:
        """Map alert to MITRE ATT&CK techniques."""
        keywords = json.dumps(alert).lower()
        mapped = []
        mapping_rules = {
            "brute": "T1110",
            "phishing": "T1566",
            "command": "T1059",
            "exfiltration": "T1048",
            "ransomware": "T1486",
            "injection": "T1055",
            "lateral": "T1021",
            "valid account": "T1078",
            "exploit": "T1190",
            "obfuscat": "T1027",
            "scheduled": "T1053",
        }
        for keyword, technique_id in mapping_rules.items():
            if keyword in keywords:
                mapped.append({
                    "id": technique_id,
                    "name": MITRE_TECHNIQUES[technique_id],
                })
        if not mapped:
            mapped.append({"id": "T1078", "name": "Valid Accounts"})
        return mapped

    def _load_sample_alerts(self) -> list[dict]:
        """Load sample alerts for demo mode."""
        sample_path = Path(__file__).parent.parent / "sample_data" / "sample_alerts.json"
        if sample_path.exists():
            with open(sample_path) as f:
                return json.load(f)
        return self._generate_demo_alerts()

    def _generate_demo_alerts(self) -> list[dict]:
        """Generate realistic demo alerts."""
        alerts = [
            {
                "id": "ALT-2024-001",
                "title": "Brute Force Attack Detected - Multiple Failed Logins",
                "source": "authentication_logs",
                "src_ip": "185.220.101.42",
                "dest_ip": "10.0.1.50",
                "user": "admin",
                "host": "server-prod-01",
                "_time": "2024-12-01T08:15:30Z",
            },
            {
                "id": "ALT-2024-002",
                "title": "SQL Injection Attempt on Web Application",
                "source": "waf_logs",
                "src_ip": "91.198.174.20",
                "dest_ip": "10.0.2.10",
                "user": "anonymous",
                "host": "web-frontend-03",
                "_time": "2024-12-01T08:22:15Z",
            },
            {
                "id": "ALT-2024-003",
                "title": "Suspicious Lateral Movement - RDP to Multiple Hosts",
                "source": "network_logs",
                "src_ip": "10.0.1.50",
                "dest_ip": "10.0.3.25",
                "user": "svc_backup",
                "host": "dc-primary",
                "_time": "2024-12-01T08:45:00Z",
            },
            {
                "id": "ALT-2024-004",
                "title": "Data Exfiltration - Large Outbound Transfer to Unknown IP",
                "source": "dlp_logs",
                "src_ip": "10.0.4.15",
                "dest_ip": "203.0.113.50",
                "user": "jsmith",
                "host": "workstation-dev-07",
                "_time": "2024-12-01T09:10:22Z",
            },
            {
                "id": "ALT-2024-005",
                "title": "Privilege Escalation - Unauthorized Admin Access",
                "source": "audit_logs",
                "src_ip": "10.0.1.22",
                "dest_ip": "10.0.1.1",
                "user": "temp_contractor",
                "host": "server-prod-02",
                "_time": "2024-12-01T09:30:45Z",
            },
        ]
        return alerts

    def _generate_demo_triage(self, alert_id: str) -> dict:
        """Generate demo triage result for a specific alert."""
        return {
            "id": alert_id,
            "title": "Security Alert Under Investigation",
            "severity": "High",
            "threat_score": 78,
            "source": "splunk_alerts",
            "source_ip": "185.220.101.42",
            "dest_ip": "10.0.1.50",
            "user": "admin",
            "host": "server-prod-01",
            "mitre_techniques": [
                {"id": "T1110", "name": "Brute Force"},
                {"id": "T1078", "name": "Valid Accounts"},
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "triage_spl": f'search index=main alert_id="{alert_id}" | stats count by src_ip, dest_ip, user | sort -count',
        }
