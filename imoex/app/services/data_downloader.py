"""
Service for downloading data from MOEX
"""
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.moex_client import MOEXClient
from app.models.download_log import DownloadLog
from app.models.ohlcv import OHLCV
from app.schemas.download import DownloadRequest, DownloadResponse
from app.services.instrument_service import InstrumentService
from app.services.timeframe_service import TimeframeService


class DataDownloader:
    """Service for downloading MOEX data"""

    def __init__(self, db: AsyncSession, moex_client: MOEXClient):
        self.db = db
        self.moex_client = moex_client
        self.instrument_service = InstrumentService(db)
        self.timeframe_service = TimeframeService(db)

    async def download(self, request: DownloadRequest) -> DownloadResponse:
        """
        Download data from MOEX and save to database

        Args:
            request: Download request

        Returns:
            Download response
        """
        ticker = request.ticker.upper()
        timeframe = request.timeframe
        market = request.market
        board = request.board

        logger.info(f"Starting download: {ticker} {timeframe} from MOEX")

        # Validate timeframe
        if not await self.timeframe_service.validate_timeframe(timeframe):
            error_msg = f"Invalid timeframe: {timeframe}"
            logger.error(error_msg)
            return DownloadResponse(
                success=False,
                message=error_msg,
                ticker=ticker,
                timeframe=timeframe,
                error=error_msg,
            )

        # Get timeframe ID
        timeframe_obj = await self.timeframe_service.get_by_code(timeframe)
        if not timeframe_obj:
            error_msg = f"Timeframe not found: {timeframe}"
            logger.error(error_msg)
            return DownloadResponse(
                success=False,
                message=error_msg,
                ticker=ticker,
                timeframe=timeframe,
                error=error_msg,
            )

        # Get or create instrument
        try:
            # First, try to get security info from MOEX
            security_info = await self.moex_client.get_security_info(
                ticker, market, board
            )

            if security_info:
                name = security_info.get("SHORTNAME", ticker)
            else:
                name = ticker

            instrument = await self.instrument_service.get_or_create(
                ticker=ticker,
                name=name,
                market=market.upper(),
                instrument_type="stock" if market == "stock" else "future",
            )
        except Exception as e:
            error_msg = f"Failed to get/create instrument: {e}"
            logger.error(error_msg)
            return DownloadResponse(
                success=False,
                message=error_msg,
                ticker=ticker,
                timeframe=timeframe,
                error=error_msg,
            )

        # Create download log
        download_log = DownloadLog(
            instrument_id=instrument.id,
            timeframe_id=timeframe_obj.id,
            ticker=ticker,
            timeframe=timeframe,
            market=market,
            board=board,
            status="running",
            started_at=datetime.utcnow(),
        )

        # Determine date range
        start_date = request.start_date
        end_date = request.end_date or datetime.utcnow()

        if not start_date and request.days_back:
            start_date = datetime.utcnow() - timedelta(days=request.days_back)

        download_log.start_date = start_date
        download_log.end_date = end_date

        self.db.add(download_log)
        await self.db.commit()
        await self.db.refresh(download_log)

        # Download data from MOEX
        try:
            logger.info(f"Downloading data from MOEX: {ticker} {timeframe}")
            df = await self.moex_client.get_candles(
                ticker=ticker,
                timeframe=timeframe,
                market=market,
                board=board,
                start_date=start_date,
                end_date=end_date,
            )

            if df.empty:
                download_log.status = "completed"
                download_log.records_imported = 0
                download_log.completed_at = datetime.utcnow()
                download_log.duration_seconds = (
                    download_log.completed_at - download_log.started_at
                ).total_seconds()

                await self.db.commit()

                return DownloadResponse(
                    success=True,
                    message="No data found for the specified period",
                    log_id=download_log.id,
                    ticker=ticker,
                    timeframe=timeframe,
                    records_imported=0,
                    duration_seconds=download_log.duration_seconds,
                )

            # Save to database
            records_imported = await self._save_ohlcv_data(
                df, instrument.id, timeframe_obj.id, timeframe
            )

            # Update download log
            download_log.status = "completed"
            download_log.records_imported = records_imported
            download_log.completed_at = datetime.utcnow()
            download_log.duration_seconds = (
                download_log.completed_at - download_log.started_at
            ).total_seconds()
            download_log.metadata = {
                "total_rows": len(df),
                "duplicates_skipped": len(df) - records_imported,
            }

            await self.db.commit()

            logger.info(
                f"Download completed: {ticker} {timeframe}, "
                f"imported {records_imported} records in {download_log.duration_seconds:.2f}s"
            )

            return DownloadResponse(
                success=True,
                message=f"Successfully downloaded {records_imported} records",
                log_id=download_log.id,
                ticker=ticker,
                timeframe=timeframe,
                records_imported=records_imported,
                duration_seconds=download_log.duration_seconds,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Download failed: {error_msg}")

            download_log.status = "failed"
            download_log.error = error_msg
            download_log.completed_at = datetime.utcnow()
            download_log.duration_seconds = (
                download_log.completed_at - download_log.started_at
            ).total_seconds()

            await self.db.commit()

            return DownloadResponse(
                success=False,
                message=f"Download failed: {error_msg}",
                log_id=download_log.id,
                ticker=ticker,
                timeframe=timeframe,
                records_imported=0,
                duration_seconds=download_log.duration_seconds,
                error=error_msg,
            )

    async def _save_ohlcv_data(
        self, df: pd.DataFrame, instrument_id: int, timeframe_id: int, timeframe: str
    ) -> int:
        """
        Save OHLCV data to database

        Args:
            df: DataFrame with OHLCV data
            instrument_id: Instrument ID
            timeframe_id: Timeframe ID
            timeframe: Timeframe code

        Returns:
            Number of records saved
        """
        logger.debug(f"Saving {len(df)} OHLCV records to database")

        # Validate OHLC data
        df = df[
            (df["high"] >= df["open"])
            & (df["high"] >= df["close"])
            & (df["low"] <= df["open"])
            & (df["low"] <= df["close"])
        ]

        # Convert to list of dicts
        records = df.to_dict(orient="records")

        # Insert with ON CONFLICT DO NOTHING (skip duplicates)
        saved_count = 0
        for record in records:
            try:
                ohlcv = OHLCV(
                    instrument_id=instrument_id,
                    timeframe_id=timeframe_id,
                    timeframe=timeframe,
                    timestamp=record["timestamp"],
                    open=float(record["open"]),
                    high=float(record["high"]),
                    low=float(record["low"]),
                    close=float(record["close"]),
                    volume=int(record["volume"]),
                )
                self.db.add(ohlcv)
                saved_count += 1
            except Exception as e:
                logger.debug(f"Skipping duplicate or invalid record: {e}")
                continue

        await self.db.commit()

        logger.debug(f"Saved {saved_count} records (skipped {len(records) - saved_count} duplicates)")
        return saved_count
