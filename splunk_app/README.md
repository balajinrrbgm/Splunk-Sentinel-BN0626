# SplunkSentinel — Splunk App Component

This Splunk app integrates with the SplunkSentinel AI-Powered SOC Analyst backend.

## Features

- **Custom Alert Action** (`sentinel_alert_action.py`): When Splunk alerts fire, this action sends alert data to the SplunkSentinel backend for AI-powered triage and investigation. Results are logged back to Splunk.

- **Modular Input** (`sentinel_modinput.py`): Runs continuously inside Splunk to monitor for new security events, trigger periodic forecasting analysis, and report agent health metrics.

- **Saved Searches**: Pre-configured detection rules for brute force attacks, lateral movement, data exfiltration, and anomaly forecasting.

## Installation

1. Copy this `splunk_app` directory to `$SPLUNK_HOME/etc/apps/splunk_sentinel/`
2. Restart Splunk
3. Configure the SplunkSentinel backend URL in the app settings

## Configuration

Edit `default/inputs.conf` to adjust the monitoring interval:

```ini
[sentinel_monitor]
interval = 300  # Check every 5 minutes
```

## Splunk AI Capabilities Used

- **Python SDK AI**: Alert action and modular input use the Splunk Python SDK for agentic workflows
- **AI Assistant**: SPL generation patterns integrated via the backend
- **Saved Searches**: Detection rules feed into the AI pipeline
