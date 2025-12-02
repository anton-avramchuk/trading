"""
Market Regime - Определение режима рынка
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class MarketRegime(BaseIndicator):
    """
    Определение режима рынка

    Классифицирует рынок на:
    - Trending (тренд): сильное направленное движение
    - Ranging (флэт): боковое движение
    - Volatile (волатильный): высокая волатильность без тренда

    Использует:
    - ADX для определения силы тренда
    - ATR для волатильности
    - Линейная регрессия для направления
    """

    name = "MarketRegime"
    category = "custom"
    description = "Market Regime Detection - определение режима рынка"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="period",
                type="int",
                default=20,
                min_value=5,
                max_value=100,
                description="Период для анализа"
            ),
            IndicatorParameter(
                name="adx_threshold",
                type="float",
                default=25.0,
                min_value=10.0,
                max_value=50.0,
                description="Порог ADX для тренда"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Расчёт режима рынка

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.Series: Режим рынка ('trending', 'ranging', 'volatile')
        """
        self._validate_data(data)

        period = self.parameters["period"]
        adx_threshold = self.parameters["adx_threshold"]

        # Расчёт ADX для определения силы тренда
        adx = self._calculate_adx(data, period)

        # Расчёт ATR для волатильности
        atr = self._calculate_atr(data, period)

        # Нормализованная волатильность (ATR / Close)
        normalized_volatility = (atr / data["close"]) * 100

        # Определение режима
        regime = pd.Series(index=data.index, dtype=str)

        # Тренд: высокий ADX
        trending_mask = adx > adx_threshold
        regime[trending_mask] = "trending"

        # Флэт: низкий ADX и умеренная волатильность
        ranging_mask = (adx <= adx_threshold) & (normalized_volatility < normalized_volatility.rolling(50).mean())
        regime[ranging_mask] = "ranging"

        # Волатильный: низкий ADX но высокая волатильность
        volatile_mask = (adx <= adx_threshold) & (normalized_volatility >= normalized_volatility.rolling(50).mean())
        regime[volatile_mask] = "volatile"

        # Заполнение начальных NaN
        regime = regime.fillna("ranging")

        return regime

    def _calculate_adx(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Расчёт ADX"""
        prev_close = data["close"].shift(1)
        tr1 = data["high"] - data["low"]
        tr2 = (data["high"] - prev_close).abs()
        tr3 = (data["low"] - prev_close).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        prev_high = data["high"].shift(1)
        prev_low = data["low"].shift(1)

        plus_dm = data["high"] - prev_high
        minus_dm = prev_low - data["low"]

        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

        atr = true_range.ewm(span=period, adjust=False).mean()
        plus_dm_smooth = plus_dm.ewm(span=period, adjust=False).mean()
        minus_dm_smooth = minus_dm.ewm(span=period, adjust=False).mean()

        plus_di = 100 * (plus_dm_smooth / atr)
        minus_di = 100 * (minus_dm_smooth / atr)

        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
        adx = dx.ewm(span=period, adjust=False).mean()

        return adx

    def _calculate_atr(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Расчёт ATR"""
        prev_close = data["close"].shift(1)
        tr1 = data["high"] - data["low"]
        tr2 = (data["high"] - prev_close).abs()
        tr3 = (data["low"] - prev_close).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.ewm(span=period, adjust=False).mean()
        return atr
