"""
API endpoints для торговых сигналов
"""
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.instrument import Instrument
from app.models.signal import Signal as SignalModel
from app.signals.filters import apply_filters
from app.signals.generator import SignalGenerator
from app.signals.risk_manager import RiskManager
from app.strategies.registry import strategy_registry

router = APIRouter()


# Pydantic схемы


class SignalResponse(BaseModel):
    """Ответ с информацией о сигнале"""
    id: int
    instrument_id: int
    ticker: str
    strategy_name: str
    signal_type: str
    timestamp: datetime
    price: float
    confidence: Optional[float] = None
    position_size: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SignalGenerateRequest(BaseModel):
    """Запрос на генерацию сигналов"""
    strategy_name: str = Field(..., description="Название стратегии")
    ticker: str = Field(..., description="Тикер инструмента")
    start_date: Optional[date] = Field(None, description="Начальная дата")
    end_date: Optional[date] = Field(None, description="Конечная дата")

    # Параметры риск-менеджмента
    use_risk_manager: bool = Field(True, description="Использовать риск-менеджер")
    max_position_size: float = Field(0.1, description="Максимальный размер позиции (%)")
    atr_multiplier_sl: float = Field(2.0, description="Множитель ATR для Stop Loss")
    atr_multiplier_tp: float = Field(3.0, description="Множитель ATR для Take Profit")

    # Параметры фильтрации
    min_confidence: Optional[float] = Field(None, description="Минимальная уверенность")
    remove_duplicates: bool = Field(True, description="Удалить дубликаты")

    # Опции
    save_to_db: bool = Field(True, description="Сохранить сигналы в БД")


class SignalGenerateResponse(BaseModel):
    """Ответ на генерацию сигналов"""
    strategy_name: str
    ticker: str
    total_points: int
    signals_generated: int
    buy_signals: int
    sell_signals: int
    signals_saved: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    signals: List[SignalResponse]


class SignalStatsResponse(BaseModel):
    """Статистика по сигналам"""
    total_signals: int
    buy_signals: int
    sell_signals: int
    unique_strategies: int
    unique_instruments: int
    avg_confidence: Optional[float] = None
    date_range: Optional[dict] = None


# API Endpoints


