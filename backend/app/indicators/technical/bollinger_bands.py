"""
Bollinger Bands - Полосы Боллинджера
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class BollingerBands(BaseIndicator):
    """
    Полосы Боллинджера

    Состоит из трёх линий:
    - Middle Band: SMA(period)
    - Upper Band: Middle Band + (std_dev * стандартное отклонение)
    - Lower Band: Middle Band - (std_dev * стандартное отклонение)

    Используется для:
    - Определения волатильности
    - Выявления перекупленности/перепроданности
    - Определения ценовых каналов
    """

    name = "BBands"
    category = "volatility"
    description = "Bollinger Bands - полосы Боллинджера"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="period",
                type="int",
                default=20,
                min_value=2,
                max_value=200,
                description="Период скользящей средней"
            ),
            IndicatorParameter(
                name="std_dev",
                type="float",
                default=2.0,
                min_value=0.1,
                max_value=5.0,
                description="Количество стандартных отклонений"
            ),
            IndicatorParameter(
                name="source",
                type="str",
                default="close",
                description="Источник данных (open, high, low, close)"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Расчёт Bollinger Bands

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.DataFrame: Три колонки - upper, middle, lower
        """
        self._validate_data(data)

        period = self.parameters["period"]
        std_dev = self.parameters["std_dev"]
        source = self.parameters["source"]

        if source not in data.columns:
            raise ValueError(f"Invalid source column: {source}")

        # Middle Band (SMA)
        middle = data[source].rolling(window=period).mean()

        # Стандартное отклонение
        std = data[source].rolling(window=period).std()

        # Upper и Lower Bands
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)

        # Результат
        result = pd.DataFrame({
            "upper": upper,
            "middle": middle,
            "lower": lower
        }, index=data.index)

        return result
