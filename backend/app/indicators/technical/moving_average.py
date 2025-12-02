"""
Moving Average (MA) - Скользящая средняя
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class MovingAverage(BaseIndicator):
    """
    Скользящая средняя (Simple Moving Average)

    Простая скользящая средняя - среднее значение цены за N периодов.
    Используется для определения тренда и уровней поддержки/сопротивления.
    """

    name = "MA"
    category = "trend"
    description = "Simple Moving Average - простая скользящая средняя"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="period",
                type="int",
                default=20,
                min_value=1,
                max_value=500,
                description="Период скользящей средней"
            ),
            IndicatorParameter(
                name="source",
                type="str",
                default="close",
                description="Источник данных (open, high, low, close)"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Расчёт скользящей средней

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.Series: Значения MA
        """
        self._validate_data(data)

        period = self.parameters["period"]
        source = self.parameters["source"]

        if source not in data.columns:
            raise ValueError(f"Invalid source column: {source}")

        # Расчёт простой скользящей средней
        ma = data[source].rolling(window=period).mean()

        return ma


@register_indicator
class ExponentialMovingAverage(BaseIndicator):
    """
    Экспоненциальная скользящая средняя (EMA)

    EMA придаёт больший вес последним ценам.
    Более чувствительна к изменениям цены, чем SMA.
    """

    name = "EMA"
    category = "trend"
    description = "Exponential Moving Average - экспоненциальная скользящая средняя"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="period",
                type="int",
                default=20,
                min_value=1,
                max_value=500,
                description="Период EMA"
            ),
            IndicatorParameter(
                name="source",
                type="str",
                default="close",
                description="Источник данных (open, high, low, close)"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Расчёт EMA

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.Series: Значения EMA
        """
        self._validate_data(data)

        period = self.parameters["period"]
        source = self.parameters["source"]

        if source not in data.columns:
            raise ValueError(f"Invalid source column: {source}")

        # Расчёт экспоненциальной скользящей средней
        ema = data[source].ewm(span=period, adjust=False).mean()

        return ema
