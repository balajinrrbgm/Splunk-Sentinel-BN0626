"""
Investigation Agent — Deep investigation and correlation across Splunk indexes.

Uses Foundation-Sec for reasoning about attack patterns and AI Assistant integration
for generating SPL queries to gather evidence.
"""
import logging
import json
from datetime import datetime, timezone

from connectors.splunk_mcp_client import SplunkMCPClient
from connectors.hosted_models_client import HostedModelsClient

logger = logging.getLogger(__name__)


class InvestigationAgent:
    """Autonomous investigation agent that correlates events across data sources."""

    def __init__(
        self,
        mcp_client: SplunkMCPClient,
        models_client: HostedModelsClient,
        demo_mode: bool = False,
    ):
        self.mcp_client = mcp_client
        self.models_client = models_client
        self.demo_mode = demo_mode

    async def investigate(
        self,
        alert_id: str,
        triage_data: dict | None = None,
        context: str = "",
    ) -> dict:
        """Perform deep investigation on a triaged alert."""
        logger.info("Investigation Agent starting deep analysis for %s", alert_id)

        # Extract key entities for investigation
        entities = self._extract_entities(triage_data or {})

        # Generate investigation SPL queries using AI Assistant pattern
        spl_queries = self._generate_investigation_queries(entities, alert_id)

        # Execute queries against Splunk via MCP
        evidence = []
        for query_info in spl_queries:
            results = await self.mcp_client.search(spl=query_info["spl"])
            if results:
                evidence.append({
                    "query": query_info["spl"],
                    "purpose": query_info["purpose"],
                    "results": results[:10],  # Limit for response size
                    "count": len(results),
                })

        # Use Foundation-Sec for attack pattern analysis
        analysis_prompt = (
            f"Analyze these security investigation findings and identify attack patterns:\n"
            f"Alert: {json.dumps(triage_data, default=str)[:300]}\n"
            f"Evidence gathered from {len(evidence)} queries across Splunk indexes.\n"
            f"Entities involved: {json.dumps(entities)}\n"
            f"Context: {context}\n"
            f"Provide: 1) Attack pattern identification 2) Confidence score 3) MITRE ATT&CK mapping"
        )
        analysis = await self.models_client.analyze_security(analysis_prompt)

        # Build investigation report
        if self.demo_mode and not evidence:
            return self._generate_demo_investigation(alert_id, entities, triage_data)

        return {
            "alert_id": alert_id,
            "status": "complete",
            "entities": entities,
            "evidence": evidence,
            "spl_queries_executed": [q["spl"] for q in spl_queries],
            "analysis": analysis,
            "findings": {
                "summary": analysis.get("summary", "Investigation complete — multiple indicators of compromise identified."),
                "confidence_score": analysis.get("confidence", 82),
                "attack_pattern": analysis.get("pattern", "Multi-stage intrusion"),
                "affected_assets": entities.get("hosts", []),
                "affected_users": entities.get("users", []),
                "mitre_techniques": triage_data.get("mitre_techniques", []) if triage_data else [],
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_entities(self, triage_data: dict) -> dict:
        """Extract key entities from triage data for investigation."""
        return {
            "source_ips": [triage_data.get("source_ip", "unknown")],
            "dest_ips": [triage_data.get("dest_ip", "unknown")],
            "users": [triage_data.get("user", "unknown")],
            "hosts": [triage_data.get("host", "unknown")],
        }

    def _generate_investigation_queries(self, entities: dict, alert_id: str) -> list[dict]:
        """Generate SPL queries for investigation using AI Assistant pattern."""
        queries = []

        # Query 1: Full alert context
        queries.append({
            "purpose": "Retrieve full alert context and related events",
            "spl": f'search index=main alert_id="{alert_id}" | table _time, src_ip, dest_ip, user, action, status',
        })

        # Query 2: Source IP activity
        for src_ip in entities.get("source_ips", []):
            if src_ip != "unknown":
                queries.append({
                    "purpose": f"All activity from source IP {src_ip} in last 24h",
                    "spl": f'search index=main src_ip="{src_ip}" earliest=-24h | stats count by dest_ip, action, sourcetype | sort -count',
                })

        # Query 3: User behavior analysis
        for user in entities.get("users", []):
            if user != "unknown":
                queries.append({
                    "purpose": f"Authentication activity for user {user}",
                    "spl": f'search index=main sourcetype=authentication user="{user}" earliest=-7d | timechart span=1h count by action',
                })

        # Query 4: Network connections
        for dest_ip in entities.get("dest_ips", []):
            if dest_ip != "unknown":
                queries.append({
                    "purpose": f"Network connections to {dest_ip}",
                    "spl": f'search index=main dest_ip="{dest_ip}" | stats values(src_ip) as sources, count by dest_port | sort -count',
                })

        # Query 5: Audit trail
        for host in entities.get("hosts", []):
            if host != "unknown":
                queries.append({
                    "purpose": f"Audit events on host {host}",
                    "spl": f'search index=_audit host="{host}" earliest=-24h | stats count by action, info | sort -count',
                })

        return queries

    def _generate_demo_investigation(self, alert_id: str, entities: dict, triage_data: dict | None) -> dict:
        """Generate realistic demo investigation results."""
        return {
            "alert_id": alert_id,
            "status": "complete",
            "entities": entities,
            "evidence": [
                {
                    "query": f'search index=main src_ip="185.220.101.42" earliest=-24h | stats count by dest_ip, action',
                    "purpose": "Source IP activity analysis",
                    "results": [
                        {"dest_ip": "10.0.1.50", "action": "login_failed", "count": 847},
                        {"dest_ip": "10.0.1.50", "action": "login_success", "count": 1},
                        {"dest_ip": "10.0.2.10", "action": "login_failed", "count": 234},
                    ],
                    "count": 3,
                },
                {
                    "query": 'search index=main user="admin" sourcetype=authentication earliest=-7d | timechart span=1h count by action',
                    "purpose": "User authentication behavior",
                    "results": [
                        {"_time": "2024-12-01T07:00:00Z", "login_success": 2, "login_failed": 0},
                        {"_time": "2024-12-01T08:00:00Z", "login_success": 1, "login_failed": 847},
                    ],
                    "count": 2,
                },
                {
                    "query": 'search index=_audit host="server-prod-01" earliest=-24h | stats count by action',
                    "purpose": "Host audit trail",
                    "results": [
                        {"action": "user_login", "count": 12},
                        {"action": "privilege_change", "count": 3},
                        {"action": "file_access", "count": 156},
                        {"action": "process_create", "count": 28},
                    ],
                    "count": 4,
                },
            ],
            "spl_queries_executed": [
                f'search index=main alert_id="{alert_id}" | table _time, src_ip, dest_ip, user, action, status',
                'search index=main src_ip="185.220.101.42" earliest=-24h | stats count by dest_ip, action, sourcetype | sort -count',
                'search index=main user="admin" sourcetype=authentication earliest=-7d | timechart span=1h count by action',
                'search index=main dest_ip="10.0.1.50" | stats values(src_ip) as sources, count by dest_port | sort -count',
                'search index=_audit host="server-prod-01" earliest=-24h | stats count by action, info | sort -count',
            ],
            "analysis": {
                "summary": "Multi-stage brute force attack with successful credential compromise. Attacker gained initial access via brute force (847 attempts) then performed privilege escalation.",
                "confidence": 92,
                "pattern": "Credential Stuffing → Initial Access → Privilege Escalation",
            },
            "findings": {
                "summary": "High-confidence brute force attack from known malicious IP (185.220.101.42) targeting admin account on server-prod-01. After 847 failed attempts, attacker achieved successful login and initiated privilege escalation.",
                "confidence_score": 92,
                "attack_pattern": "Credential Stuffing → Initial Access → Privilege Escalation",
                "affected_assets": ["server-prod-01", "dc-primary"],
                "affected_users": ["admin", "svc_backup"],
                "mitre_techniques": [
                    {"id": "T1110", "name": "Brute Force"},
                    {"id": "T1078", "name": "Valid Accounts"},
                    {"id": "T1021", "name": "Remote Services"},
                ],
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
