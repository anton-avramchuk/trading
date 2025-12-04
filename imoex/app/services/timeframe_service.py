"""
Service for working with timeframes
"""
from typing import List

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timeframe import Timeframe
from app.schemas.timeframe import TimeframeResponse


class TimeframeService:
    """Service for timeframe operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, active_only: bool = True) -> List[TimeframeResponse]:
        """
        Get all timeframes

        Args:
            active_only: Return only active timeframes

        Returns:
            List of timeframes
        """
        logger.debug(f"Fetching timeframes (active_only={active_only})")

        query = select(Timeframe).order_by(Timeframe.minutes)

        if active_only:
            query = query.where(Timeframe.is_active == 1)

        result = await self.db.execute(query)
        timeframes = result.scalars().all()

        logger.info(f"Found {len(timeframes)} timeframes")
        return [TimeframeResponse.model_validate(tf) for tf in timeframes]

    async def get_by_code(self, code: str) -> TimeframeResponse | None:
        """
        Get timeframe by code

        Args:
            code: Timeframe code (e.g., "1h", "1d")

        Returns:
            Timeframe or None
        """
        logger.debug(f"Fetching timeframe by code: {code}")

        result = await self.db.execute(
            select(Timeframe).where(Timeframe.code == code)
        )
        timeframe = result.scalar_one_or_none()

        if not timeframe:
            logger.warning(f"Timeframe not found: {code}")
            return None

        return TimeframeResponse.model_validate(timeframe)

    async def validate_timeframe(self, code: str) -> bool:
        """
        Validate if timeframe exists and is active

        Args:
            code: Timeframe code

        Returns:
            True if valid, False otherwise
        """
        result = await self.db.execute(
            select(Timeframe).where(
                Timeframe.code == code, Timeframe.is_active == 1
            )
        )
        timeframe = result.scalar_one_or_none()
        return timeframe is not None
