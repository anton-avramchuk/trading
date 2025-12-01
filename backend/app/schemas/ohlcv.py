"""
Pydantic схемы для OHLCV данных
"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator


class OHLCVBase(BaseModel):
    """Базовая схема OHLCV"""

    timestamp: datetime = Field(..., description="Время свечи")
    open: float = Field(..., gt=0, description="Цена открытия")
    high: float = Field(..., gt=0, description="Максимальная цена")
    low: float = Field(..., gt=0, description="Минимальная цена")
    close: float = Field(..., gt=0, description="Цена закрытия")
    volume: int = Field(..., ge=0, description="Объем торгов")

    @field_validator("high")
    @classmethod
    def validate_high(cls, v: float, info) -> float:
        """Валидация максимальной цены"""
        values = info.data
        if "open" in values and "close" in values:
            if v < max(values["open"], values["close"]):
                raise ValueError("high must be >= max(open, close)")
        return v

    @field_validator("low")
    @classmethod
    def validate_low(cls, v: float, info) -> float:
        """Валидация минимальной цены"""
        values = info.data
        if "open" in values and "close" in values:
            if v > min(values["open"], values["close"]):
                raise ValueError("low must be <= min(open, close)")
        return v


class OHLCVCreate(OHLCVBase):
    """Схема для создания OHLCV записи"""

    instrument_id: int = Field(..., description="ID инструмента")
    timeframe: str = Field(..., description="Таймфрейм (1h, 1d, 1w, 1M)")

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        """Валидация таймфрейма"""
        allowed = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
        if v not in allowed:
            raise ValueError(f"timeframe must be one of {allowed}")
        return v


class OHLCVRead(OHLCVBase):
    """Схема для чтения OHLCV"""

    id: int
    instrument_id: int
    timeframe: str

    class Config:
        from_attributes = True


class OHLCVQuery(BaseModel):
    """Схема для запроса OHLCV данных"""

    ticker: str = Field(..., description="Тикер инструмента")
    timeframe: str = Field("1d", description="Таймфрейм")
    start: datetime = Field(..., description="Начальная дата")
    end: datetime = Field(..., description="Конечная дата")

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        """Валидация таймфрейма"""
        allowed = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
        if v not in allowed:
            raise ValueError(f"timeframe must be one of {allowed}")
        return v


class OHLCVBulkCreate(BaseModel):
    """Схема для массового создания OHLCV"""

    instrument_id: int
    timeframe: str
    data: List[OHLCVBase]


class OHLCVImportRequest(BaseModel):
    """Схема для импорта OHLCV из CSV"""

    ticker: str = Field(..., description="Тикер инструмента")
    csv_path: str = Field(..., description="Путь к CSV файлу")
    timeframe: str = Field(..., description="Таймфрейм данных")

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        """Валидация таймфрейма"""
        allowed = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
        if v not in allowed:
            raise ValueError(f"timeframe must be one of {allowed}")
        return v


class TimeframeList(BaseModel):
    """Список доступных таймфреймов"""

    timeframes: List[str] = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
