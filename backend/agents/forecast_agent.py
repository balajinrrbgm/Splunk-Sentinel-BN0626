"""
Forecast Agent — Anomaly forecasting using Cisco Deep Time Series Model.

Predicts future anomalies in network traffic, authentication patterns,
DNS queries, and data transfer volumes using Splunk's hosted time series model.
"""
import logging
import math
import random
from datetime import datetime, timezone, timedelta

from connectors.splunk_mcp_client import SplunkMCPClient
from connectors.hosted_models_client import HostedModelsClient

logger = logging.getLogger(__name__)


class ForecastAgent:
    """Anomaly forecasting agent using Cisco Deep Time Series Model."""

    def __init__(
        self,
        mcp_client: SplunkMCPClient,
        models_client: HostedModelsClient,
        demo_mode: bool = False,
    ):
        self.mcp_client = mcp_client
        self.models_client = models_client
        self.demo_mode = demo_mode

    async def forecast(self, alert_id: str, context: dict | None = None) -> dict:
        """Generate anomaly forecast related to a specific alert context."""
        logger.info("Forecast Agent generating anomaly predictions for %s", alert_id)

        if self.demo_mode:
            return self._generate_demo_forecast(alert_id)

        # Gather historical metrics from Splunk
        metrics = await self._gather_historical_metrics(alert_id, context)

        # Send to Cisco Deep Time Series Model for forecasting
        forecast = await self.models_client.forecast_timeseries(metrics)

        return {
            "alert_id": alert_id,
            "forecast": forecast,
            "risk_windows": self._identify_risk_windows(forecast),
            "spl_used": 'search index=main | timechart span=1h count by sourcetype | predict algorithm=LLP5 future_timespan=24',
        }

    async def forecast_metric(self, metric: str, hours: int = 24) -> dict:
        """Forecast anomalies for a specific metric type."""
        logger.info("Forecast Agent predicting %s for next %dh", metric, hours)

        if self.demo_mode:
            return self._generate_metric_forecast(metric, hours)

        # Query historical data for the metric
        spl_map = {
            "network_traffic": 'search index=main sourcetype=network | timechart span=1h sum(bytes) as total_bytes',
            "auth_failures": 'search index=main sourcetype=authentication action=failure | timechart span=1h count',
            "dns_queries": 'search index=main sourcetype=dns | timechart span=1h count',
            "data_transfer": 'search index=main sourcetype=network action=upload | timechart span=1h sum(bytes)',
        }

        spl = spl_map.get(metric, spl_map["network_traffic"])
        historical = await self.mcp_client.search(spl=spl + " earliest=-7d")

        # Run through Cisco DTSM
        forecast = await self.models_client.forecast_timeseries(historical or [])

        return {
            "metric": metric,
            "forecast_hours": hours,
            "data": forecast,
            "spl_used": spl,
        }

    async def _gather_historical_metrics(self, alert_id: str, context: dict | None) -> list[dict]:
        """Gather historical time series data relevant to the alert."""
        spl = f'search index=main earliest=-7d | timechart span=1h count by sourcetype'
        results = await self.mcp_client.search(spl=spl)
        return results or []

    def _identify_risk_windows(self, forecast_data: dict | list) -> list[dict]:
        """Identify high-risk time windows from forecast data."""
        risk_windows = []
        if isinstance(forecast_data, list):
            for point in forecast_data:
                if point.get("anomaly_score", 0) > 0.8:
                    risk_windows.append({
                        "start": point.get("timestamp"),
                        "risk_level": "high",
                        "predicted_anomaly_score": point.get("anomaly_score"),
                    })
        return risk_windows

    def _generate_demo_forecast(self, alert_id: str) -> dict:
        """Generate demo forecast for alert context."""
        now = datetime.now(timezone.utc)
        return {
            "alert_id": alert_id,
            "forecast": self._generate_metric_forecast("network_traffic", 24),
            "risk_windows": [
                {
                    "start": (now + timedelta(hours=3)).isoformat(),
                    "end": (now + timedelta(hours=5)).isoformat(),
                    "risk_level": "high",
                    "predicted_anomaly_score": 0.89,
                    "description": "Predicted spike in outbound traffic — possible data exfiltration window",
                },
                {
                    "start": (now + timedelta(hours=14)).isoformat(),
                    "end": (now + timedelta(hours=16)).isoformat(),
                    "risk_level": "medium",
                    "predicted_anomaly_score": 0.72,
                    "description": "Unusual authentication pattern predicted — potential credential abuse",
                },
            ],
            "spl_used": 'search index=main | timechart span=1h count by sourcetype | predict algorithm=LLP5 future_timespan=24',
        }

    def _generate_metric_forecast(self, metric: str, hours: int) -> dict:
        """Generate realistic time series forecast data."""
        now = datetime.now(timezone.utc)
        historical = []
        forecast = []

        # Generate 48h of historical data
        for i in range(48):
            t = now - timedelta(hours=48 - i)
            # Simulate daily pattern with noise
            base = 1000 + 500 * math.sin(2 * math.pi * i / 24)
            value = max(0, base + random.gauss(0, 100))
            historical.append({
                "timestamp": t.isoformat(),
                "value": round(value, 1),
                "type": "historical",
            })

        # Generate forecast with confidence intervals
        for i in range(hours):
            t = now + timedelta(hours=i)
            base = 1000 + 500 * math.sin(2 * math.pi * (48 + i) / 24)
            predicted = base + random.gauss(0, 50)
            uncertainty = 50 + i * 10  # Uncertainty grows over time

            # Inject anomalies at specific points
            is_anomaly = i in [3, 4, 14, 15]
            if is_anomaly:
                predicted *= 2.5  # Anomalous spike

            forecast.append({
                "timestamp": t.isoformat(),
                "value": round(predicted, 1),
                "upper_bound": round(predicted + uncertainty, 1),
                "lower_bound": round(max(0, predicted - uncertainty), 1),
                "anomaly_score": round(0.92 if is_anomaly else random.uniform(0.1, 0.4), 2),
                "is_anomaly": is_anomaly,
                "type": "forecast",
            })

        return {
            "metric": metric,
            "forecast_hours": hours,
            "historical": historical,
            "forecast": forecast,
            "anomalies_predicted": sum(1 for f in forecast if f["is_anomaly"]),
            "model": "Cisco Deep Time Series Model",
            "confidence": "95% prediction interval",
        }
