"""
Splunk SDK Client — Direct Splunk SDK integration for advanced operations.

Uses the splunk-sdk Python package for operations not available through MCP,
such as real-time searches and KV store access.
"""
import logging

try:
    import splunklib.client as splunk_client
    import splunklib.results as splunk_results
    HAS_SPLUNK_SDK = True
except ImportError:
    HAS_SPLUNK_SDK = False

logger = logging.getLogger(__name__)


class SplunkSDKClient:
    """Direct Splunk SDK client for advanced operations."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8089,
        token: str = "",
        demo_mode: bool = False,
    ):
        self.host = host
        self.port = port
        self.token = token
        self.demo_mode = demo_mode
        self._service = None

        if not demo_mode and HAS_SPLUNK_SDK and token:
            try:
                self._service = splunk_client.connect(
                    host=host,
                    port=port,
                    token=token,
                )
                logger.info("Splunk SDK connected to %s:%d", host, port)
            except Exception as e:
                logger.warning("Splunk SDK connection failed: %s", str(e))

    def is_connected(self) -> bool:
        """Check SDK connection status."""
        return self._service is not None or self.demo_mode

    def search_oneshot(self, spl: str) -> list[dict]:
        """Execute a oneshot search and return results."""
        if self.demo_mode or not self._service:
            return []

        try:
            results_stream = self._service.jobs.oneshot(spl)
            reader = splunk_results.JSONResultsReader(results_stream)
            results = []
            for item in reader:
                if isinstance(item, dict):
                    results.append(item)
            return results
        except Exception as e:
            logger.error("Oneshot search failed: %s", str(e))
            return []

    def get_indexes(self) -> list[str]:
        """List available indexes."""
        if self.demo_mode or not self._service:
            return ["main", "_audit", "_internal"]

        try:
            return [idx.name for idx in self._service.indexes]
        except Exception as e:
            logger.error("Failed to list indexes: %s", str(e))
            return []
