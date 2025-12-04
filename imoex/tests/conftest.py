"""
Pytest configuration and fixtures
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.dependencies import get_db


# Test database URL (использует тестовую БД)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/trading", "/trading_test")


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def test_session_factory(test_engine):
    """Create test session factory"""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture
async def db_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_session_factory() as session:
        yield session


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """Create test client with overridden dependencies"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
