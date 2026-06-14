"""
SplunkSentinel Modular Input — Continuous monitoring and forecasting trigger.

This modular input runs continuously inside Splunk to:
1. Monitor for new security events and trigger AI analysis
2. Periodically invoke the forecasting pipeline
3. Report agent health metrics back to Splunk

Uses the Splunk Python SDK modular input pattern:
https://github.com/splunk/splunk-sdk-python/tree/develop/examples/
"""
import sys
import os
import json
import time
import logging
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename=os.path.join(os.environ.get('SPLUNK_HOME', '/opt/splunk'), 'var', 'log', 'splunk', 'sentinel_modinput.log'),
)
logger = logging.getLogger('sentinel_modinput')

BACKEND_URL = os.environ.get("SENTINEL_BACKEND_URL", "http://localhost:8000")


def check_backend_health() -> dict:
    """Check SplunkSentinel backend health status."""
    try:
        url = f"{BACKEND_URL}/api/health"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logger.error("Backend health check failed: %s", str(e))
        return {"status": "unreachable", "error": str(e)}


def trigger_forecast() -> dict:
    """Trigger anomaly forecasting analysis."""
    try:
        url = f"{BACKEND_URL}/api/forecast?metric=network_traffic&hours=24"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logger.error("Forecast trigger failed: %s", str(e))
        return {"error": str(e)}


def trigger_triage() -> dict:
    """Trigger alert triage pipeline."""
    try:
        url = f"{BACKEND_URL}/api/alerts/triage?limit=50"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logger.error("Triage trigger failed: %s", str(e))
        return {"error": str(e)}


def emit_event(data: dict):
    """Emit an event to Splunk stdout (modular input pattern)."""
    event = {
        "time": time.time(),
        "sourcetype": "sentinel:metrics",
        "event": data,
    }
    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()


def get_scheme():
    """Return the modular input scheme definition."""
    return """
    <scheme>
        <title>SplunkSentinel Monitor</title>
        <description>Continuous monitoring and AI analysis trigger for SplunkSentinel</description>
        <use_external_validation>false</use_external_validation>
        <streaming_mode>simple</streaming_mode>
        <endpoint>
            <args>
                <arg name="backend_url">
                    <title>Backend URL</title>
                    <description>URL of the SplunkSentinel backend API</description>
                    <required_on_create>false</required_on_create>
                    <data_type>string</data_type>
                </arg>
                <arg name="interval">
                    <title>Check Interval</title>
                    <description>Interval in seconds between checks</description>
                    <required_on_create>false</required_on_create>
                    <data_type>number</data_type>
                </arg>
            </args>
        </endpoint>
    </scheme>
    """


def run():
    """Main modular input execution loop."""
    logger.info("SplunkSentinel modular input starting")

    # Check if running in scheme mode
    if len(sys.argv) > 1 and sys.argv[1] == "--scheme":
        print(get_scheme())
        sys.exit(0)

    cycle_count = 0

    while True:
        cycle_count += 1

        # Check backend health every cycle
        health = check_backend_health()
        emit_event({
            "type": "health_check",
            "cycle": cycle_count,
            "backend_status": health.get("status", "unknown"),
            "agents": health.get("agents", {}),
            "splunk_connected": health.get("splunk_connected", False),
        })

        # Trigger triage every cycle
        triage_result = trigger_triage()
        if "error" not in triage_result:
            emit_event({
                "type": "triage_complete",
                "cycle": cycle_count,
                "alerts_triaged": triage_result.get("total", 0),
            })

        # Trigger forecast every 12 cycles (hourly if interval=300s)
        if cycle_count % 12 == 0:
            forecast_result = trigger_forecast()
            if "error" not in forecast_result:
                emit_event({
                    "type": "forecast_complete",
                    "cycle": cycle_count,
                    "anomalies_predicted": forecast_result.get("anomalies_predicted", 0),
                })

        logger.info("Cycle %d complete", cycle_count)

        # Sleep for configured interval (default 5 minutes)
        time.sleep(300)


if __name__ == "__main__":
    run()
