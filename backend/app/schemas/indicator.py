"""
Pydantic схемы для индикаторов
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IndicatorParameter(BaseModel):
    """Параметр индикатора"""

    name: str = Field(..., description="Название параметра")
    type: str = Field(..., description="Тип параметра (int, float, str)")
    default: Any = Field(..., description="Значение по умолчанию")
    description: Optional[str] = Field(None, description="Описание параметра")
    min_value: Optional[float] = Field(None, description="Минимальное значение")
    max_value: Optional[float] = Field(None, description="Максимальное значение")


class IndicatorInfo(BaseModel):
    """Информация об индикаторе"""

    name: str = Field(..., description="Название индикатора")
    category: str = Field(..., description="Категория индикатора")
    description: Optional[str] = Field(None, description="Описание")
    parameters: List[IndicatorParameter] = Field(default_factory=list, description="Параметры")


class IndicatorConfig(BaseModel):
    """Конфигурация индикатора"""

    name: str = Field(..., description="Название индикатора")
    timeframe: str = Field("1d", description="Таймфрейм")
    params: Dict[str, Any] = Field(default_factory=dict, description="Параметры индикатора")


class IndicatorCalculateRequest(BaseModel):
    """Запрос на расчёт индикатора"""

    ticker: str = Field(..., description="Тикер инструмента")
    timeframe: str = Field("1d", description="Таймфрейм")
    indicator: str = Field(..., description="Название индикатора")
    params: Dict[str, Any] = Field(default_factory=dict, description="Параметры индикатора")
    start: Optional[str] = Field(None, description="Начальная дата (YYYY-MM-DD)")
    end: Optional[str] = Field(None, description="Конечная дата (YYYY-MM-DD)")


class IndicatorValue(BaseModel):
    """Значение индикатора"""

    timestamp: str = Field(..., description="Время")
    value: float = Field(..., description="Значение индикатора")


class IndicatorCalculateResponse(BaseModel):
    """Ответ на расчёт индикатора"""

    indicator: str = Field(..., description="Название индикатора")
    timeframe: str = Field(..., description="Таймфрейм")
    values: List[IndicatorValue] = Field(..., description="Значения индикатора")


class IndicatorListResponse(BaseModel):
    """Список доступных индикаторов"""

    indicators: List[IndicatorInfo] = Field(..., description="Список индикаторов")
    total: int = Field(..., description="Общее количество")


class MultiTimeframeIndicatorConfig(BaseModel):
    """Конфигурация мульти-таймфрейм индикаторов"""

    indicators: List[IndicatorConfig] = Field(..., description="Список индикаторов")
