"""
Tests for Pydantic schemas
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.download import DownloadRequest


def test_download_request_valid():
    """Test valid download request"""
    request = DownloadRequest(
        ticker="GAZP",
        timeframe="1h",
        market="stock",
        board="TQBR",
        days_back=30,
    )

    assert request.ticker == "GAZP"
    assert request.timeframe == "1h"
    assert request.market == "stock"
    assert request.board == "TQBR"
    assert request.days_back == 30


def test_download_request_invalid_timeframe():
    """Test download request with invalid timeframe"""
    with pytest.raises(ValidationError) as exc_info:
        DownloadRequest(
            ticker="GAZP",
            timeframe="5m",  # Invalid
            market="stock",
            board="TQBR",
        )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "timeframe" in errors[0]["loc"]


def test_download_request_invalid_market():
    """Test download request with invalid market"""
    with pytest.raises(ValidationError) as exc_info:
        DownloadRequest(
            ticker="GAZP",
            timeframe="1h",
            market="invalid",  # Invalid
            board="TQBR",
        )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "market" in errors[0]["loc"]


def test_download_request_defaults():
    """Test download request with default values"""
    request = DownloadRequest(
        ticker="SBER",
        timeframe="1d",
    )

    assert request.market == "stock"
    assert request.board == "TQBR"
    assert request.start_date is None
    assert request.end_date is None
    assert request.days_back is None
