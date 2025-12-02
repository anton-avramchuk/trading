"""
Реестр индикаторов
"""
from typing import Any, Dict, List, Type

from loguru import logger

from app.indicators.base import BaseIndicator


class IndicatorRegistry:
    """Реестр всех доступных индикаторов"""

    _indicators: Dict[str, Type[BaseIndicator]] = {}

    @classmethod
    def register(cls, indicator_class: Type[BaseIndicator]) -> None:
        """
        Зарегистрировать индикатор

        Args:
            indicator_class: Класс индикатора

        Raises:
            ValueError: Если индикатор с таким именем уже зарегистрирован
        """
        if not issubclass(indicator_class, BaseIndicator):
            raise ValueError(
                f"{indicator_class.__name__} must inherit from BaseIndicator"
            )

        name = indicator_class.name

        if name in cls._indicators:
            logger.warning(
                f"Indicator '{name}' is already registered. Overwriting."
            )

        cls._indicators[name] = indicator_class
        logger.debug(f"Registered indicator: {name}")

    @classmethod
    def get(cls, name: str) -> Type[BaseIndicator] | None:
        """
        Получить класс индикатора по имени

        Args:
            name: Название индикатора

        Returns:
            Класс индикатора или None если не найден
        """
        return cls._indicators.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, Type[BaseIndicator]]:
        """
        Получить все зарегистрированные индикаторы

        Returns:
            Dict[str, Type[BaseIndicator]]: Словарь {name: indicator_class}
        """
        return cls._indicators.copy()

    @classmethod
    def list_names(cls) -> List[str]:
        """
        Получить список названий всех индикаторов

        Returns:
            List[str]: Список названий
        """
        return list(cls._indicators.keys())

    @classmethod
    def get_by_category(cls, category: str) -> Dict[str, Type[BaseIndicator]]:
        """
        Получить индикаторы по категории

        Args:
            category: Категория (trend, momentum, volatility, volume, custom)

        Returns:
            Dict[str, Type[BaseIndicator]]: Индикаторы данной категории
        """
        return {
            name: indicator_class
            for name, indicator_class in cls._indicators.items()
            if indicator_class.category == category
        }

    @classmethod
    def get_info(cls, name: str) -> Dict[str, Any] | None:
        """
        Получить информацию об индикаторе

        Args:
            name: Название индикатора

        Returns:
            dict: Метаданные индикатора или None если не найден
        """
        indicator_class = cls.get(name)
        if indicator_class is None:
            return None

        return indicator_class.get_info()

    @classmethod
    def get_all_info(cls) -> List[Dict[str, Any]]:
        """
        Получить информацию о всех индикаторах

        Returns:
            List[dict]: Список метаданных всех индикаторов
        """
        return [
            indicator_class.get_info()
            for indicator_class in cls._indicators.values()
        ]

    @classmethod
    def create_indicator(
        cls,
        name: str,
        timeframe: str = "1d",
        **parameters: Any
    ) -> BaseIndicator:
        """
        Создать экземпляр индикатора

        Args:
            name: Название индикатора
            timeframe: Таймфрейм
            **parameters: Параметры индикатора

        Returns:
            BaseIndicator: Экземпляр индикатора

        Raises:
            ValueError: Если индикатор не найден
        """
        indicator_class = cls.get(name)

        if indicator_class is None:
            raise ValueError(
                f"Indicator '{name}' not found. "
                f"Available: {', '.join(cls.list_names())}"
            )

        return indicator_class(timeframe=timeframe, **parameters)

    @classmethod
    def clear(cls) -> None:
        """Очистить реестр (для тестов)"""
        cls._indicators.clear()


def register_indicator(indicator_class: Type[BaseIndicator]) -> Type[BaseIndicator]:
    """
    Декоратор для автоматической регистрации индикатора

    Usage:
        @register_indicator
        class MyIndicator(BaseIndicator):
            name = "MyIndicator"
            ...

    Args:
        indicator_class: Класс индикатора

    Returns:
        Класс индикатора (неизменённый)
    """
    IndicatorRegistry.register(indicator_class)
    return indicator_class
