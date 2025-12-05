"""
Pydantic схемы для Country
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CountryBase(BaseModel):
    """Базовая схема страны"""

    code: str = Field(..., min_length=2, max_length=2, description="Код страны ISO 3166 Alpha-2 (RU, US)")
    code3: Optional[str] = Field(None, min_length=3, max_length=3, description="Код страны ISO 3166 Alpha-3 (RUS, USA)")
    name: str = Field(..., min_length=1, max_length=100, description="Название страны")
    name_en: Optional[str] = Field(None, max_length=100, description="Название на английском")
    region: Optional[str] = Field(None, max_length=50, description="Регион (Europe, Asia, Americas)")
    is_active: int = Field(1, ge=0, le=1, description="Активна ли страна (1 - да, 0 - нет)")


class CountryCreate(CountryBase):
    """Схема для создания страны"""
    pass


class CountryUpdate(BaseModel):
    """Схема для обновления страны"""

    code: Optional[str] = Field(None, min_length=2, max_length=2)
    code3: Optional[str] = Field(None, min_length=3, max_length=3)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    is_active: Optional[int] = Field(None, ge=0, le=1)


class CountryResponse(CountryBase):
    """Схема для ответа с данными страны"""

    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
