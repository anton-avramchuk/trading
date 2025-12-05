"""
API endpoints для работы с валютами
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Currency, get_db
from app.schemas.currency import CurrencyCreate, CurrencyResponse, CurrencyUpdate

router = APIRouter()


@router.get("/", response_model=List[CurrencyResponse])
def get_currencies(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Получить список валют

    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        active_only: Вернуть только активные валюты
        db: Сессия базы данных

    Returns:
        Список валют
    """
    query = select(Currency)

    if active_only:
        query = query.where(Currency.is_active == 1)

    query = query.offset(skip).limit(limit).order_by(Currency.id)

    currencies = db.execute(query).scalars().all()
    return currencies


@router.get("/{currency_id}", response_model=CurrencyResponse)
def get_currency(currency_id: int, db: Session = Depends(get_db)):
    """
    Получить валюту по ID

    Args:
        currency_id: ID валюты
        db: Сессия базы данных

    Returns:
        Данные валюты

    Raises:
        HTTPException: Если валюта не найдена
    """
    currency = db.get(Currency, currency_id)

    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency with id {currency_id} not found"
        )

    return currency


@router.get("/code/{code}", response_model=CurrencyResponse)
def get_currency_by_code(code: str, db: Session = Depends(get_db)):
    """
    Получить валюту по коду

    Args:
        code: Код валюты (RUB, USD, EUR, BTC и т.д.)
        db: Сессия базы данных

    Returns:
        Данные валюты

    Raises:
        HTTPException: Если валюта не найдена
    """
    query = select(Currency).where(Currency.code == code.upper())
    currency = db.execute(query).scalar_one_or_none()

    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency with code '{code}' not found"
        )

    return currency


@router.post("/", response_model=CurrencyResponse, status_code=status.HTTP_201_CREATED)
def create_currency(currency: CurrencyCreate, db: Session = Depends(get_db)):
    """
    Создать новую валюту

    Args:
        currency: Данные новой валюты
        db: Сессия базы данных

    Returns:
        Созданная валюта

    Raises:
        HTTPException: Если валюта с таким кодом уже существует
    """
    # Проверка на дубликат
    existing = db.execute(
        select(Currency).where(Currency.code == currency.code.upper())
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency with code '{currency.code}' already exists"
        )

    db_currency = Currency(**currency.model_dump())
    db_currency.code = db_currency.code.upper()  # Код всегда в верхнем регистре

    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)

    return db_currency


@router.patch("/{currency_id}", response_model=CurrencyResponse)
def update_currency(
    currency_id: int,
    currency_update: CurrencyUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить данные валюты

    Args:
        currency_id: ID валюты
        currency_update: Данные для обновления
        db: Сессия базы данных

    Returns:
        Обновленная валюта

    Raises:
        HTTPException: Если валюта не найдена
    """
    currency = db.get(Currency, currency_id)

    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency with id {currency_id} not found"
        )

    # Обновление только предоставленных полей
    update_data = currency_update.model_dump(exclude_unset=True)

    # Код всегда в верхнем регистре
    if "code" in update_data:
        update_data["code"] = update_data["code"].upper()

    for field, value in update_data.items():
        setattr(currency, field, value)

    db.commit()
    db.refresh(currency)

    return currency


@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_currency(currency_id: int, db: Session = Depends(get_db)):
    """
    Удалить валюту

    Args:
        currency_id: ID валюты
        db: Сессия базы данных

    Raises:
        HTTPException: Если валюта не найдена
    """
    currency = db.get(Currency, currency_id)

    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency with id {currency_id} not found"
        )

    db.delete(currency)
    db.commit()
