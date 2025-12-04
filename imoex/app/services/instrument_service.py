"""
Service for working with instruments
"""
from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentResponse, InstrumentListResponse


class InstrumentService:
    """Service for instrument operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        market: Optional[str] = None,
        instrument_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> InstrumentListResponse:
        """
        Get all instruments with optional filters

        Args:
            market: Filter by market
            instrument_type: Filter by instrument type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of instruments with count
        """
        logger.debug(
            f"Fetching instruments (market={market}, type={instrument_type}, skip={skip}, limit={limit})"
        )

        query = select(Instrument).order_by(Instrument.ticker)

        if market:
            query = query.where(Instrument.market == market)
        if instrument_type:
            query = query.where(Instrument.instrument_type == instrument_type)

        # Get total count
        count_result = await self.db.execute(query)
        total_count = len(count_result.scalars().all())

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        instruments = result.scalars().all()

        logger.info(f"Found {len(instruments)} instruments (total: {total_count})")

        return InstrumentListResponse(
            items=[InstrumentResponse.model_validate(inst) for inst in instruments],
            count=total_count,
        )

    async def get_by_ticker(self, ticker: str) -> InstrumentResponse | None:
        """
        Get instrument by ticker

        Args:
            ticker: Instrument ticker

        Returns:
            Instrument or None
        """
        logger.debug(f"Fetching instrument by ticker: {ticker}")

        result = await self.db.execute(
            select(Instrument).where(Instrument.ticker == ticker)
        )
        instrument = result.scalar_one_or_none()

        if not instrument:
            logger.warning(f"Instrument not found: {ticker}")
            return None

        return InstrumentResponse.model_validate(instrument)

    async def get_by_id(self, instrument_id: int) -> InstrumentResponse | None:
        """
        Get instrument by ID

        Args:
            instrument_id: Instrument ID

        Returns:
            Instrument or None
        """
        logger.debug(f"Fetching instrument by ID: {instrument_id}")

        result = await self.db.execute(
            select(Instrument).where(Instrument.id == instrument_id)
        )
        instrument = result.scalar_one_or_none()

        if not instrument:
            logger.warning(f"Instrument not found: {instrument_id}")
            return None

        return InstrumentResponse.model_validate(instrument)

    async def get_or_create(
        self,
        ticker: str,
        name: str,
        market: str,
        instrument_type: str,
        index_id: Optional[int] = None,
    ) -> InstrumentResponse:
        """
        Get existing instrument or create new one

        Args:
            ticker: Instrument ticker
            name: Instrument name
            market: Market
            instrument_type: Instrument type
            index_id: Optional index ID

        Returns:
            Instrument
        """
        logger.debug(f"Get or create instrument: {ticker}")

        # Try to get existing
        existing = await self.get_by_ticker(ticker)
        if existing:
            logger.debug(f"Found existing instrument: {ticker}")
            return existing

        # Create new
        logger.info(f"Creating new instrument: {ticker}")
        instrument = Instrument(
            ticker=ticker,
            name=name,
            market=market,
            instrument_type=instrument_type,
            index_id=index_id,
        )

        self.db.add(instrument)
        await self.db.commit()
        await self.db.refresh(instrument)

        return InstrumentResponse.model_validate(instrument)
