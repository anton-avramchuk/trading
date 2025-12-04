"""
Tests for MOEX ISS API client
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.moex_client import MOEXClient
from app.models.timeframe import Timeframe


@pytest.fixture
async def moex_client(db_session: AsyncSession):
    """Create MOEX client with mock database"""
    # Create mock timeframes in database
    timeframes = [
        Timeframe(
            id=1,
            code="1h",
            name="1 час",
            minutes=60,
            moex_interval=60,
            is_active=1,
        ),
        Timeframe(
            id=2,
            code="1d",
            name="1 день",
            minutes=1440,
            moex_interval=24,
            is_active=1,
        ),
    ]

    # Mock database query
    db_session.execute = AsyncMock()
    db_session.execute.return_value.scalars.return_value.all.return_value = timeframes

    client = MOEXClient(db_session)
    await client.initialize()

    return client


@pytest.mark.asyncio
async def test_moex_client_initialization(moex_client: MOEXClient):
    """Test MOEX client initialization loads timeframes"""
    assert len(moex_client._valid_timeframes) == 2
    assert "1h" in moex_client._valid_timeframes
    assert "1d" in moex_client._valid_timeframes
    assert moex_client._valid_timeframes["1h"] == 60
    assert moex_client._valid_timeframes["1d"] == 24


@pytest.mark.asyncio
async def test_validate_timeframe_valid(moex_client: MOEXClient):
    """Test validating a valid timeframe"""
    # Should not raise exception
    moex_client.validate_timeframe("1h")
    moex_client.validate_timeframe("1d")


@pytest.mark.asyncio
async def test_validate_timeframe_invalid(moex_client: MOEXClient):
    """Test validating an invalid timeframe"""
    with pytest.raises(ValueError) as exc_info:
        moex_client.validate_timeframe("5m")

    assert "Invalid timeframe '5m'" in str(exc_info.value)
    assert "1d, 1h" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_moex_interval(moex_client: MOEXClient):
    """Test getting MOEX interval for timeframe"""
    assert moex_client.get_moex_interval("1h") == 60
    assert moex_client.get_moex_interval("1d") == 24


@pytest.mark.asyncio
async def test_get_timeframe_id(moex_client: MOEXClient):
    """Test getting timeframe ID"""
    assert moex_client.get_timeframe_id("1h") == 1
    assert moex_client.get_timeframe_id("1d") == 2


@pytest.mark.asyncio
async def test_get_moex_interval_invalid(moex_client: MOEXClient):
    """Test getting MOEX interval for invalid timeframe"""
    with pytest.raises(ValueError):
        moex_client.get_moex_interval("5m")
