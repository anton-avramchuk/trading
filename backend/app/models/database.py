"""
Настройка базы данных
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

# Создание engine с параметрами в зависимости от типа БД
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite не поддерживает pool_size, max_overflow
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG_MODE
    )
else:
    # PostgreSQL/MySQL и другие БД
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG_MODE
    )

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Базовый класс для моделей
class Base(DeclarativeBase):
    """Базовый класс для всех моделей БД"""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии базы данных

    Yields:
        Session: Сессия SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Инициализация базы данных"""
    Base.metadata.create_all(bind=engine)
