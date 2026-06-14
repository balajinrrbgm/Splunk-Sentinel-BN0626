"""Alert data models for SplunkSentinel."""
from pydantic import BaseModel, Field
from typing import Optional


class InvestigationRequest(BaseModel):
    """Request model for triggering an investigation."""

    alert_id: str = Field(..., description="The alert ID to investigate")
    context: str = Field(default="", description="Additional context for the investigation")
    depth: str = Field(default="full", description="Investigation depth: quick, standard, or full")


class AlertBatch(BaseModel):
    """Batch of alerts for processing."""

    alerts: list[dict] = Field(default_factory=list)
    source: str = Field(default="splunk")
    timestamp: Optional[str] = None
