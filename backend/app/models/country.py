"""
Модель страны (ISO 3166)
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.models.database import Base


class Country(Base):
    """Модель страны"""

    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)

    # Код страны ISO 3166-1 alpha-2 (RU, US, GB, CN, etc.)
    code = Column(String(2), unique=True, nullable=False, index=True)

    # Код страны ISO 3166-1 alpha-3 (RUS, USA, GBR, CHN, etc.)
    code3 = Column(String(3), nullable=True)

    # Название страны
    name = Column(String(100), nullable=False)

    # Название на английском
    name_en = Column(String(100), nullable=True)

    # Регион (Europe, Asia, Americas, etc.)
    region = Column(String(50), nullable=True)

    # Активна ли страна
    is_active = Column(Integer, nullable=False, default=1)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    indexes = relationship("Index", back_populates="country_rel")

    def __repr__(self) -> str:
        return f"<Country(code='{self.code}', name='{self.name}')>"
