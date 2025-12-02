"""
ADX (Average Directional Index) - Индекс среднего направленного движения
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class ADX(BaseIndicator):
    """
    Индекс среднего направленного движения (ADX)

    Измеряет силу тренда (не направление).
    Диапазон: 0-100

    - ADX < 20: слабый тренд или боковое движение
    - ADX 20-40: развивающийся тренд
    - ADX > 40: сильный тренд

    Также возвращает:
    - +DI (Positive Directional Indicator)
    - -DI (Negative Directional Indicator)
    """

    name = "ADX"
    category = "trend"
    description = "Average Directional Index - индекс среднего направленного движения"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="period",
                type="int",
                default=14,
                min_value=1,
                max_value=100,
                description="Период ADX"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Расчёт ADX

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.DataFrame: Три колонки - adx, plus_di, minus_di
        """
        self._validate_data(data)

        period = self.parameters["period"]

        # Расчёт True Range
        prev_close = data["close"].shift(1)
        tr1 = data["high"] - data["low"]
        tr2 = (data["high"] - prev_close).abs()
        tr3 = (data["low"] - prev_close).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Directional Movement
        prev_high = data["high"].shift(1)
        prev_low = data["low"].shift(1)

        plus_dm = data["high"] - prev_high
        minus_dm = prev_low - data["low"]

        # Условия для DM
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

        # Сглаженный True Range и DM
        atr = true_range.ewm(span=period, adjust=False).mean()
        plus_dm_smooth = plus_dm.ewm(span=period, adjust=False).mean()
        minus_dm_smooth = minus_dm.ewm(span=period, adjust=False).mean()

        # Directional Indicators
        plus_di = 100 * (plus_dm_smooth / atr)
        minus_di = 100 * (minus_dm_smooth / atr)

        # DX (Directional Index)
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))

        # ADX (сглаженный DX)
        adx = dx.ewm(span=period, adjust=False).mean()

        # Результат
        result = pd.DataFrame({
            "adx": adx,
            "plus_di": plus_di,
            "minus_di": minus_di
        }, index=data.index)

        return result
