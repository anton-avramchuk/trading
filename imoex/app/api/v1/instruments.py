"""
Instruments API endpoints
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.instrument import InstrumentResponse, InstrumentListResponse
from app.services.instrument_service import InstrumentService

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("", response_model=InstrumentListResponse)
async def get_instruments(
    market: Optional[str] = Query(None, description="Filter by market"),
    instrument_type: Optional[str] = Query(None, description="Filter by type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all instruments with optional filters

    Returns:
        List of instruments with total count
    """
    service = InstrumentService(db)
    return await service.get_all(
        market=market, instrument_type=instrument_type, skip=skip, limit=limit
    )


@router.get("/{ticker}", response_model=InstrumentResponse)
async def get_instrument_by_ticker(ticker: str, db: AsyncSession = Depends(get_db)):
    """
    Get instrument by ticker

    Args:
        ticker: Instrument ticker (e.g., GAZP, SBER)

    Returns:
        Instrument details
    """
    service = InstrumentService(db)
    instrument = await service.get_by_ticker(ticker.upper())

    if not instrument:
        raise HTTPException(
            status_code=404, detail=f"Instrument '{ticker}' not found"
        )

    return instrument
