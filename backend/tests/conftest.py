"""
Общие фикстуры для тестов
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.database import Base
from app.api.deps import get_db

# Тестовая база данных (SQLite in-memory)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """
    Создание тестового engine для каждого теста
    """
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Критично для SQLite in-memory: все соединения используют одну БД
        echo=False
    )

    # Импортируем все модели для правильной регистрации
    from app.models.index import Index
    from app.models.instrument import Instrument
    from app.models.ohlcv import OHLCV
    from app.models.signal import Signal
    from app.models.strategy import Strategy
    from app.models.currency import Currency
    from app.models.country import Country
    from app.models.timeframe import Timeframe
    from app.models.backtest import Backtest
    from app.models.download_log import DownloadLog

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """
    Создание тестовой сессии БД для каждого теста
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(test_db):
    """
    Создание тестового клиента FastAPI с тестовой БД
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_index(test_db):
    """
    Создание тестового индекса
    """
    from app.models.index import Index

    index = Index(
        name="Test Index",
        ticker="TESTIDX",
        description="Test Index Description"
    )
    test_db.add(index)
    test_db.commit()
    test_db.refresh(index)
    return index


@pytest.fixture(scope="function")
def sample_instrument(test_db, sample_index):
    """
    Создание тестового инструмента
    """
    from app.models.instrument import Instrument

    instrument = Instrument(
        ticker="TEST",
        name="Test Instrument",
        market="MOEX",
        instrument_type="stock",
        index_id=sample_index.id
    )
    test_db.add(instrument)
    test_db.commit()
    test_db.refresh(instrument)
    return instrument


@pytest.fixture(scope="function")
def sample_instruments(test_db, sample_index):
    """
    Создание нескольких тестовых инструментов
    """
    from app.models.instrument import Instrument

    instruments = [
        Instrument(
            ticker="GAZP",
            name="Gazprom",
            market="MOEX",
            instrument_type="stock",
            index_id=sample_index.id
        ),
        Instrument(
            ticker="SBER",
            name="Sberbank",
            market="MOEX",
            instrument_type="stock",
            index_id=sample_index.id
        ),
        Instrument(
            ticker="YNDX",
            name="Yandex",
            market="MOEX",
            instrument_type="stock"
        )
    ]

    for instrument in instruments:
        test_db.add(instrument)

    test_db.commit()

    for instrument in instruments:
        test_db.refresh(instrument)

    return instruments


@pytest.fixture(scope="function")
def sample_timeframe(test_db):
    """
    Создание тестового таймфрейма
    """
    from app.models.timeframe import Timeframe

    timeframe = Timeframe(
        code="1d",
        name="1 day",
        minutes=1440,
        moex_interval=24,
        description="Daily timeframe"
    )
    test_db.add(timeframe)
    test_db.commit()
    test_db.refresh(timeframe)
    return timeframe


@pytest.fixture(scope="function")
def sample_ohlcv(test_db, sample_instrument, sample_timeframe):
    """
    Создание тестовых OHLCV данных
    """
    from app.models.ohlcv import OHLCV
    from datetime import datetime, timedelta

    ohlcv_list = []
    base_date = datetime(2024, 1, 1)

    for i in range(10):
        ohlcv = OHLCV(
            instrument_id=sample_instrument.id,
            timeframe_id=sample_timeframe.id,
            timeframe="1d",
            timestamp=base_date + timedelta(days=i),
            open=100.0 + i,
            high=105.0 + i,
            low=95.0 + i,
            close=102.0 + i,
            volume=1000000 + i * 10000
        )
        ohlcv_list.append(ohlcv)
        test_db.add(ohlcv)

    test_db.commit()

    for ohlcv in ohlcv_list:
        test_db.refresh(ohlcv)

    return ohlcv_list


@pytest.fixture(scope="function")
def sample_signal(test_db, sample_instrument):
    """
    Создание тестового сигнала
    """
    from app.models.signal import Signal
    from datetime import datetime

    signal = Signal(
        instrument_id=sample_instrument.id,
        strategy_name="TestStrategy",
        signal_type="BUY",
        timestamp=datetime(2024, 1, 1, 10, 0, 0),
        price=100.0,
        confidence=0.85,
        position_size=1000.0,
        stop_loss=95.0,
        take_profit=110.0
    )
    test_db.add(signal)
    test_db.commit()
    test_db.refresh(signal)
    return signal


@pytest.fixture(scope="function")
def sample_signals(test_db, sample_instrument):
    """
    Создание нескольких тестовых сигналов
    """
    from app.models.signal import Signal
    from datetime import datetime, timedelta

    signals = []
    base_date = datetime(2024, 1, 1)

    for i in range(5):
        signal = Signal(
            instrument_id=sample_instrument.id,
            strategy_name="TestStrategy",
            signal_type="BUY" if i % 2 == 0 else "SELL",
            timestamp=base_date + timedelta(days=i),
            price=100.0 + i,
            confidence=0.7 + (i * 0.05),
            position_size=1000.0,
            stop_loss=95.0 + i,
            take_profit=110.0 + i
        )
        signals.append(signal)
        test_db.add(signal)

    test_db.commit()

    for signal in signals:
        test_db.refresh(signal)

    return signals
