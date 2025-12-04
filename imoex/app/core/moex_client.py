"""
MOEX ISS API Client with timeframe validation

This client validates all timeframe requests against the database timeframes table
to ensure only valid timeframes are used for data downloads.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import pandas as pd
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


class MOEXClient:
    """MOEX ISS API client with timeframe validation"""

    def __init__(self, session: AsyncSession):
        """
        Initialize MOEX client

        Args:
            session: Database session for timeframe validation
        """
        self.base_url = settings.MOEX_BASE_URL
        self.timeout = aiohttp.ClientTimeout(total=settings.MOEX_TIMEOUT)
        self.max_retries = settings.MOEX_MAX_RETRIES
        self.rate_limit = settings.MOEX_RATE_LIMIT
        self._last_request_time = 0.0
        self._db_session = session
        self._valid_timeframes: Dict[str, int] = {}  # code -> moex_interval
        self._timeframe_ids: Dict[str, int] = {}  # code -> id

    async def initialize(self) -> None:
        """Load valid timeframes from database"""
        from app.models.timeframe import Timeframe

        logger.info("Loading valid timeframes from database...")

        result = await self._db_session.execute(
            select(Timeframe).where(Timeframe.is_active == 1)
        )
        timeframes = result.scalars().all()

        self._valid_timeframes = {tf.code: tf.moex_interval for tf in timeframes}
        self._timeframe_ids = {tf.code: tf.id for tf in timeframes}

        logger.info(f"Loaded {len(self._valid_timeframes)} valid timeframes: {list(self._valid_timeframes.keys())}")

    def validate_timeframe(self, timeframe: str) -> None:
        """
        Validate timeframe against database

        Args:
            timeframe: Timeframe code to validate

        Raises:
            ValueError: If timeframe is not valid
        """
        if not self._valid_timeframes:
            raise RuntimeError("MOEXClient not initialized. Call initialize() first.")

        if timeframe not in self._valid_timeframes:
            valid_codes = ", ".join(sorted(self._valid_timeframes.keys()))
            raise ValueError(
                f"Invalid timeframe '{timeframe}'. "
                f"Valid timeframes from database: {valid_codes}"
            )

    def get_moex_interval(self, timeframe: str) -> int:
        """
        Get MOEX interval for timeframe

        Args:
            timeframe: Timeframe code

        Returns:
            MOEX interval value

        Raises:
            ValueError: If timeframe is not valid
        """
        self.validate_timeframe(timeframe)
        return self._valid_timeframes[timeframe]

    def get_timeframe_id(self, timeframe: str) -> int:
        """
        Get timeframe ID for timeframe code

        Args:
            timeframe: Timeframe code

        Returns:
            Timeframe ID

        Raises:
            ValueError: If timeframe is not valid
        """
        self.validate_timeframe(timeframe)
        return self._timeframe_ids[timeframe]

    async def _rate_limit(self) -> None:
        """Enforce rate limiting"""
        if self.rate_limit <= 0:
            return

        now = asyncio.get_event_loop().time()
        time_since_last = now - self._last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)

        self._last_request_time = asyncio.get_event_loop().time()

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to MOEX ISS API

        Args:
            endpoint: API endpoint
            params: Query parameters
            retry_count: Current retry attempt

        Returns:
            JSON response

        Raises:
            aiohttp.ClientError: If request fails after retries
        """
        await self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["iss.json"] = "extended"  # Use extended JSON format
        params["iss.meta"] = "off"  # Disable metadata

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if retry_count < self.max_retries:
                logger.warning(
                    f"Request failed (attempt {retry_count + 1}/{self.max_retries}): {e}"
                )
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._request(endpoint, params, retry_count + 1)
            else:
                logger.error(f"Request failed after {self.max_retries} retries: {e}")
                raise

    async def get_candles(
        self,
        ticker: str,
        timeframe: str,
        market: str = "stock",
        board: str = "TQBR",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Download OHLCV candles from MOEX

        Args:
            ticker: Instrument ticker
            timeframe: Timeframe code (validated against database)
            market: Market type (stock, futures)
            board: Board code
            start_date: Start date for data
            end_date: End date for data

        Returns:
            DataFrame with OHLCV data

        Raises:
            ValueError: If timeframe is invalid
        """
        # Validate timeframe against database
        self.validate_timeframe(timeframe)
        moex_interval = self.get_moex_interval(timeframe)

        logger.info(
            f"Downloading {ticker} {timeframe} data from MOEX "
            f"(market={market}, board={board}, interval={moex_interval})"
        )

        # Determine market path
        if market == "stock":
            market_path = "engines/stock/markets/shares"
        elif market == "futures":
            market_path = "engines/futures/markets/forts"
        else:
            raise ValueError(f"Unsupported market: {market}")

        # Build endpoint
        endpoint = f"/{market_path}/boards/{board}/securities/{ticker}/candles.json"

        # Prepare parameters
        params = {"interval": moex_interval}

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["till"] = end_date.strftime("%Y-%m-%d")

        # Fetch data with pagination
        all_candles = []
        start = 0
        limit = 500  # MOEX returns max 500 candles per request

        while True:
            params["start"] = start

            try:
                data = await self._request(endpoint, params)

                # Extract candles from response
                # Response format: [1, [columns], [row1], [row2], ...]
                if not data or len(data) < 3:
                    break

                columns = data[1]
                rows = data[2:]

                if not rows:
                    break

                # Create DataFrame
                df_page = pd.DataFrame(rows, columns=columns)
                all_candles.append(df_page)

                logger.debug(f"Fetched {len(df_page)} candles (start={start})")

                # Check if we got less than limit (last page)
                if len(df_page) < limit:
                    break

                start += limit

            except Exception as e:
                logger.error(f"Error fetching candles for {ticker}: {e}")
                raise

        if not all_candles:
            logger.warning(f"No data found for {ticker} {timeframe}")
            return pd.DataFrame()

        # Combine all pages
        df = pd.concat(all_candles, ignore_index=True)

        # Rename columns to match our schema
        df = df.rename(
            columns={
                "begin": "timestamp",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume",
            }
        )

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Select only required columns
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]

        # Sort by timestamp
        df = df.sort_values("timestamp")

        # Remove duplicates
        df = df.drop_duplicates(subset=["timestamp"], keep="last")

        logger.info(f"Downloaded {len(df)} candles for {ticker} {timeframe}")

        return df

    async def search_securities(
        self, query: str, market: str = "stock"
    ) -> List[Dict[str, Any]]:
        """
        Search for securities on MOEX

        Args:
            query: Search query (ticker or name)
            market: Market type

        Returns:
            List of found securities
        """
        logger.info(f"Searching securities: {query}")

        endpoint = "/securities.json"
        params = {"q": query}

        try:
            data = await self._request(endpoint, params)

            # Parse response
            if not data or len(data) < 3:
                return []

            columns = data[1]
            rows = data[2:]

            results = []
            for row in rows:
                security = dict(zip(columns, row))
                results.append(security)

            logger.info(f"Found {len(results)} securities")
            return results

        except Exception as e:
            logger.error(f"Error searching securities: {e}")
            return []

    async def get_security_info(
        self, ticker: str, market: str = "stock", board: str = "TQBR"
    ) -> Optional[Dict[str, Any]]:
        """
        Get security information

        Args:
            ticker: Security ticker
            market: Market type
            board: Board code

        Returns:
            Security information or None
        """
        logger.info(f"Getting info for {ticker}")

        if market == "stock":
            market_path = "engines/stock/markets/shares"
        elif market == "futures":
            market_path = "engines/futures/markets/forts"
        else:
            raise ValueError(f"Unsupported market: {market}")

        endpoint = f"/{market_path}/boards/{board}/securities/{ticker}.json"

        try:
            data = await self._request(endpoint)

            if not data or len(data) < 3:
                return None

            columns = data[1]
            rows = data[2:]

            if not rows:
                return None

            security = dict(zip(columns, rows[0]))
            return security

        except Exception as e:
            logger.error(f"Error getting security info for {ticker}: {e}")
            return None
