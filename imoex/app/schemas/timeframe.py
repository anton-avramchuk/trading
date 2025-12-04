"""
Pydantic schemas for timeframe
"""
from datetime import datetime
from pydantic import BaseModel, Field


class TimeframeResponse(BaseModel):
    """Response schema for timeframe"""

    id: int
    code: str = Field(..., description="Timeframe code (1m, 10m, 1h, 1d, etc.)")
    name: str = Field(..., description="Timeframe name")
    description: str | None = Field(None, description="Timeframe description")
    minutes: int = Field(..., description="Number of minutes")
    moex_interval: int = Field(..., description="MOEX ISS API interval value")
    is_active: int = Field(..., description="Active status (1=active, 0=inactive)")
    created_at: datetime

    class Config:
        from_attributes = True
