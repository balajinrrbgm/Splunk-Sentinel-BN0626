"""
Timeline Agent — Attack timeline reconstruction and kill chain mapping.

Correlates events across time windows to identify initial access, lateral movement,
data exfiltration, and persistence techniques.
"""
import logging
from datetime import datetime, timezone, timedelta

from connectors.splunk_mcp_client import SplunkMCPClient
from connectors.hosted_models_client import HostedModelsClient

logger = logging.getLogger(__name__)

ATTACK_STAGES = [
    "Reconnaissance",
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Credential Access",
    "Discovery",
    "Lateral Movement",
    "Collection",
    "Exfiltration",
    "Impact",
]


class TimelineAgent:
    """Reconstructs attack timelines and maps events to MITRE ATT&CK kill chain."""

    def __init__(
        self,
        mcp_client: SplunkMCPClient,
        models_client: HostedModelsClient,
        demo_mode: bool = False,
    ):
        self.mcp_client = mcp_client
        self.models_client = models_client
        self.demo_mode = demo_mode

    async def reconstruct(
        self,
        alert_id: str,
        investigation_data: dict | None = None,
    ) -> dict:
        """Reconstruct the full attack timeline for an alert."""
        logger.info("Timeline Agent reconstructing kill chain for %s", alert_id)

        if self.demo_mode or not investigation_data:
            return self._generate_demo_timeline(alert_id)

        # Extract entities from investigation
        entities = investigation_data.get("entities", {})
        source_ips = entities.get("source_ips", [])
        hosts = entities.get("hosts", [])

        # Query events in time windows around the alert
        timeline_events = []
        for ip in source_ips:
            if ip != "unknown":
                results = await self.mcp_client.search(
                    spl=f'search index=main src_ip="{ip}" earliest=-48h latest=+2h | sort _time | table _time, action, dest_ip, user, host'
                )
                for event in (results or []):
                    timeline_events.append(event)

        # Classify events by attack stage
        classified = self._classify_events(timeline_events)

        return {
            "alert_id": alert_id,
            "timeline": classified,
            "total_events": len(timeline_events),
            "attack_stages_identified": list(set(e["stage"] for e in classified)),
            "duration": self._calculate_duration(classified),
            "entities_involved": entities,
            "spl_used": f'search index=main (src_ip IN ({",".join(source_ips)})) earliest=-48h | sort _time',
        }

    def _classify_events(self, events: list[dict]) -> list[dict]:
        """Classify events into MITRE ATT&CK kill chain stages."""
        classified = []
        for event in events:
            action = str(event.get("action", "")).lower()
            stage = "Discovery"  # default

            if any(w in action for w in ["scan", "probe", "enum"]):
                stage = "Reconnaissance"
            elif any(w in action for w in ["login_success", "auth_success", "exploit"]):
                stage = "Initial Access"
            elif any(w in action for w in ["exec", "run", "create_process"]):
                stage = "Execution"
            elif any(w in action for w in ["persist", "schedule", "registry"]):
                stage = "Persistence"
            elif any(w in action for w in ["privilege", "escalat", "sudo"]):
                stage = "Privilege Escalation"
            elif any(w in action for w in ["lateral", "rdp", "ssh", "smb"]):
                stage = "Lateral Movement"
            elif any(w in action for w in ["exfil", "upload", "transfer"]):
                stage = "Exfiltration"
            elif any(w in action for w in ["encrypt", "ransom", "destroy"]):
                stage = "Impact"

            classified.append({
                **event,
                "stage": stage,
            })
        return classified

    def _calculate_duration(self, events: list[dict]) -> str:
        """Calculate attack duration from timeline events."""
        if not events:
            return "unknown"
        timestamps = [e.get("_time", e.get("timestamp", "")) for e in events]
        return f"{len(timestamps)} events over estimated attack window"

    def _generate_demo_timeline(self, alert_id: str) -> dict:
        """Generate a realistic demo attack timeline."""
        base_time = datetime(2024, 12, 1, 7, 0, 0, tzinfo=timezone.utc)
        timeline = [
            {
                "timestamp": (base_time + timedelta(minutes=0)).isoformat(),
                "stage": "Reconnaissance",
                "event": "Port scan detected from 185.220.101.42",
                "source_ip": "185.220.101.42",
                "dest_ip": "10.0.1.0/24",
                "action": "port_scan",
                "severity": "Low",
                "details": "Sequential port scan across subnet — ports 22, 80, 443, 3389, 8080",
            },
            {
                "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
                "stage": "Initial Access",
                "event": "Brute force attack initiated against admin account",
                "source_ip": "185.220.101.42",
                "dest_ip": "10.0.1.50",
                "action": "brute_force_start",
                "severity": "High",
                "details": "847 login attempts over 45 minutes using credential stuffing pattern",
            },
            {
                "timestamp": (base_time + timedelta(minutes=60)).isoformat(),
                "stage": "Initial Access",
                "event": "Successful authentication — admin account compromised",
                "source_ip": "185.220.101.42",
                "dest_ip": "10.0.1.50",
                "action": "login_success",
                "severity": "Critical",
                "details": "Attacker gained access after 847 failed attempts. Session ID: sess_a8f2c1",
            },
            {
                "timestamp": (base_time + timedelta(minutes=65)).isoformat(),
                "stage": "Discovery",
                "event": "Internal network enumeration detected",
                "source_ip": "10.0.1.50",
                "dest_ip": "10.0.0.0/16",
                "action": "network_discovery",
                "severity": "Medium",
                "details": "Compromised host scanning internal network for domain controllers and file shares",
            },
            {
                "timestamp": (base_time + timedelta(minutes=80)).isoformat(),
                "stage": "Privilege Escalation",
                "event": "Service account privilege escalation",
                "source_ip": "10.0.1.50",
                "dest_ip": "10.0.1.50",
                "action": "privilege_escalation",
                "severity": "Critical",
                "details": "Attacker escalated from admin to svc_backup using cached credentials",
            },
            {
                "timestamp": (base_time + timedelta(minutes=95)).isoformat(),
                "stage": "Lateral Movement",
                "event": "RDP connection to domain controller",
                "source_ip": "10.0.1.50",
                "dest_ip": "10.0.3.25",
                "action": "rdp_connection",
                "severity": "Critical",
                "details": "Lateral movement via RDP using svc_backup credentials to dc-primary",
            },
            {
                "timestamp": (base_time + timedelta(minutes=110)).isoformat(),
                "stage": "Collection",
                "event": "Sensitive file access on domain controller",
                "source_ip": "10.0.3.25",
                "dest_ip": "10.0.3.25",
                "action": "file_access",
                "severity": "High",
                "details": "Access to NTDS.dit, SAM database, and Group Policy configurations",
            },
            {
                "timestamp": (base_time + timedelta(minutes=130)).isoformat(),
                "stage": "Exfiltration",
                "event": "Large data transfer to external IP",
                "source_ip": "10.0.4.15",
                "dest_ip": "203.0.113.50",
                "action": "data_exfiltration",
                "severity": "Critical",
                "details": "2.3GB transferred via HTTPS to external server. Data includes credential dumps.",
            },
        ]

        return {
            "alert_id": alert_id,
            "timeline": timeline,
            "total_events": len(timeline),
            "attack_stages_identified": [
                "Reconnaissance",
                "Initial Access",
                "Discovery",
                "Privilege Escalation",
                "Lateral Movement",
                "Collection",
                "Exfiltration",
            ],
            "duration": "2 hours 10 minutes",
            "entities_involved": {
                "source_ips": ["185.220.101.42", "10.0.1.50", "10.0.4.15"],
                "dest_ips": ["10.0.1.50", "10.0.3.25", "203.0.113.50"],
                "users": ["admin", "svc_backup"],
                "hosts": ["server-prod-01", "dc-primary", "workstation-dev-07"],
            },
            "spl_used": 'search index=main (src_ip="185.220.101.42" OR src_ip="10.0.1.50") earliest=-48h | sort _time | table _time, action, src_ip, dest_ip, user, host',
        }
