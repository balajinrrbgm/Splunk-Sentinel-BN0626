"""
SplunkSentinel Backend — AI-Powered Autonomous SOC Analyst
FastAPI server orchestrating multi-agent security analysis pipeline.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from datetime import datetime, timezone

from config import Settings
from agents.orchestrator import OrchestratorAgent
from connectors.splunk_mcp_client import SplunkMCPClient
from connectors.hosted_models_client import HostedModelsClient
from models.alert import InvestigationRequest
from services.report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = Settings()

orchestrator: OrchestratorAgent | None = None
mcp_client: SplunkMCPClient | None = None
models_client: HostedModelsClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agents and connections on startup."""
    global orchestrator, mcp_client, models_client

    mcp_client = SplunkMCPClient(
        host=settings.SPLUNK_HOST,
        port=settings.SPLUNK_PORT,
        token=settings.SPLUNK_TOKEN,
        mcp_endpoint=settings.SPLUNK_MCP_ENDPOINT,
        demo_mode=settings.DEMO_MODE,
    )
    models_client = HostedModelsClient(
        foundation_sec_endpoint=settings.FOUNDATION_SEC_ENDPOINT,
        cisco_dtsm_endpoint=settings.CISCO_DTSM_ENDPOINT,
        demo_mode=settings.DEMO_MODE,
    )
    orchestrator = OrchestratorAgent(
        mcp_client=mcp_client,
        models_client=models_client,
        demo_mode=settings.DEMO_MODE,
    )

    logger.info("🛡️ SplunkSentinel initialized — all agents online (demo_mode=%s)", settings.DEMO_MODE)
    yield
    logger.info("🛡️ SplunkSentinel shutting down")


app = FastAPI(
    title="SplunkSentinel",
    description="AI-Powered Autonomous SOC Analyst",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check with agent status."""
    return {
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": orchestrator.get_agent_status() if orchestrator else {},
        "splunk_connected": mcp_client.is_connected() if mcp_client else False,
        "demo_mode": settings.DEMO_MODE,
    }


@app.post("/api/investigate")
async def investigate_alert(request: InvestigationRequest):
    """Trigger a full AI investigation on a specific alert or event."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    result = await orchestrator.investigate(
        alert_id=request.alert_id,
        context=request.context,
        depth=request.depth,
    )
    return result


@app.get("/api/alerts/triage")
async def get_triaged_alerts(limit: int = 50):
    """Get AI-triaged and prioritized alerts."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    alerts = await orchestrator.triage_alerts(limit=limit)
    return {"alerts": alerts, "total": len(alerts)}


@app.get("/api/forecast")
async def get_anomaly_forecast(metric: str = "network_traffic", hours: int = 24):
    """Get anomaly forecasting from Cisco Deep Time Series Model."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    forecast = await orchestrator.forecast_anomalies(metric=metric, forecast_hours=hours)
    return forecast


@app.get("/api/timeline/{alert_id}")
async def get_attack_timeline(alert_id: str):
    """Reconstruct the attack timeline for an alert."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    timeline = await orchestrator.build_timeline(alert_id)
    return timeline


@app.post("/api/response/{alert_id}")
async def get_response_actions(alert_id: str):
    """Get AI-recommended response actions for an alert."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    actions = await orchestrator.recommend_responses(alert_id)
    return actions


@app.get("/api/report/executive")
async def generate_executive_report():
    """Generate an AI-powered executive security summary."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    report = await ReportGenerator(orchestrator).generate_executive_summary()
    return report


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket for real-time alert streaming."""
    await websocket.accept()
    try:
        while True:
            alerts = await orchestrator.get_latest_alerts()
            await websocket.send_json({
                "type": "alert_update",
                "data": alerts,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


@app.websocket("/ws/investigation/{alert_id}")
async def websocket_investigation(websocket: WebSocket, alert_id: str):
    """WebSocket for real-time investigation progress streaming."""
    await websocket.accept()
    try:
        async for update in orchestrator.stream_investigation(alert_id):
            await websocket.send_json(update)
    except WebSocketDisconnect:
        logger.info("Investigation WebSocket disconnected")
