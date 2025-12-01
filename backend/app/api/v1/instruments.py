"""
API endpoints для инструментов и индексов
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Index, Instrument
from app.schemas import (
    IndexCreate,
    IndexRead,
    IndexUpdate,
    InstrumentCreate,
    InstrumentRead,
    InstrumentUpdate,
    InstrumentWithIndex,
)

router = APIRouter()


# ===== Instruments Endpoints =====

@router.get("/", response_model=List[InstrumentRead])
def get_instruments(
    skip: int = 0,
    limit: int = 100,
    market: str | None = None,
    instrument_type: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Получить список инструментов

    Args:
        skip: Пропустить N записей (для пагинации)
        limit: Максимальное количество записей
        market: Фильтр по рынку (опционально)
        instrument_type: Фильтр по типу инструмента (опционально)

    Returns:
        List[InstrumentRead]: Список инструментов
    """
    query = db.query(Instrument)

    if market:
        query = query.filter(Instrument.market == market.upper())

    if instrument_type:
        query = query.filter(Instrument.instrument_type == instrument_type.lower())

    instruments = query.offset(skip).limit(limit).all()
    return instruments


@router.get("/{ticker}", response_model=InstrumentWithIndex)
def get_instrument(ticker: str, db: Session = Depends(get_db)):
    """
    Получить информацию об инструменте по тикеру

    Args:
        ticker: Тикер инструмента

    Returns:
        InstrumentWithIndex: Информация об инструменте с данными индекса

    Raises:
        HTTPException: 404 если инструмент не найден
    """
    instrument = db.query(Instrument).filter(
        Instrument.ticker == ticker.upper()
    ).first()

    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {ticker} not found"
        )

    # Подготовка данных с индексом
    result = InstrumentWithIndex(
        id=instrument.id,
        ticker=instrument.ticker,
        name=instrument.name,
        market=instrument.market,
        instrument_type=instrument.instrument_type,
        index_id=instrument.index_id,
        created_at=instrument.created_at,
        updated_at=instrument.updated_at,
        index_name=instrument.index.name if instrument.index else None,
        index_ticker=instrument.index.ticker if instrument.index else None
    )

    return result


@router.post("/", response_model=InstrumentRead, status_code=status.HTTP_201_CREATED)
def create_instrument(
    instrument: InstrumentCreate,
    db: Session = Depends(get_db)
):
    """
    Создать новый инструмент

    Args:
        instrument: Данные для создания инструмента

    Returns:
        InstrumentRead: Созданный инструмент

    Raises:
        HTTPException: 400 если инструмент с таким тикером уже существует
        HTTPException: 404 если указанный index_id не найден
    """
    # Проверка на существование
    existing = db.query(Instrument).filter(
        Instrument.ticker == instrument.ticker.upper()
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Instrument with ticker {instrument.ticker} already exists"
        )

    # Проверка существования индекса (если указан)
    if instrument.index_id:
        index = db.query(Index).filter(Index.id == instrument.index_id).first()
        if not index:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Index with id {instrument.index_id} not found"
            )

    # Создание инструмента
    db_instrument = Instrument(
        ticker=instrument.ticker.upper(),
        name=instrument.name,
        market=instrument.market,
        instrument_type=instrument.instrument_type,
        index_id=instrument.index_id
    )

    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)

    logger.info(f"Created instrument: {db_instrument.ticker}")
    return db_instrument


