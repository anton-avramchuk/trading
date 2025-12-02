"""
Базовый класс для всех индикаторов
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field

from app.indicators.result_types import IndicatorResult


class IndicatorParameter(BaseModel):
    """Описание параметра индикатора"""
    name: str = Field(..., description="Название параметра")
    type: str = Field(..., description="Тип параметра (int, float, str)")
    default: Any = Field(..., description="Значение по умолчанию")
    min_value: Optional[float] = Field(None, description="Минимальное значение")
    max_value: Optional[float] = Field(None, description="Максимальное значение")
    description: Optional[str] = Field(None, description="Описание параметра")


class BaseIndicator(ABC):
    """
    Базовый класс для всех индикаторов

    Attributes:
        name: Название индикатора (уникальное)
        category: Категория (trend, momentum, volatility, volume, custom)
        description: Описание индикатора
        timeframe: Таймфрейм для расчёта
        parameters: Параметры индикатора
    """

    # Метаданные индикатора (должны быть переопределены в наследниках)
    name: str = "BaseIndicator"
    category: str = "base"
    description: str = "Base indicator class"

    def __init__(
        self,
        timeframe: str = "1d",
        **parameters: Any
    ):
        """
        Инициализация индикатора

        Args:
            timeframe: Таймфрейм для расчёта
            **parameters: Параметры индикатора
        """
        self.timeframe = timeframe
        self.parameters = parameters

        # Валидация параметров
        self._validate_parameters()

    @classmethod
    @abstractmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        """
        Получить схему параметров индикатора

        Returns:
            List[IndicatorParameter]: Список описаний параметров
        """
        pass

    @abstractmethod
    def calculate(
        self,
        data: pd.DataFrame
    ) -> Union[pd.Series, pd.DataFrame, IndicatorResult]:
        """
        Расчёт индикатора

        Args:
            data: DataFrame с OHLCV данными (индекс - timestamp)
                  Колонки: open, high, low, close, volume

        Returns:
            Результат расчёта индикатора (3 варианта):
            - pd.Series: для простых индикаторов (MA, RSI)
            - pd.DataFrame: для сложных индикаторов (MACD, Bollinger Bands)
            - IndicatorResult: для дискретных точек и фигур

        Raises:
            ValueError: Если данные некорректны
        """
        pass

    def normalize_result(
        self,
        result: Union[pd.Series, pd.DataFrame, IndicatorResult]
    ) -> IndicatorResult:
        """
        Нормализация результата в IndicatorResult

        Обеспечивает обратную совместимость для старых индикаторов.

        Args:
            result: Результат calculate()

        Returns:
            IndicatorResult: Нормализованный результат
        """
        if isinstance(result, IndicatorResult):
            return result
        elif isinstance(result, (pd.Series, pd.DataFrame)):
            return IndicatorResult.from_continuous(result)
        else:
            raise TypeError(
                f"Invalid result type: {type(result)}. "
                f"Expected Series, DataFrame, or IndicatorResult"
            )

    def _validate_parameters(self) -> None:
        """
        Валидация параметров индикатора

        Raises:
            ValueError: Если параметры некорректны
        """
        schema = self.get_parameters_schema()

        for param_schema in schema:
            param_name = param_schema.name

            # Проверка наличия обязательного параметра
            if param_name not in self.parameters:
                # Использовать значение по умолчанию
                self.parameters[param_name] = param_schema.default

            value = self.parameters[param_name]

            # Проверка типа
            expected_type = param_schema.type
            if expected_type == "int" and not isinstance(value, int):
                raise ValueError(
                    f"Parameter '{param_name}' must be int, got {type(value)}"
                )
            elif expected_type == "float" and not isinstance(value, (int, float)):
                raise ValueError(
                    f"Parameter '{param_name}' must be float, got {type(value)}"
                )
            elif expected_type == "str" and not isinstance(value, str):
                raise ValueError(
                    f"Parameter '{param_name}' must be str, got {type(value)}"
                )

            # Проверка диапазона (для числовых параметров)
            if param_schema.min_value is not None and value < param_schema.min_value:
                raise ValueError(
                    f"Parameter '{param_name}' must be >= {param_schema.min_value}, got {value}"
                )

            if param_schema.max_value is not None and value > param_schema.max_value:
                raise ValueError(
                    f"Parameter '{param_name}' must be <= {param_schema.max_value}, got {value}"
                )

    def _validate_data(self, data: pd.DataFrame) -> None:
        """
        Валидация входных данных

        Args:
            data: DataFrame с OHLCV данными

        Raises:
            ValueError: Если данные некорректны
        """
        required_columns = ["open", "high", "low", "close", "volume"]

        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col}")

        if data.empty:
            raise ValueError("Data is empty")

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data index must be DatetimeIndex")

    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        """
        Получить информацию об индикаторе

        Returns:
            dict: Метаданные индикатора
        """
        return {
            "name": cls.name,
            "category": cls.category,
            "description": cls.description,
            "parameters": [
                param.model_dump() for param in cls.get_parameters_schema()
            ]
        }

    def __repr__(self) -> str:
        """Строковое представление индикатора"""
        params_str = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"{self.name}(timeframe={self.timeframe}, {params_str})"

    def __str__(self) -> str:
        """Строковое представление индикатора"""
        return self.__repr__()


class IndicatorError(Exception):
    """Ошибка при расчёте индикатора"""
    pass
