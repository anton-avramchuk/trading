"""
Pydantic schemas for instrument
"""
from datetime import datetime
from pydantic import BaseModel, Field


class InstrumentResponse(BaseModel):
    """Response schema for instrument"""

    id: int
    ticker: str = Field(..., description="Instrument ticker")
    name: str = Field(..., description="Instrument name")
    market: str = Field(..., description="Market (MOEX, CME, etc.)")
    instrument_type: str = Field(..., description="Instrument type (stock, future, index)")
    index_id: int | None = Field(None, description="Related index ID")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InstrumentListResponse(BaseModel):
    """Response schema for list of instruments"""

    items: list[InstrumentResponse]
    count: int
