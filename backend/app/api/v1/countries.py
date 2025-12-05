"""
API endpoints для работы со странами
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Country, get_db
from app.schemas.country import CountryCreate, CountryResponse, CountryUpdate

router = APIRouter()


@router.get("/", response_model=List[CountryResponse])
def get_countries(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    region: str = None,
    db: Session = Depends(get_db)
):
    """
    Получить список стран

    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        active_only: Вернуть только активные страны
        region: Фильтр по региону (Europe, Asia, Americas)
        db: Сессия базы данных

    Returns:
        Список стран
    """
    query = select(Country)

    if active_only:
        query = query.where(Country.is_active == 1)

    if region:
        query = query.where(Country.region == region)

    query = query.offset(skip).limit(limit).order_by(Country.id)

    countries = db.execute(query).scalars().all()
    return countries


@router.get("/{country_id}", response_model=CountryResponse)
def get_country(country_id: int, db: Session = Depends(get_db)):
    """
    Получить страну по ID

    Args:
        country_id: ID страны
        db: Сессия базы данных

    Returns:
        Данные страны

    Raises:
        HTTPException: Если страна не найдена
    """
    country = db.get(Country, country_id)

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {country_id} not found"
        )

    return country


@router.get("/code/{code}", response_model=CountryResponse)
def get_country_by_code(code: str, db: Session = Depends(get_db)):
    """
    Получить страну по коду

    Args:
        code: Код страны ISO 3166 (RU, US, GB и т.д.)
        db: Сессия базы данных

    Returns:
        Данные страны

    Raises:
        HTTPException: Если страна не найдена
    """
    query = select(Country).where(Country.code == code.upper())
    country = db.execute(query).scalar_one_or_none()

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with code '{code}' not found"
        )

    return country


@router.post("/", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
def create_country(country: CountryCreate, db: Session = Depends(get_db)):
    """
    Создать новую страну

    Args:
        country: Данные новой страны
        db: Сессия базы данных

    Returns:
        Созданная страна

    Raises:
        HTTPException: Если страна с таким кодом уже существует
    """
    # Проверка на дубликат
    existing = db.execute(
        select(Country).where(Country.code == country.code.upper())
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Country with code '{country.code}' already exists"
        )

    db_country = Country(**country.model_dump())
    db_country.code = db_country.code.upper()  # Код всегда в верхнем регистре
    if db_country.code3:
        db_country.code3 = db_country.code3.upper()

    db.add(db_country)
    db.commit()
    db.refresh(db_country)

    return db_country


@router.patch("/{country_id}", response_model=CountryResponse)
def update_country(
    country_id: int,
    country_update: CountryUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить данные страны

    Args:
        country_id: ID страны
        country_update: Данные для обновления
        db: Сессия базы данных

    Returns:
        Обновленная страна

    Raises:
        HTTPException: Если страна не найдена
    """
    country = db.get(Country, country_id)

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {country_id} not found"
        )

    # Обновление только предоставленных полей
    update_data = country_update.model_dump(exclude_unset=True)

    # Коды всегда в верхнем регистре
    if "code" in update_data:
        update_data["code"] = update_data["code"].upper()
    if "code3" in update_data and update_data["code3"]:
        update_data["code3"] = update_data["code3"].upper()

    for field, value in update_data.items():
        setattr(country, field, value)

    db.commit()
    db.refresh(country)

    return country


@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_id: int, db: Session = Depends(get_db)):
    """
    Удалить страну

    Args:
        country_id: ID страны
        db: Сессия базы данных

    Raises:
        HTTPException: Если страна не найдена
    """
    country = db.get(Country, country_id)

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {country_id} not found"
        )

    db.delete(country)
    db.commit()
