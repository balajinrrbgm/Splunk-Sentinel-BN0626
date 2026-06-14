"""
Orchestrator Agent — Master coordinator for the SplunkSentinel agent pipeline.

Manages the lifecycle of investigations through a state machine:
PENDING → TRIAGING → INVESTIGATING → CORRELATING → FORECASTING → RESPONDING → COMPLETE
"""
import asyncio
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import AsyncGenerator

from agents.triage_agent import TriageAgent
from agents.investigation_agent import InvestigationAgent
from agents.timeline_agent import TimelineAgent
from agents.forecast_agent import ForecastAgent
from agents.response_agent import ResponseAgent
from connectors.splunk_mcp_client import SplunkMCPClient
from connectors.hosted_models_client import HostedModelsClient

logger = logging.getLogger(__name__)


class InvestigationState(str, Enum):
    PENDING = "pending"
    TRIAGING = "triaging"
    INVESTIGATING = "investigating"
    CORRELATING = "correlating"
    FORECASTING = "forecasting"
    RESPONDING = "responding"
    COMPLETE = "complete"
    ERROR = "error"


class OrchestratorAgent:
    """Master agent coordinating 5 sub-agents for autonomous SOC analysis."""

    def __init__(
        self,
        mcp_client: SplunkMCPClient,
        models_client: HostedModelsClient,
        demo_mode: bool = False,
    ):
        self.mcp_client = mcp_client
        self.models_client = models_client
        self.demo_mode = demo_mode

        # Initialize sub-agents
        self.triage_agent = TriageAgent(mcp_client, models_client, demo_mode)
        self.investigation_agent = InvestigationAgent(mcp_client, models_client, demo_mode)
        self.timeline_agent = TimelineAgent(mcp_client, models_client, demo_mode)
        self.forecast_agent = ForecastAgent(mcp_client, models_client, demo_mode)
        self.response_agent = ResponseAgent(mcp_client, models_client, demo_mode)

        # State tracking
        self.investigations: dict[str, dict] = {}
        self.agent_metrics = {
            "triage": {"processed": 0, "avg_time_ms": 0},
            "investigation": {"processed": 0, "avg_time_ms": 0},
            "timeline": {"processed": 0, "avg_time_ms": 0},
            "forecast": {"processed": 0, "avg_time_ms": 0},
            "response": {"processed": 0, "avg_time_ms": 0},
        }

        logger.info("Orchestrator Agent initialized with %d sub-agents", 5)

    def get_agent_status(self) -> dict:
        """Return status of all agents."""
        return {
            "orchestrator": "active",
            "triage_agent": "active",
            "investigation_agent": "active",
            "timeline_agent": "active",
            "forecast_agent": "active",
            "response_agent": "active",
            "metrics": self.agent_metrics,
            "active_investigations": len(
                [i for i in self.investigations.values() if i["state"] != InvestigationState.COMPLETE]
            ),
        }

    async def triage_alerts(self, limit: int = 50) -> list[dict]:
        """Run the triage agent on incoming alerts."""
        start = datetime.now(timezone.utc)
        alerts = await self.triage_agent.triage(limit=limit)
        elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        self.agent_metrics["triage"]["processed"] += len(alerts)
        self.agent_metrics["triage"]["avg_time_ms"] = round(elapsed / max(len(alerts), 1), 1)
        return alerts

    async def investigate(self, alert_id: str, context: str = "", depth: str = "full") -> dict:
        """Run a full investigation pipeline on an alert."""
        self.investigations[alert_id] = {
            "state": InvestigationState.PENDING,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "results": {},
        }

        try:
            # Phase 1: Triage
            self.investigations[alert_id]["state"] = InvestigationState.TRIAGING
            triage_result = await self.triage_agent.triage_single(alert_id)
            self.investigations[alert_id]["results"]["triage"] = triage_result

            # Phase 2: Investigation
            self.investigations[alert_id]["state"] = InvestigationState.INVESTIGATING
            investigation_result = await self.investigation_agent.investigate(
                alert_id=alert_id,
                triage_data=triage_result,
                context=context,
            )
            self.investigations[alert_id]["results"]["investigation"] = investigation_result

            # Phase 3: Timeline
            self.investigations[alert_id]["state"] = InvestigationState.CORRELATING
            timeline_result = await self.timeline_agent.reconstruct(
                alert_id=alert_id,
                investigation_data=investigation_result,
            )
            self.investigations[alert_id]["results"]["timeline"] = timeline_result

            # Phase 4: Forecast
            self.investigations[alert_id]["state"] = InvestigationState.FORECASTING
            forecast_result = await self.forecast_agent.forecast(
                alert_id=alert_id,
                context=investigation_result,
            )
            self.investigations[alert_id]["results"]["forecast"] = forecast_result

            # Phase 5: Response
            self.investigations[alert_id]["state"] = InvestigationState.RESPONDING
            response_result = await self.response_agent.recommend(
                alert_id=alert_id,
                investigation=investigation_result,
                timeline=timeline_result,
            )
            self.investigations[alert_id]["results"]["response"] = response_result

            # Complete
            self.investigations[alert_id]["state"] = InvestigationState.COMPLETE
            self.investigations[alert_id]["completed_at"] = datetime.now(timezone.utc).isoformat()

            return self.investigations[alert_id]

        except Exception as e:
            logger.error("Investigation failed for %s: %s", alert_id, str(e))
            self.investigations[alert_id]["state"] = InvestigationState.ERROR
            self.investigations[alert_id]["error"] = str(e)
            return self.investigations[alert_id]

    async def forecast_anomalies(self, metric: str, forecast_hours: int) -> dict:
        """Run anomaly forecasting for a specific metric."""
        return await self.forecast_agent.forecast_metric(
            metric=metric, hours=forecast_hours
        )

    async def build_timeline(self, alert_id: str) -> dict:
        """Reconstruct attack timeline for a specific alert."""
        investigation_data = self.investigations.get(alert_id, {}).get("results", {}).get("investigation")
        return await self.timeline_agent.reconstruct(
            alert_id=alert_id,
            investigation_data=investigation_data,
        )

    async def recommend_responses(self, alert_id: str) -> dict:
        """Get response recommendations for an alert."""
        inv = self.investigations.get(alert_id, {}).get("results", {})
        return await self.response_agent.recommend(
            alert_id=alert_id,
            investigation=inv.get("investigation"),
            timeline=inv.get("timeline"),
        )

    async def get_latest_alerts(self) -> list[dict]:
        """Get latest triaged alerts for WebSocket streaming."""
        return await self.triage_agent.get_latest(limit=10)

    async def stream_investigation(self, alert_id: str) -> AsyncGenerator[dict, None]:
        """Stream investigation progress updates via WebSocket."""
        stages = [
            (InvestigationState.TRIAGING, "🔍 Triage Agent analyzing alert severity and threat score..."),
            (InvestigationState.INVESTIGATING, "🕵️ Investigation Agent correlating events across 5 indexes..."),
            (InvestigationState.CORRELATING, "⏱️ Timeline Agent reconstructing attack kill chain..."),
            (InvestigationState.FORECASTING, "📊 Forecast Agent predicting next 24h anomaly windows..."),
            (InvestigationState.RESPONDING, "🛡️ Response Agent generating remediation playbook..."),
        ]

        # Start investigation in background
        task = asyncio.create_task(self.investigate(alert_id))

        for state, message in stages:
            yield {
                "type": "progress",
                "alert_id": alert_id,
                "state": state.value,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await asyncio.sleep(2)  # Simulate processing time for demo

        # Wait for completion
        result = await task
        yield {
            "type": "complete",
            "alert_id": alert_id,
            "state": InvestigationState.COMPLETE.value,
            "message": "✅ Investigation complete — all agents reported",
            "data": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
