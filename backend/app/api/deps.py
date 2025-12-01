"""
API Dependencies
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии базы данных

    Yields:
        Session: Сессия SQLAlchemy

    Example:
        ```python
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Placeholder для будущей аутентификации
def get_current_user():
    """
    Dependency для получения текущего пользователя
    (будет реализовано позже)
    """
    pass


# Placeholder для проверки прав доступа
def check_permissions():
    """
    Dependency для проверки прав доступа
    (будет реализовано позже)
    """
    pass
