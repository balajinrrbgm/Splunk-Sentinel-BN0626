"""
Response Agent — Automated response recommendation and playbook generation.

Uses Foundation-Sec to generate tailored response recommendations categorized
as Immediate, Short-term, and Long-term actions with executable SPL queries.
"""
import logging
from datetime import datetime, timezone

from connectors.splunk_mcp_client import SplunkMCPClient
from connectors.hosted_models_client import HostedModelsClient

logger = logging.getLogger(__name__)


class ResponseAgent:
    """AI-powered response recommendation agent."""

    def __init__(
        self,
        mcp_client: SplunkMCPClient,
        models_client: HostedModelsClient,
        demo_mode: bool = False,
    ):
        self.mcp_client = mcp_client
        self.models_client = models_client
        self.demo_mode = demo_mode

    async def recommend(
        self,
        alert_id: str,
        investigation: dict | None = None,
        timeline: dict | None = None,
    ) -> dict:
        """Generate response recommendations based on investigation findings."""
        logger.info("Response Agent generating playbook for %s", alert_id)

        if self.demo_mode or not investigation:
            return self._generate_demo_response(alert_id)

        # Use Foundation-Sec for response generation
        prompt = (
            f"Based on this security investigation, generate a response playbook:\n"
            f"Findings: {investigation.get('findings', {}).get('summary', '')}\n"
            f"Attack Pattern: {investigation.get('findings', {}).get('attack_pattern', '')}\n"
            f"Affected Assets: {investigation.get('findings', {}).get('affected_assets', [])}\n"
            f"MITRE Techniques: {investigation.get('findings', {}).get('mitre_techniques', [])}\n"
            f"Provide categorized response actions: Immediate, Short-term, Long-term"
        )

        response = await self.models_client.analyze_security(prompt)

        return {
            "alert_id": alert_id,
            "playbook": response.get("playbook", self._generate_demo_response(alert_id)["playbook"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_demo_response(self, alert_id: str) -> dict:
        """Generate a comprehensive demo response playbook."""
        return {
            "alert_id": alert_id,
            "severity": "Critical",
            "playbook": {
                "title": "Brute Force Attack with Lateral Movement — Response Playbook",
                "generated_by": "Foundation-Sec-1.1-8B-Instruct",
                "immediate_actions": [
                    {
                        "action": "Block attacker IP at firewall",
                        "priority": 1,
                        "description": "Immediately block the source IP to prevent further access attempts",
                        "spl": '| makeresults | eval action="block", ip="185.220.101.42" | sendalert firewall_block',
                        "automated": True,
                    },
                    {
                        "action": "Disable compromised admin account",
                        "priority": 2,
                        "description": "Disable the admin account that was compromised to prevent further abuse",
                        "spl": '| makeresults | eval action="disable_account", user="admin" | sendalert ad_account_action',
                        "automated": True,
                    },
                    {
                        "action": "Terminate active sessions from compromised accounts",
                        "priority": 3,
                        "description": "Kill all active sessions associated with compromised credentials",
                        "spl": 'search index=main sourcetype=authentication user IN ("admin", "svc_backup") action=session_active | sendalert session_terminator',
                        "automated": True,
                    },
                    {
                        "action": "Isolate affected hosts from network",
                        "priority": 4,
                        "description": "Network-isolate server-prod-01 and dc-primary to contain lateral movement",
                        "spl": '| makeresults | eval action="isolate", hosts="server-prod-01,dc-primary" | sendalert network_isolate',
                        "automated": False,
                    },
                ],
                "short_term_actions": [
                    {
                        "action": "Rotate all credentials on affected systems",
                        "priority": 1,
                        "description": "Force password reset for all accounts that accessed compromised systems",
                        "spl": 'search index=_audit host IN ("server-prod-01", "dc-primary") earliest=-24h | stats dc(user) as affected_users | sendalert credential_rotation',
                        "timeframe": "Within 4 hours",
                    },
                    {
                        "action": "Update firewall rules for Tor exit nodes",
                        "priority": 2,
                        "description": "Block all known Tor exit node IPs at network perimeter",
                        "spl": '| inputlookup tor_exit_nodes.csv | eval action="block" | sendalert firewall_bulk_block',
                        "timeframe": "Within 4 hours",
                    },
                    {
                        "action": "Enable enhanced logging on critical systems",
                        "priority": 3,
                        "description": "Increase audit logging verbosity on domain controllers and production servers",
                        "spl": '| makeresults | eval hosts="dc-primary,server-prod-01,server-prod-02" | sendalert enable_enhanced_audit',
                        "timeframe": "Within 8 hours",
                    },
                    {
                        "action": "Scan for persistence mechanisms",
                        "priority": 4,
                        "description": "Check for scheduled tasks, registry modifications, and unauthorized services",
                        "spl": 'search index=main host IN ("server-prod-01", "dc-primary") (sourcetype=WinRegistry OR sourcetype=scheduled_tasks) earliest=-24h | stats count by host, action, path',
                        "timeframe": "Within 12 hours",
                    },
                ],
                "long_term_actions": [
                    {
                        "action": "Implement MFA for all admin accounts",
                        "priority": 1,
                        "description": "Enforce multi-factor authentication for all privileged accounts to prevent credential-based attacks",
                        "timeframe": "Within 1 week",
                    },
                    {
                        "action": "Deploy network segmentation",
                        "priority": 2,
                        "description": "Segment production network to limit lateral movement paths between workstations and domain controllers",
                        "timeframe": "Within 2 weeks",
                    },
                    {
                        "action": "Implement account lockout policies",
                        "priority": 3,
                        "description": "Configure account lockout after 5 failed attempts with 30-minute lockout duration",
                        "timeframe": "Within 1 week",
                    },
                    {
                        "action": "Create monitoring saved searches",
                        "priority": 4,
                        "description": "Deploy ongoing detection rules for similar attack patterns",
                        "spl": 'search index=main sourcetype=authentication action=failure | stats count by src_ip, user | where count > 50 | sendalert brute_force_detection',
                        "timeframe": "Within 3 days",
                    },
                ],
                "monitoring_queries": [
                    {
                        "name": "Brute Force Detection",
                        "spl": 'search index=main sourcetype=authentication action=failure earliest=-1h | stats count by src_ip, user | where count > 20',
                        "schedule": "Every 15 minutes",
                    },
                    {
                        "name": "Lateral Movement Detection",
                        "spl": 'search index=main sourcetype=network (dest_port=3389 OR dest_port=22) | stats dc(dest_ip) as targets by src_ip | where targets > 3',
                        "schedule": "Every 5 minutes",
                    },
                    {
                        "name": "Data Exfiltration Monitor",
                        "spl": 'search index=main sourcetype=network direction=outbound | stats sum(bytes) as total_bytes by src_ip | where total_bytes > 1073741824',
                        "schedule": "Every 30 minutes",
                    },
                ],
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
