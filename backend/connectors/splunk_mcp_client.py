"""
Splunk MCP Client — Model Context Protocol connector for secure Splunk data access.

Implements the MCP client specification for communicating with the Splunk MCP Server,
providing secure, protocol-compliant access to Splunk searches, indexes, and saved searches.
"""
import logging
import json
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


class SplunkMCPClient:
    """Client for the Splunk MCP (Model Context Protocol) Server."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8089,
        token: str = "",
        mcp_endpoint: str = "http://localhost:8088/mcp",
        demo_mode: bool = False,
    ):
        self.host = host
        self.port = port
        self.token = token
        self.mcp_endpoint = mcp_endpoint
        self.demo_mode = demo_mode
        self._connected = False
        self._http_client: httpx.AsyncClient | None = None

        if not demo_mode and token:
            self._http_client = httpx.AsyncClient(
                base_url=mcp_endpoint,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            self._connected = True

        logger.info(
            "SplunkMCPClient initialized (host=%s, port=%d, demo_mode=%s)",
            host, port, demo_mode,
        )

    def is_connected(self) -> bool:
        """Check if the MCP client is connected to Splunk."""
        return self._connected or self.demo_mode

    async def search(self, spl: str, earliest: str = "-24h", latest: str = "now") -> list[dict]:
        """
        Execute a SPL search query via the Splunk MCP Server.

        Uses the MCP protocol's 'tools/call' method with the search tool.
        """
        logger.info("MCP Search: %s", spl[:100])

        if self.demo_mode:
            return self._demo_search(spl)

        if not self._http_client:
            logger.warning("MCP client not connected — returning empty results")
            return []

        try:
            # MCP protocol: call the search tool
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "splunk_search",
                    "arguments": {
                        "search_query": spl,
                        "earliest_time": earliest,
                        "latest_time": latest,
                    },
                },
            }

            response = await self._http_client.post("/", json=payload)
            response.raise_for_status()
            result = response.json()

            # Parse MCP response
            if "result" in result:
                content = result["result"].get("content", [])
                if content and content[0].get("type") == "text":
                    return json.loads(content[0]["text"])
            return []

        except httpx.HTTPError as e:
            logger.error("MCP search failed: %s", str(e))
            if self.demo_mode:
                return self._demo_search(spl)
            return []

    async def get_indexes(self) -> list[str]:
        """Get available Splunk indexes via MCP."""
        if self.demo_mode:
            return ["main", "_audit", "_internal", "network", "security", "web"]

        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "splunk_list_indexes",
                    "arguments": {},
                },
            }
            response = await self._http_client.post("/", json=payload)
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                return json.loads(content[0]["text"])
            return []
        except Exception as e:
            logger.error("Failed to get indexes: %s", str(e))
            return ["main", "_audit", "_internal"]

    async def get_saved_searches(self) -> list[dict]:
        """Get saved searches via MCP."""
        if self.demo_mode:
            return [
                {"name": "Brute Force Detection", "search": 'search index=main sourcetype=auth action=failure | stats count by src_ip | where count > 20'},
                {"name": "Lateral Movement", "search": 'search index=main dest_port IN (3389, 22) | stats dc(dest_ip) by src_ip | where dc > 3'},
                {"name": "Data Exfiltration", "search": 'search index=main direction=outbound | stats sum(bytes) by src_ip | where sum > 1GB'},
            ]

        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "splunk_list_saved_searches",
                    "arguments": {},
                },
            }
            response = await self._http_client.post("/", json=payload)
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                return json.loads(content[0]["text"])
            return []
        except Exception as e:
            logger.error("Failed to get saved searches: %s", str(e))
            return []

    async def create_saved_search(self, name: str, search: str, cron: str = "*/15 * * * *") -> dict:
        """Create a new saved search via MCP."""
        if self.demo_mode:
            return {"status": "created", "name": name}

        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "splunk_create_saved_search",
                    "arguments": {
                        "name": name,
                        "search": search,
                        "cron_schedule": cron,
                    },
                },
            }
            response = await self._http_client.post("/", json=payload)
            return response.json().get("result", {})
        except Exception as e:
            logger.error("Failed to create saved search: %s", str(e))
            return {"status": "error", "message": str(e)}

    def _demo_search(self, spl: str) -> list[dict]:
        """Return demo results based on SPL query patterns."""
        spl_lower = spl.lower()

        if "alert" in spl_lower or "sample_alerts" in spl_lower:
            return self._load_sample_file("sample_alerts.json")
        if "network" in spl_lower or "traffic" in spl_lower:
            return self._load_sample_file("network_traffic.json")
        if "security" in spl_lower or "event" in spl_lower:
            return self._load_sample_file("security_events.json")

        # Generic demo response
        return [
            {"_time": "2024-12-01T08:00:00Z", "count": 42, "source": "demo"},
        ]

    def _load_sample_file(self, filename: str) -> list[dict]:
        """Load sample data file for demo mode."""
        sample_path = Path(__file__).parent.parent / "sample_data" / filename
        if sample_path.exists():
            with open(sample_path) as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        return []
