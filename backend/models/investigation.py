"""Investigation result data models."""
from pydantic import BaseModel, Field
from typing import Optional


class InvestigationResult(BaseModel):
    """Result of an AI investigation."""

    alert_id: str
    status: str = "complete"
    findings_summary: str = ""
    confidence_score: int = 0
    attack_pattern: str = ""
    affected_assets: list[str] = Field(default_factory=list)
    mitre_techniques: list[dict] = Field(default_factory=list)
    evidence_count: int = 0
    spl_queries_used: list[str] = Field(default_factory=list)
