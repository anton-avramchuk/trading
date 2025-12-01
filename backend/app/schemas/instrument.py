"""
Pydantic схемы для инструментов
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class InstrumentBase(BaseModel):
    """Базовая схема инструмента"""

    ticker: str = Field(..., min_length=1, max_length=20, description="Тикер инструмента")
    name: str = Field(..., min_length=1, max_length=255, description="Название инструмента")
    market: str = Field(..., description="Рынок (MOEX, CME, и т.д.)")
    instrument_type: str = Field(..., description="Тип инструмента (stock, future, index)")

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        """Преобразование тикера в верхний регистр"""
        return v.upper().strip()

    @field_validator("instrument_type")
    @classmethod
    def validate_instrument_type(cls, v: str) -> str:
        """Валидация типа инструмента"""
        allowed_types = ["stock", "future", "index", "bond", "currency"]
        if v.lower() not in allowed_types:
            raise ValueError(f"instrument_type must be one of {allowed_types}")
        return v.lower()


class InstrumentCreate(InstrumentBase):
    """Схема для создания инструмента"""

    index_id: Optional[int] = Field(None, description="ID индекса")


class InstrumentUpdate(BaseModel):
    """Схема для обновления инструмента"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    market: Optional[str] = None
    instrument_type: Optional[str] = None
    index_id: Optional[int] = None


class InstrumentRead(InstrumentBase):
    """Схема для чтения инструмента"""

    id: int
    index_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InstrumentWithIndex(InstrumentRead):
    """Схема инструмента с информацией об индексе"""

    index_name: Optional[str] = None
    index_ticker: Optional[str] = None


# Index schemas
class IndexBase(BaseModel):
    """Базовая схема индекса"""

    name: str = Field(..., min_length=1, max_length=255, description="Название индекса")
    ticker: str = Field(..., min_length=1, max_length=20, description="Тикер индекса")
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        """Преобразование тикера в верхний регистр"""
        return v.upper().strip()


class IndexCreate(IndexBase):
    """Схема для создания индекса"""

    pass


class IndexUpdate(BaseModel):
    """Схема для обновления индекса"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class IndexRead(IndexBase):
    """Схема для чтения индекса"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IndexWithInstruments(IndexRead):
    """Схема индекса со списком инструментов"""

    instruments_count: int = 0
