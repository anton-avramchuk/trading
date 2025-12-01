"""
Модель индекса
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.models.database import Base


class Index(Base):
    """Модель биржевого индекса"""

    __tablename__ = "indexes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    description = Column(String(1000), nullable=True)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instruments = relationship("Instrument", back_populates="index")

    def __repr__(self) -> str:
        return f"<Index(ticker='{self.ticker}', name='{self.name}')>"
