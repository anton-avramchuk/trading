"""
Pydantic schemas for download operations
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class DownloadRequest(BaseModel):
    """Request schema for downloading MOEX data"""

    ticker: str = Field(..., description="Instrument ticker (e.g., GAZP, SBER)")
    timeframe: str = Field(..., description="Timeframe code (1m, 10m, 1h, 1d, etc.)")
    market: str = Field(default="stock", description="MOEX market (stock, futures)")
    board: str = Field(default="TQBR", description="MOEX board (TQBR, RFUD, etc.)")
    start_date: datetime | None = Field(None, description="Start date for download")
    end_date: datetime | None = Field(None, description="End date for download")
    days_back: int | None = Field(None, description="Number of days to download (if start_date not provided)")

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        """Validate timeframe format"""
        valid_timeframes = {"1m", "10m", "1h", "1d", "1w", "1M", "1Q"}
        if v not in valid_timeframes:
            raise ValueError(f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}")
        return v

    @field_validator("market")
    @classmethod
    def validate_market(cls, v: str) -> str:
        """Validate market"""
        valid_markets = {"stock", "futures"}
        if v not in valid_markets:
            raise ValueError(f"Invalid market. Must be one of: {', '.join(valid_markets)}")
        return v


class DownloadResponse(BaseModel):
    """Response schema for download operation"""

    success: bool
    message: str
    log_id: int | None = Field(None, description="Download log ID")
    ticker: str
    timeframe: str
    records_imported: int = Field(default=0, description="Number of records imported")
    duration_seconds: float | None = Field(None, description="Duration in seconds")
    error: str | None = Field(None, description="Error message if failed")


class DownloadLogResponse(BaseModel):
    """Response schema for download log"""

    id: int
    instrument_id: int | None
    timeframe_id: int | None
    ticker: str
    timeframe: str
    market: str
    board: str
    status: str = Field(..., description="Status (pending, running, completed, failed)")
    records_imported: int
    start_date: datetime | None
    end_date: datetime | None
    started_at: datetime
    completed_at: datetime | None
    duration_seconds: float | None
    error: str | None
    metadata: dict | None
    created_at: datetime

    class Config:
        from_attributes = True


class DownloadStatsResponse(BaseModel):
    """Response schema for download statistics"""

    total_downloads: int
    successful_downloads: int
    failed_downloads: int
    total_records: int
    average_duration: float | None
    last_download: datetime | None
