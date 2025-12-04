"""
Download data API endpoints
"""
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.moex_client import MOEXClient
from app.dependencies import get_db
from app.models.download_log import DownloadLog
from app.schemas.download import (
    DownloadRequest,
    DownloadResponse,
    DownloadLogResponse,
    DownloadStatsResponse,
)
from app.services.data_downloader import DataDownloader

router = APIRouter(prefix="/download", tags=["download"])


async def get_moex_client(db: AsyncSession = Depends(get_db)) -> MOEXClient:
    """Get initialized MOEX client"""
    client = MOEXClient(db)
    await client.initialize()
    return client


@router.post("", response_model=DownloadResponse)
async def download_data(
    request: DownloadRequest,
    db: AsyncSession = Depends(get_db),
    moex_client: MOEXClient = Depends(get_moex_client),
):
    """
    Download OHLCV data from MOEX

    This endpoint validates the timeframe against the database before downloading.
    Only timeframes that exist in the timeframes table can be used.

    Args:
        request: Download request with ticker, timeframe, market, etc.

    Returns:
        Download result with status and statistics
    """
    logger.info(f"Download request: {request.ticker} {request.timeframe}")

    downloader = DataDownloader(db, moex_client)
    result = await downloader.download(request)

    return result


@router.post("/background", response_model=dict)
async def download_data_background(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    moex_client: MOEXClient = Depends(get_moex_client),
):
    """
    Download OHLCV data from MOEX in background

    Returns immediately with task ID, actual download runs in background.

    Args:
        request: Download request
        background_tasks: FastAPI background tasks

    Returns:
        Task information
    """
    logger.info(f"Background download request: {request.ticker} {request.timeframe}")

    # Add task to background
    downloader = DataDownloader(db, moex_client)
    background_tasks.add_task(downloader.download, request)

    return {
        "status": "accepted",
        "message": "Download task started in background",
        "ticker": request.ticker,
        "timeframe": request.timeframe,
    }


@router.get("/logs", response_model=List[DownloadLogResponse])
async def get_download_logs(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    timeframe: Optional[str] = Query(None, description="Filter by timeframe"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=500, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get download logs with optional filters

    Args:
        ticker: Filter by ticker
        timeframe: Filter by timeframe
        status: Filter by status (pending, running, completed, failed)
        limit: Maximum number of records

    Returns:
        List of download logs
    """
    query = select(DownloadLog).order_by(DownloadLog.started_at.desc())

    if ticker:
        query = query.where(DownloadLog.ticker == ticker.upper())
    if timeframe:
        query = query.where(DownloadLog.timeframe == timeframe)
    if status:
        query = query.where(DownloadLog.status == status)

    query = query.limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [DownloadLogResponse.model_validate(log) for log in logs]


@router.get("/logs/{log_id}", response_model=DownloadLogResponse)
async def get_download_log(log_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get specific download log by ID

    Args:
        log_id: Download log ID

    Returns:
        Download log details
    """
    result = await db.execute(select(DownloadLog).where(DownloadLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail=f"Download log {log_id} not found")

    return DownloadLogResponse.model_validate(log)


@router.get("/stats", response_model=DownloadStatsResponse)
async def get_download_stats(db: AsyncSession = Depends(get_db)):
    """
    Get download statistics

    Returns:
        Overall download statistics
    """
    # Total downloads
    total_result = await db.execute(select(func.count(DownloadLog.id)))
    total_downloads = total_result.scalar() or 0

    # Successful downloads
    success_result = await db.execute(
        select(func.count(DownloadLog.id)).where(DownloadLog.status == "completed")
    )
    successful_downloads = success_result.scalar() or 0

    # Failed downloads
    failed_result = await db.execute(
        select(func.count(DownloadLog.id)).where(DownloadLog.status == "failed")
    )
    failed_downloads = failed_result.scalar() or 0

    # Total records
    records_result = await db.execute(
        select(func.sum(DownloadLog.records_imported)).where(
            DownloadLog.status == "completed"
        )
    )
    total_records = records_result.scalar() or 0

    # Average duration
    duration_result = await db.execute(
        select(func.avg(DownloadLog.duration_seconds)).where(
            DownloadLog.status == "completed"
        )
    )
    average_duration = duration_result.scalar()

    # Last download
    last_result = await db.execute(
        select(DownloadLog.started_at)
        .order_by(DownloadLog.started_at.desc())
        .limit(1)
    )
    last_download = last_result.scalar_one_or_none()

    return DownloadStatsResponse(
        total_downloads=total_downloads,
        successful_downloads=successful_downloads,
        failed_downloads=failed_downloads,
        total_records=total_records,
        average_duration=average_duration,
        last_download=last_download,
    )
