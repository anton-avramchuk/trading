"""
Модель индекса
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.database import Base


class Index(Base):
    """Модель биржевого индекса"""

    __tablename__ = "indexes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    description = Column(String(1000), nullable=True)

    # Связь с валютой
    currency_id = Column(Integer, ForeignKey("currencies.id", ondelete="SET NULL"), nullable=True, index=True)

    # Связь со страной
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True, index=True)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instruments = relationship("Instrument", back_populates="index")
    currency_rel = relationship("Currency", back_populates="indexes")
    country_rel = relationship("Country", back_populates="indexes")

    def __repr__(self) -> str:
        return f"<Index(ticker='{self.ticker}', name='{self.name}')>"
