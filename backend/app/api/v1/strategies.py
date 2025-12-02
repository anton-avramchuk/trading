"""
API endpoints для стратегий
"""
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status
from loguru import logger
from pydantic import BaseModel, Field

from app.strategies import StrategyRegistry

router = APIRouter()


class StrategyInfo(BaseModel):
    """Информация о стратегии"""
    name: str = Field(..., description="Название стратегии")
    description: str = Field(..., description="Описание стратегии")
    version: str = Field(..., description="Версия стратегии")


class StrategyListResponse(BaseModel):
    """Список стратегий"""
    total: int = Field(..., description="Общее количество стратегий")
    strategies: List[StrategyInfo] = Field(..., description="Список стратегий")


class StrategyDetailsResponse(BaseModel):
    """Детальная информация о стратегии"""
    name: str = Field(..., description="Название стратегии")
    description: str = Field(..., description="Описание")
    version: str = Field(..., description="Версия")
    required_timeframes: List[str] = Field(..., description="Необходимые таймфреймы")
    indicators_config: List[Dict[str, Any]] = Field(..., description="Конфигурация индикаторов")


@router.get("/", response_model=StrategyListResponse)
def get_strategies():
    """
    Получить список всех доступных стратегий

    Returns:
        StrategyListResponse: Список стратегий
    """
    all_strategies = StrategyRegistry.get_all_info()

    logger.info(f"Retrieved {len(all_strategies)} strategies")

    return StrategyListResponse(
        total=len(all_strategies),
        strategies=[StrategyInfo(**info) for info in all_strategies]
    )


@router.get("/{name}", response_model=StrategyInfo)
def get_strategy_info(name: str):
    """
    Получить информацию о конкретной стратегии

    Args:
        name: Название стратегии

    Returns:
        StrategyInfo: Метаданные стратегии

    Raises:
        HTTPException: 404 если стратегия не найдена
    """
    info = StrategyRegistry.get_info(name)

    if info is None:
        available = ", ".join(StrategyRegistry.list_names())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy '{name}' not found. Available: {available}"
        )

    logger.debug(f"Retrieved info for strategy: {name}")

    return StrategyInfo(**info)


@router.get("/{name}/details", response_model=StrategyDetailsResponse)
def get_strategy_details(name: str, **parameters: Any):
    """
    Получить детальную информацию о стратегии

    Включает конфигурацию индикаторов и необходимые таймфреймы.

    Args:
        name: Название стратегии
        **parameters: Параметры для создания экземпляра стратегии

    Returns:
        StrategyDetailsResponse: Детальная информация

    Raises:
        HTTPException: 404 если стратегия не найдена
        HTTPException: 400 если ошибка создания стратегии
    """
    try:
        # Создание экземпляра стратегии для получения конфигурации
        strategy = StrategyRegistry.create_strategy(name, **parameters)

        # Конвертация IndicatorConfig в dict
        indicators_config = [
            {
                "name": config.name,
                "timeframe": config.timeframe,
                "parameters": config.parameters,
                "alias": config.alias
            }
            for config in strategy.indicators_config
        ]

        logger.debug(f"Retrieved details for strategy: {name}")

        return StrategyDetailsResponse(
            name=strategy.name,
            description=strategy.description,
            version=strategy.version,
            required_timeframes=strategy.required_timeframes(),
            indicators_config=indicators_config
        )

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        logger.error(f"Error getting strategy details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting strategy details: {str(e)}"
        )


@router.get("/stats/summary")
def get_strategies_stats():
    """
    Получить статистику по стратегиям

    Returns:
        dict: Статистика (общее количество, список названий)
    """
    all_strategies = StrategyRegistry.get_all()

    stats = {
        "total": len(all_strategies),
        "available_strategies": StrategyRegistry.list_names()
    }

    logger.debug(f"Strategies stats: {stats['total']} total")

    return stats
