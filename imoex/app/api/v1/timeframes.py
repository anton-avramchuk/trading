"""
Timeframes API endpoints
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.timeframe import TimeframeResponse
from app.services.timeframe_service import TimeframeService

router = APIRouter(prefix="/timeframes", tags=["timeframes"])


@router.get("", response_model=List[TimeframeResponse])
async def get_timeframes(
    active_only: bool = True, db: AsyncSession = Depends(get_db)
):
    """
    Get all available timeframes

    Args:
        active_only: Return only active timeframes

    Returns:
        List of timeframes
    """
    service = TimeframeService(db)
    return await service.get_all(active_only=active_only)


@router.get("/{code}", response_model=TimeframeResponse)
async def get_timeframe_by_code(code: str, db: AsyncSession = Depends(get_db)):
    """
    Get timeframe by code

    Args:
        code: Timeframe code (e.g., "1h", "1d")

    Returns:
        Timeframe details
    """
    service = TimeframeService(db)
    timeframe = await service.get_by_code(code)

    if not timeframe:
        raise HTTPException(status_code=404, detail=f"Timeframe '{code}' not found")

    return timeframe
