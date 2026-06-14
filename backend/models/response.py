"""Response action data models."""
from pydantic import BaseModel, Field
from typing import Optional


class ResponseAction(BaseModel):
    """A single response action recommendation."""

    action: str
    priority: int
    description: str
    category: str = "immediate"  # immediate, short_term, long_term
    spl: Optional[str] = None
    automated: bool = False
    timeframe: Optional[str] = None