@router.get("/", response_model=List[SignalResponse])
async def get_signals(
    ticker: Optional[str] = Query(None, description="Фильтр по тикеру"),
    strategy: Optional[str] = Query(None, description="Фильтр по стратегии"),
    signal_type: Optional[str] = Query(None, description="Фильтр по типу (BUY/SELL)"),
    start_date: Optional[date] = Query(None, description="Начальная дата"),
    end_date: Optional[date] = Query(None, description="Конечная дата"),
    min_confidence: Optional[float] = Query(None, description="Минимальная уверенность"),
    limit: int = Query(100, ge=1, le=1000, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: Session = Depends(get_db)
):
    """
    Получить список торговых сигналов с фильтрацией

    Поддерживает фильтрацию по:
    - Тикеру инструмента
    - Названию стратегии
    - Типу сигнала (BUY/SELL)
    - Диапазону дат
    - Минимальной уверенности
    """
    query = db.query(SignalModel).join(Instrument)

    # Фильтры
    if ticker:
        query = query.filter(Instrument.ticker == ticker)

    if strategy:
        query = query.filter(SignalModel.strategy_name == strategy)

    if signal_type:
        query = query.filter(SignalModel.signal_type == signal_type)

    if start_date:
        query = query.filter(SignalModel.timestamp >= start_date)

    if end_date:
        query = query.filter(SignalModel.timestamp <= end_date)

    if min_confidence is not None:
        query = query.filter(SignalModel.confidence >= min_confidence)

    # Сортировка по времени (новые первые)
    query = query.order_by(SignalModel.timestamp.desc())

    # Пагинация
    total = query.count()
    signals = query.offset(offset).limit(limit).all()

    # Добавить ticker к каждому сигналу
    result = []
    for signal in signals:
        signal_dict = {
            "id": signal.id,
            "instrument_id": signal.instrument_id,
            "ticker": signal.instrument.ticker,
            "strategy_name": signal.strategy_name,
            "signal_type": signal.signal_type,
            "timestamp": signal.timestamp,
            "price": signal.price,
            "confidence": signal.confidence,
            "position_size": signal.position_size,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "created_at": signal.created_at
        }
        result.append(SignalResponse(**signal_dict))

    logger.info(
        f"Retrieved {len(result)} signals (total: {total}, "
        f"offset: {offset}, limit: {limit})"
    )

    return result


@router.post("/generate", response_model=SignalGenerateResponse)
async def generate_signals(
    request: SignalGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Генерировать торговые сигналы на исторических данных

    Использует указанную стратегию для генерации сигналов
    на исторических данных инструмента.
    """
    logger.info(
        f"Generating signals: strategy={request.strategy_name}, "
        f"ticker={request.ticker}"
    )

    # Проверка существования инструмента
    instrument = (
        db.query(Instrument)
        .filter(Instrument.ticker == request.ticker)
        .first()
    )

    if not instrument:
        raise HTTPException(
            status_code=404,
            detail=f"Instrument {request.ticker} not found"
        )

    # Получить стратегию
    try:
        strategy_class = strategy_registry.get(request.strategy_name)
        strategy = strategy_class()
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Strategy '{request.strategy_name}' not found: {e}"
        )

    # Создать риск-менеджер (если требуется)
    risk_manager = None
    if request.use_risk_manager:
        risk_manager = RiskManager(
            max_position_size=request.max_position_size,
            atr_multiplier_sl=request.atr_multiplier_sl,
            atr_multiplier_tp=request.atr_multiplier_tp
        )

    # Создать генератор сигналов
    db_session = db if request.save_to_db else None
    generator = SignalGenerator(
        strategy=strategy,
        risk_manager=risk_manager,
        db_session=db_session
    )

    # Генерация сигналов
    try:
        signals = generator.generate_signals(
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date
        )
    except Exception as e:
        logger.error(f"Signal generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Signal generation failed: {e}"
        )

    # Применить фильтры
    if request.min_confidence or request.remove_duplicates:
        signals = apply_filters(
            signals,
            min_confidence=request.min_confidence,
            remove_duplicates=request.remove_duplicates
        )

    # Получить статистику
    stats = generator.get_stats()

    # Конвертировать сигналы в response format
    signal_responses = []
    for signal in signals:
        signal_responses.append(SignalResponse(
            id=0,  # Временный ID (если не сохранено в БД)
            instrument_id=instrument.id,
            ticker=request.ticker,
            strategy_name=request.strategy_name,
            signal_type=signal.signal_type,
            timestamp=signal.timestamp,
            price=signal.price,
            confidence=signal.confidence,
            position_size=signal.position_size,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            created_at=datetime.now()
        ))

    return SignalGenerateResponse(
        strategy_name=request.strategy_name,
        ticker=request.ticker,
        total_points=stats["total_points"],
        signals_generated=stats["signals_generated"],
        buy_signals=stats["buy_signals"],
        sell_signals=stats["sell_signals"],
        signals_saved=stats["signals_saved"],
        start_date=str(request.start_date) if request.start_date else None,
        end_date=str(request.end_date) if request.end_date else None,
        signals=signal_responses
    )


@router.get("/stats", response_model=SignalStatsResponse)
async def get_signal_stats(
    ticker: Optional[str] = Query(None, description="Фильтр по тикеру"),
    strategy: Optional[str] = Query(None, description="Фильтр по стратегии"),
    start_date: Optional[date] = Query(None, description="Начальная дата"),
    end_date: Optional[date] = Query(None, description="Конечная дата"),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по торговым сигналам

    Возвращает агрегированную статистику:
    - Общее количество сигналов
    - Количество BUY/SELL сигналов
    - Количество уникальных стратегий и инструментов
    - Средняя уверенность
    - Диапазон дат
    """
    query = db.query(SignalModel).join(Instrument)

    # Фильтры
    if ticker:
        query = query.filter(Instrument.ticker == ticker)

    if strategy:
        query = query.filter(SignalModel.strategy_name == strategy)

    if start_date:
        query = query.filter(SignalModel.timestamp >= start_date)

    if end_date:
        query = query.filter(SignalModel.timestamp <= end_date)

    # Статистика
    signals = query.all()

    if not signals:
        return SignalStatsResponse(
            total_signals=0,
            buy_signals=0,
            sell_signals=0,
            unique_strategies=0,
            unique_instruments=0
        )

    buy_count = sum(1 for s in signals if s.signal_type == "BUY")
    sell_count = sum(1 for s in signals if s.signal_type == "SELL")

    unique_strategies = len(set(s.strategy_name for s in signals))
    unique_instruments = len(set(s.instrument_id for s in signals))

    # Средняя уверенность
    confidences = [s.confidence for s in signals if s.confidence is not None]
    avg_confidence = sum(confidences) / len(confidences) if confidences else None

    # Диапазон дат
    timestamps = [s.timestamp for s in signals]
    date_range = {
        "min": str(min(timestamps).date()),
        "max": str(max(timestamps).date())
    } if timestamps else None

    return SignalStatsResponse(
        total_signals=len(signals),
        buy_signals=buy_count,
        sell_signals=sell_count,
        unique_strategies=unique_strategies,
        unique_instruments=unique_instruments,
        avg_confidence=round(avg_confidence, 4) if avg_confidence else None,
        date_range=date_range
    )


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить конкретный сигнал по ID
    """
    signal = db.query(SignalModel).filter(SignalModel.id == signal_id).first()

    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal {signal_id} not found")

    return SignalResponse(
        id=signal.id,
        instrument_id=signal.instrument_id,
        ticker=signal.instrument.ticker,
        strategy_name=signal.strategy_name,
        signal_type=signal.signal_type,
        timestamp=signal.timestamp,
        price=signal.price,
        confidence=signal.confidence,
        position_size=signal.position_size,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profit,
        created_at=signal.created_at
    )


@router.delete("/{signal_id}")
async def delete_signal(
    signal_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить сигнал по ID
    """
    signal = db.query(SignalModel).filter(SignalModel.id == signal_id).first()

    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal {signal_id} not found")

    db.delete(signal)
    db.commit()

    logger.info(f"Deleted signal {signal_id}")

    return {"message": f"Signal {signal_id} deleted successfully"}