@router.put("/{ticker}", response_model=InstrumentRead)
def update_instrument(
    ticker: str,
    instrument_update: InstrumentUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить информацию об инструменте

    Args:
        ticker: Тикер инструмента
        instrument_update: Данные для обновления

    Returns:
        InstrumentRead: Обновлённый инструмент

    Raises:
        HTTPException: 404 если инструмент не найден
    """
    instrument = db.query(Instrument).filter(
        Instrument.ticker == ticker.upper()
    ).first()

    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {ticker} not found"
        )

    # Обновление полей
    update_data = instrument_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instrument, field, value)

    db.commit()
    db.refresh(instrument)

    logger.info(f"Updated instrument: {instrument.ticker}")
    return instrument


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instrument(ticker: str, db: Session = Depends(get_db)):
    """
    Удалить инструмент

    Args:
        ticker: Тикер инструмента

    Raises:
        HTTPException: 404 если инструмент не найден
    """
    instrument = db.query(Instrument).filter(
        Instrument.ticker == ticker.upper()
    ).first()

    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {ticker} not found"
        )

    db.delete(instrument)
    db.commit()

    logger.info(f"Deleted instrument: {ticker}")
    return None


@router.put("/{ticker}/index/{index_id}", response_model=InstrumentRead)
def link_instrument_to_index(
    ticker: str,
    index_id: int,
    db: Session = Depends(get_db)
):
    """
    Связать инструмент с индексом

    Args:
        ticker: Тикер инструмента
        index_id: ID индекса

    Returns:
        InstrumentRead: Обновлённый инструмент

    Raises:
        HTTPException: 404 если инструмент или индекс не найден
    """
    instrument = db.query(Instrument).filter(
        Instrument.ticker == ticker.upper()
    ).first()

    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {ticker} not found"
        )

    index = db.query(Index).filter(Index.id == index_id).first()
    if not index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index with id {index_id} not found"
        )

    instrument.index_id = index_id
    db.commit()
    db.refresh(instrument)

    logger.info(f"Linked instrument {ticker} to index {index.ticker}")
    return instrument


# ===== Indexes Endpoints =====

@router.get("/indexes/", response_model=List[IndexRead])
def get_indexes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список индексов

    Args:
        skip: Пропустить N записей
        limit: Максимальное количество записей

    Returns:
        List[IndexRead]: Список индексов
    """
    indexes = db.query(Index).offset(skip).limit(limit).all()
    return indexes


@router.get("/indexes/{index_id}", response_model=IndexRead)
def get_index(index_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию об индексе

    Args:
        index_id: ID индекса

    Returns:
        IndexRead: Информация об индексе

    Raises:
        HTTPException: 404 если индекс не найден
    """
    index = db.query(Index).filter(Index.id == index_id).first()

    if not index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index with id {index_id} not found"
        )

    return index


@router.post("/indexes/", response_model=IndexRead, status_code=status.HTTP_201_CREATED)
def create_index(index: IndexCreate, db: Session = Depends(get_db)):
    """
    Создать новый индекс

    Args:
        index: Данные для создания индекса

    Returns:
        IndexRead: Созданный индекс

    Raises:
        HTTPException: 400 если индекс с таким тикером уже существует
    """
    # Проверка на существование
    existing = db.query(Index).filter(
        Index.ticker == index.ticker.upper()
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Index with ticker {index.ticker} already exists"
        )

    # Создание индекса
    db_index = Index(
        name=index.name,
        ticker=index.ticker.upper(),
        description=index.description
    )

    db.add(db_index)
    db.commit()
    db.refresh(db_index)

    logger.info(f"Created index: {db_index.ticker}")
    return db_index


@router.put("/indexes/{index_id}", response_model=IndexRead)
def update_index(
    index_id: int,
    index_update: IndexUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить информацию об индексе

    Args:
        index_id: ID индекса
        index_update: Данные для обновления

    Returns:
        IndexRead: Обновлённый индекс

    Raises:
        HTTPException: 404 если индекс не найден
    """
    index = db.query(Index).filter(Index.id == index_id).first()

    if not index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index with id {index_id} not found"
        )

    # Обновление полей
    update_data = index_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(index, field, value)

    db.commit()
    db.refresh(index)

    logger.info(f"Updated index: {index.ticker}")
    return index


@router.delete("/indexes/{index_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_index(index_id: int, db: Session = Depends(get_db)):
    """
    Удалить индекс

    Args:
        index_id: ID индекса

    Raises:
        HTTPException: 404 если индекс не найден
    """
    index = db.query(Index).filter(Index.id == index_id).first()

    if not index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index with id {index_id} not found"
        )

    db.delete(index)
    db.commit()

    logger.info(f"Deleted index: {index.ticker}")
    return None
