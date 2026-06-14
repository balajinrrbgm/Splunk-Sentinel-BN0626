"""
SplunkSentinel Alert Action — AI-powered alert processing using Splunk Python SDK AI.

This custom alert action triggers when saved searches fire in Splunk, sends the
alert data to the SplunkSentinel backend for AI triage and investigation, and
logs the AI analysis results back to a Splunk index.

Uses the Splunk Python SDK AI examples pattern:
https://github.com/splunk/splunk-sdk-python/tree/develop/examples/
"""
import sys
import os
import json
import logging
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename=os.path.join(os.environ.get('SPLUNK_HOME', '/opt/splunk'), 'var', 'log', 'splunk', 'sentinel_alert_action.log'),
)
logger = logging.getLogger('sentinel_alert_action')


def send_to_sentinel(alert_data: dict, backend_url: str) -> dict:
    """Send alert data to SplunkSentinel backend for AI analysis."""
    url = f"{backend_url}/api/investigate"
    payload = json.dumps({
        "alert_id": alert_data.get("sid", "unknown"),
        "context": json.dumps(alert_data.get("result", {})),
        "depth": "full",
    }).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        logger.error("Failed to connect to SplunkSentinel backend: %s", str(e))
        return {"error": str(e)}


def log_to_splunk(result: dict, session_key: str):
    """Log AI analysis results back to a Splunk index via HEC or SDK."""
    try:
        import splunklib.client as client

        service = client.connect(token=session_key)
        index = service.indexes["main"]
        event_data = json.dumps({
            "sourcetype": "sentinel:investigation",
            "event": result,
        })
        index.submit(event_data, sourcetype="sentinel:investigation")
        logger.info("Logged investigation result to Splunk index")
    except Exception as e:
        logger.error("Failed to log to Splunk: %s", str(e))


def main():
    """Main entry point for the alert action."""
    if len(sys.argv) < 2:
        logger.error("No payload file provided")
        sys.exit(1)

    # Read alert payload from Splunk
    payload_file = sys.argv[1]
    try:
        with open(payload_file, 'r') as f:
            payload = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logger.error("Failed to read payload: %s", str(e))
        sys.exit(1)

    # Extract configuration
    config = payload.get("configuration", {})
    backend_url = config.get("backend_url", "http://localhost:8000")
    session_key = payload.get("session_key", "")

    # Extract alert information
    alert_data = {
        "sid": payload.get("sid", ""),
        "search_name": payload.get("search_name", ""),
        "results_link": payload.get("results_link", ""),
        "result": payload.get("result", {}),
        "owner": payload.get("owner", ""),
        "app": payload.get("app", ""),
    }

    logger.info(
        "SplunkSentinel alert action triggered: search=%s, sid=%s",
        alert_data["search_name"],
        alert_data["sid"],
    )

    # Send to SplunkSentinel backend for AI analysis
    result = send_to_sentinel(alert_data, backend_url)

    if "error" not in result:
        logger.info(
            "Investigation complete: alert_id=%s, state=%s",
            result.get("alert_id", "unknown"),
            result.get("state", "unknown"),
        )
        # Log results back to Splunk
        if session_key:
            log_to_splunk(result, session_key)
    else:
        logger.warning("Investigation returned error: %s", result.get("error"))

    sys.exit(0)


if __name__ == "__main__":
    main()
