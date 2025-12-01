"""
Pydantic схемы для торговых сигналов
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SignalBase(BaseModel):
    """Базовая схема сигнала"""

    signal_type: str = Field(..., description="Тип сигнала (BUY, SELL)")
    timestamp: datetime = Field(..., description="Время сигнала")
    price: float = Field(..., gt=0, description="Цена")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Уверенность (0-1)")

    @field_validator("signal_type")
    @classmethod
    def validate_signal_type(cls, v: str) -> str:
        """Валидация типа сигнала"""
        allowed = ["BUY", "SELL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"signal_type must be one of {allowed}")
        return v_upper


class SignalCreate(SignalBase):
    """Схема для создания сигнала"""

    instrument_id: int = Field(..., description="ID инструмента")
    strategy_name: str = Field(..., min_length=1, max_length=255, description="Название стратегии")
    position_size: Optional[float] = Field(None, gt=0, description="Размер позиции")
    stop_loss: Optional[float] = Field(None, gt=0, description="Стоп-лосс")
    take_profit: Optional[float] = Field(None, gt=0, description="Тейк-профит")


class SignalRead(SignalBase):
    """Схема для чтения сигнала"""

    id: int
    instrument_id: int
    strategy_name: str
    position_size: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SignalWithInstrument(SignalRead):
    """Схема сигнала с информацией об инструменте"""

    ticker: str
    instrument_name: str


class SignalQuery(BaseModel):
    """Схема для запроса сигналов"""

    ticker: Optional[str] = Field(None, description="Тикер инструмента")
    strategy_name: Optional[str] = Field(None, description="Название стратегии")
    signal_type: Optional[str] = Field(None, description="Тип сигнала (BUY, SELL)")
    start: Optional[datetime] = Field(None, description="Начальная дата")
    end: Optional[datetime] = Field(None, description="Конечная дата")
    limit: int = Field(100, ge=1, le=1000, description="Количество результатов")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")

    @field_validator("signal_type")
    @classmethod
    def validate_signal_type(cls, v: Optional[str]) -> Optional[str]:
        """Валидация типа сигнала"""
        if v is None:
            return None
        allowed = ["BUY", "SELL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"signal_type must be one of {allowed}")
        return v_upper


class SignalGenerateRequest(BaseModel):
    """Схема для запроса генерации сигналов"""

    strategy_id: int = Field(..., description="ID стратегии")
    tickers: List[str] = Field(..., min_length=1, description="Список тикеров")
    start_date: datetime = Field(..., description="Начальная дата")
    end_date: datetime = Field(..., description="Конечная дата")


class SignalGenerateResponse(BaseModel):
    """Схема ответа на генерацию сигналов"""

    generated_count: int = Field(..., description="Количество сгенерированных сигналов")
    signals: List[SignalRead] = Field(..., description="Список сигналов")


class SignalStatistics(BaseModel):
    """Статистика по сигналам"""

    total_signals: int
    buy_signals: int
    sell_signals: int
    avg_confidence: Optional[float] = None
    strategies: List[str] = []
