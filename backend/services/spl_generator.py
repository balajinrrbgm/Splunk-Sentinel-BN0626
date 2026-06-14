"""
SPL Generator — AI-powered SPL query generation using Splunk AI Assistant pattern.

Generates valid SPL (Search Processing Language) queries from natural language
investigation questions, with validation and template support.
"""
import logging
from typing import Optional

from connectors.hosted_models_client import HostedModelsClient

logger = logging.getLogger(__name__)

# Common SPL query templates for security investigations
SPL_TEMPLATES = {
    "brute_force": (
        'search index=main sourcetype=authentication action=failure '
        '| stats count by src_ip, user '
        '| where count > {threshold} '
        '| sort -count'
    ),
    "lateral_movement": (
        'search index=main (dest_port=3389 OR dest_port=22 OR dest_port=445) '
        '| stats dc(dest_ip) as target_count, values(dest_ip) as targets by src_ip '
        '| where target_count > 3 '
        '| sort -target_count'
    ),
    "data_exfiltration": (
        'search index=main sourcetype=network direction=outbound '
        '| stats sum(bytes) as total_bytes by src_ip, dest_ip '
        '| where total_bytes > 1073741824 '
        '| sort -total_bytes'
    ),
    "privilege_escalation": (
        'search index=_audit action=privilege_change OR action=role_change '
        '| stats count by user, host, action '
        '| sort -count'
    ),
    "suspicious_dns": (
        'search index=main sourcetype=dns '
        '| eval domain_length=len(query) '
        '| where domain_length > 50 OR query_type="TXT" '
        '| stats count by query, src_ip '
        '| sort -count'
    ),
    "user_activity": (
        'search index=main user="{user}" earliest=-{timespan} '
        '| stats count by action, host, sourcetype '
        '| sort -count'
    ),
    "ip_activity": (
        'search index=main src_ip="{ip}" earliest=-{timespan} '
        '| stats count by dest_ip, dest_port, action '
        '| sort -count'
    ),
    "host_audit": (
        'search index=_audit host="{host}" earliest=-{timespan} '
        '| stats count by action, user, info '
        '| sort -count'
    ),
}


class SPLGenerator:
    """AI-powered SPL query generation service."""

    def __init__(self, models_client: Optional[HostedModelsClient] = None):
        self.models_client = models_client

    async def generate_from_natural_language(self, question: str) -> dict:
        """
        Generate an SPL query from a natural language question.
        Uses AI Assistant pattern for intelligent query construction.
        """
        # Try template matching first
        template_result = self._match_template(question)
        if template_result:
            return template_result

        # Fall back to AI-generated SPL
        if self.models_client:
            prompt = (
                f"Generate a valid Splunk SPL query for this investigation question:\n"
                f"Question: {question}\n"
                f"Rules: Use proper SPL syntax, include index specification, "
                f"add stats/table commands for readable output."
            )
            response = await self.models_client.analyze_security(prompt)
            return {
                "spl": response.get("summary", "search index=main | head 100"),
                "source": "ai_assistant",
                "confidence": response.get("confidence", 70),
            }

        return {
            "spl": "search index=main | head 100",
            "source": "fallback",
            "confidence": 30,
        }

    def generate_for_entity(self, entity_type: str, entity_value: str, timespan: str = "24h") -> str:
        """Generate an SPL query for investigating a specific entity."""
        if entity_type == "ip":
            return SPL_TEMPLATES["ip_activity"].format(ip=entity_value, timespan=timespan)
        elif entity_type == "user":
            return SPL_TEMPLATES["user_activity"].format(user=entity_value, timespan=timespan)
        elif entity_type == "host":
            return SPL_TEMPLATES["host_audit"].format(host=entity_value, timespan=timespan)
        else:
            return f'search index=main "{entity_value}" earliest=-{timespan} | head 100'

    def _match_template(self, question: str) -> Optional[dict]:
        """Match question to known SPL templates."""
        q_lower = question.lower()

        if "brute force" in q_lower or "failed login" in q_lower:
            return {
                "spl": SPL_TEMPLATES["brute_force"].format(threshold=20),
                "source": "template",
                "template": "brute_force",
                "confidence": 95,
            }
        if "lateral" in q_lower or "movement" in q_lower:
            return {
                "spl": SPL_TEMPLATES["lateral_movement"],
                "source": "template",
                "template": "lateral_movement",
                "confidence": 95,
            }
        if "exfiltration" in q_lower or "large transfer" in q_lower:
            return {
                "spl": SPL_TEMPLATES["data_exfiltration"],
                "source": "template",
                "template": "data_exfiltration",
                "confidence": 95,
            }
        if "privilege" in q_lower or "escalation" in q_lower:
            return {
                "spl": SPL_TEMPLATES["privilege_escalation"],
                "source": "template",
                "template": "privilege_escalation",
                "confidence": 95,
            }
        if "dns" in q_lower or "domain" in q_lower:
            return {
                "spl": SPL_TEMPLATES["suspicious_dns"],
                "source": "template",
                "template": "suspicious_dns",
                "confidence": 90,
            }

        return None
