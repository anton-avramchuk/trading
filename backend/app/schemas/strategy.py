"""
Pydantic схемы для стратегий
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StrategyBase(BaseModel):
    """Базовая схема стратегии"""

    name: str = Field(..., min_length=1, max_length=255, description="Название стратегии")
    description: Optional[str] = Field(None, description="Описание стратегии")


class StrategyConfig(BaseModel):
    """Конфигурация стратегии"""

    indicators: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Список индикаторов с их параметрами"
    )
    rules: Dict[str, str] = Field(
        default_factory=dict,
        description="Правила входа и выхода"
    )
    timeframes: List[str] = Field(
        default_factory=list,
        description="Используемые таймфреймы"
    )


class StrategyCreate(StrategyBase):
    """Схема для создания стратегии"""

    config: StrategyConfig = Field(..., description="Конфигурация стратегии")


class StrategyUpdate(BaseModel):
    """Схема для обновления стратегии"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[StrategyConfig] = None
    is_active: Optional[bool] = None


class StrategyRead(StrategyBase):
    """Схема для чтения стратегии"""

    id: int
    config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StrategyDetails(StrategyRead):
    """Детальная информация о стратегии"""

    signals_count: Optional[int] = Field(None, description="Количество сгенерированных сигналов")
    backtests_count: Optional[int] = Field(None, description="Количество бэктестов")


class StrategyListItem(BaseModel):
    """Элемент списка стратегий"""

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    timeframes: List[str] = []
    indicators_count: int = 0
    created_at: datetime


class StrategyListResponse(BaseModel):
    """Список стратегий"""

    strategies: List[StrategyListItem]
    total: int


class StrategyIndicator(BaseModel):
    """Индикатор стратегии"""

    name: str = Field(..., description="Название индикатора")
    timeframe: str = Field(..., description="Таймфрейм")
    params: Dict[str, Any] = Field(default_factory=dict, description="Параметры")


class StrategyRule(BaseModel):
    """Правило стратегии"""

    type: str = Field(..., description="Тип правила (entry, exit)")
    condition: str = Field(..., description="Условие в виде строки")


class StrategyValidation(BaseModel):
    """Результат валидации стратегии"""

    is_valid: bool = Field(..., description="Валидна ли стратегия")
    errors: List[str] = Field(default_factory=list, description="Список ошибок")
    warnings: List[str] = Field(default_factory=list, description="Список предупреждений")
