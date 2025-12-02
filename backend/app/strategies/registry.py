"""
Реестр стратегий
"""
from typing import Any, Dict, List, Type

from loguru import logger

from app.strategies.base import BaseStrategy


class StrategyRegistry:
    """Реестр всех доступных торговых стратегий"""

    _strategies: Dict[str, Type[BaseStrategy]] = {}

    @classmethod
    def register(cls, strategy_class: Type[BaseStrategy]) -> None:
        """
        Зарегистрировать стратегию

        Args:
            strategy_class: Класс стратегии

        Raises:
            ValueError: Если стратегия с таким именем уже зарегистрирована
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(
                f"{strategy_class.__name__} must inherit from BaseStrategy"
            )

        name = strategy_class.name

        if name in cls._strategies:
            logger.warning(
                f"Strategy '{name}' is already registered. Overwriting."
            )

        cls._strategies[name] = strategy_class
        logger.debug(f"Registered strategy: {name}")

    @classmethod
    def get(cls, name: str) -> Type[BaseStrategy] | None:
        """
        Получить класс стратегии по имени

        Args:
            name: Название стратегии

        Returns:
            Класс стратегии или None если не найдена
        """
        return cls._strategies.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, Type[BaseStrategy]]:
        """
        Получить все зарегистрированные стратегии

        Returns:
            Dict[str, Type[BaseStrategy]]: Словарь {name: strategy_class}
        """
        return cls._strategies.copy()

    @classmethod
    def list_names(cls) -> List[str]:
        """
        Получить список названий всех стратегий

        Returns:
            List[str]: Список названий
        """
        return list(cls._strategies.keys())

    @classmethod
    def get_info(cls, name: str) -> Dict[str, Any] | None:
        """
        Получить информацию о стратегии

        Args:
            name: Название стратегии

        Returns:
            dict: Метаданные стратегии или None если не найдена
        """
        strategy_class = cls.get(name)
        if strategy_class is None:
            return None

        return strategy_class.get_info()

    @classmethod
    def get_all_info(cls) -> List[Dict[str, Any]]:
        """
        Получить информацию о всех стратегиях

        Returns:
            List[dict]: Список метаданных всех стратегий
        """
        return [
            strategy_class.get_info()
            for strategy_class in cls._strategies.values()
        ]

    @classmethod
    def create_strategy(
        cls,
        name: str,
        **parameters: Any
    ) -> BaseStrategy:
        """
        Создать экземпляр стратегии

        Args:
            name: Название стратегии
            **parameters: Параметры стратегии

        Returns:
            BaseStrategy: Экземпляр стратегии

        Raises:
            ValueError: Если стратегия не найдена
        """
        strategy_class = cls.get(name)

        if strategy_class is None:
            raise ValueError(
                f"Strategy '{name}' not found. "
                f"Available: {', '.join(cls.list_names())}"
            )

        return strategy_class(**parameters)

    @classmethod
    def clear(cls) -> None:
        """Очистить реестр (для тестов)"""
        cls._strategies.clear()


def register_strategy(strategy_class: Type[BaseStrategy]) -> Type[BaseStrategy]:
    """
    Декоратор для автоматической регистрации стратегии

    Usage:
        @register_strategy
        class MyStrategy(BaseStrategy):
            name = "MyStrategy"
            ...

    Args:
        strategy_class: Класс стратегии

    Returns:
        Класс стратегии (неизменённый)
    """
    StrategyRegistry.register(strategy_class)
    return strategy_class
