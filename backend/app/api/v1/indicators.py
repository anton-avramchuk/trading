"""
API endpoints для индикаторов
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.data_manager import DataManager
from app.indicators import IndicatorRegistry
from app.schemas import (
    IndicatorCalculateRequest,
    IndicatorCalculateResponse,
    IndicatorInfo,
    IndicatorListResponse,
)

router = APIRouter()


@router.get("/", response_model=IndicatorListResponse)
def get_indicators():
    """
    Получить список всех доступных индикаторов

    Returns:
        IndicatorListResponse: Список индикаторов с метаданными
    """
    all_indicators = IndicatorRegistry.get_all_info()

    logger.info(f"Retrieved {len(all_indicators)} indicators")

    return IndicatorListResponse(
        total=len(all_indicators),
        indicators=all_indicators
    )


@router.get("/{name}", response_model=IndicatorInfo)
def get_indicator_info(name: str):
    """
    Получить информацию о конкретном индикаторе

    Args:
        name: Название индикатора

    Returns:
        IndicatorInfo: Метаданные индикатора

    Raises:
        HTTPException: 404 если индикатор не найден
    """
    info = IndicatorRegistry.get_info(name)

    if info is None:
        available = ", ".join(IndicatorRegistry.list_names())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicator '{name}' not found. Available: {available}"
        )

    logger.debug(f"Retrieved info for indicator: {name}")

    return IndicatorInfo(**info)


@router.get("/category/{category}", response_model=IndicatorListResponse)
def get_indicators_by_category(category: str):
    """
    Получить индикаторы по категории

    Args:
        category: Категория (trend, momentum, volatility, volume, custom)

    Returns:
        IndicatorListResponse: Список индикаторов данной категории

    Raises:
        HTTPException: 400 если категория некорректна
    """
    valid_categories = ["trend", "momentum", "volatility", "volume", "custom"]

    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category: {category}. Valid: {', '.join(valid_categories)}"
        )

    indicators_dict = IndicatorRegistry.get_by_category(category)
    indicators_info = [
        indicator_class.get_info()
        for indicator_class in indicators_dict.values()
    ]

    logger.info(f"Retrieved {len(indicators_info)} indicators for category '{category}'")

    return IndicatorListResponse(
        total=len(indicators_info),
        indicators=indicators_info
    )


@router.post("/calculate", response_model=IndicatorCalculateResponse)
def calculate_indicator(
    request: IndicatorCalculateRequest,
    db: Session = Depends(get_db)
):
    """
    Рассчитать индикатор на исторических данных

    Args:
        request: Параметры расчёта (indicator_name, ticker, timeframe, dates, parameters)

    Returns:
        IndicatorCalculateResponse: Результаты расчёта индикатора

    Raises:
        HTTPException: 404 если индикатор или инструмент не найден
        HTTPException: 400 если некорректные параметры
        HTTPException: 500 если ошибка расчёта
    """
    logger.info(
        f"Calculating indicator: {request.indicator_name} for {request.ticker} "
        f"{request.timeframe}"
    )

    # Проверка существования индикатора
    if IndicatorRegistry.get(request.indicator_name) is None:
        available = ", ".join(IndicatorRegistry.list_names())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicator '{request.indicator_name}' not found. Available: {available}"
        )

    try:
        # Получение данных
        data_manager = DataManager(db)
        df = data_manager.get_data(
            ticker=request.ticker,
            timeframe=request.timeframe,
            start=request.start_date,
            end=request.end_date
        )

        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for {request.ticker} {request.timeframe}"
            )

        # Создание экземпляра индикатора
        indicator = IndicatorRegistry.create_indicator(
            name=request.indicator_name,
            timeframe=request.timeframe,
            **(request.parameters or {})
        )

        # Расчёт индикатора
        result = indicator.calculate(df)

        # Конвертация результата в dict
        if hasattr(result, 'to_dict'):
            # DataFrame - несколько колонок
            result_dict = result.to_dict(orient='index')
            # Конвертация timestamp в строку
            result_dict = {
                str(timestamp): values
                for timestamp, values in result_dict.items()
            }
        else:
            # Series - одна колонка
            result_dict = {
                str(timestamp): {"value": value}
                for timestamp, value in result.items()
            }

        logger.info(
            f"Successfully calculated {request.indicator_name} "
            f"for {request.ticker}, {len(result_dict)} data points"
        )

        return IndicatorCalculateResponse(
            indicator_name=request.indicator_name,
            ticker=request.ticker,
            timeframe=request.timeframe,
            parameters=request.parameters or {},
            result=result_dict
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating indicator: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating indicator: {str(e)}"
        )


@router.post("/calculate/multiple", response_model=List[IndicatorCalculateResponse])
def calculate_multiple_indicators(
    requests: List[IndicatorCalculateRequest],
    db: Session = Depends(get_db)
):
    """
    Рассчитать несколько индикаторов одновременно

    Args:
        requests: Список параметров расчёта

    Returns:
        List[IndicatorCalculateResponse]: Результаты расчёта для каждого индикатора

    Raises:
        HTTPException: 400 если слишком много индикаторов (лимит 10)
    """
    if len(requests) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 indicators can be calculated at once"
        )

    logger.info(f"Calculating {len(requests)} indicators")

    results = []
    for req in requests:
        try:
            result = calculate_indicator(req, db)
            results.append(result)
        except HTTPException:
            # Пропускаем индикаторы с ошибками
            logger.warning(f"Skipping indicator {req.indicator_name} due to error")
            continue

    return results


@router.get("/stats/usage")
def get_indicators_stats():
    """
    Получить статистику по индикаторам

    Returns:
        dict: Статистика (количество по категориям)
    """
    all_indicators = IndicatorRegistry.get_all()

    stats: Dict[str, Any] = {
        "total": len(all_indicators),
        "by_category": {}
    }

    # Подсчёт по категориям
    for indicator_class in all_indicators.values():
        category = indicator_class.category
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

    # Список всех названий
    stats["available_indicators"] = IndicatorRegistry.list_names()

    logger.debug(f"Indicators stats: {stats['total']} total")

    return stats
