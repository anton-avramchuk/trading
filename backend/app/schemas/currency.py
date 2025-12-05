"""
Pydantic схемы для Currency
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CurrencyBase(BaseModel):
    """Базовая схема валюты"""

    code: str = Field(..., min_length=1, max_length=10, description="Код валюты (RUB, USD, BTC)")
    numeric_code: Optional[str] = Field(None, max_length=3, description="Цифровой код ISO 4217")
    name: str = Field(..., min_length=1, max_length=100, description="Название валюты")
    name_en: Optional[str] = Field(None, max_length=100, description="Название на английском")
    symbol: Optional[str] = Field(None, max_length=10, description="Символ валюты (₽, $, €)")
    decimal_places: int = Field(2, ge=0, le=18, description="Количество знаков после запятой")
    is_active: int = Field(1, ge=0, le=1, description="Активна ли валюта (1 - да, 0 - нет)")


class CurrencyCreate(CurrencyBase):
    """Схема для создания валюты"""
    pass


class CurrencyUpdate(BaseModel):
    """Схема для обновления валюты"""

    code: Optional[str] = Field(None, min_length=1, max_length=10)
    numeric_code: Optional[str] = Field(None, max_length=3)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)
    decimal_places: Optional[int] = Field(None, ge=0, le=18)
    is_active: Optional[int] = Field(None, ge=0, le=1)


class CurrencyResponse(CurrencyBase):
    """Схема для ответа с данными валюты"""

    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
