"""
Support/Resistance - Уровни поддержки и сопротивления
"""
from typing import List

import pandas as pd
import numpy as np

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class SupportResistance(BaseIndicator):
    """
    Определение уровней поддержки и сопротивления

    Находит значимые уровни цен где:
    - Support (поддержка): уровень где цена останавливается при падении
    - Resistance (сопротивление): уровень где цена останавливается при росте

    Метод: поиск локальных минимумов (support) и максимумов (resistance)
    с кластеризацией близких уровней.
    """

    name = "SupportResistance"
    category = "custom"
    description = "Support/Resistance Levels - уровни поддержки и сопротивления"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="window",
                type="int",
                default=10,
                min_value=3,
                max_value=50,
                description="Окно для поиска локальных экстремумов"
            ),
            IndicatorParameter(
                name="num_levels",
                type="int",
                default=3,
                min_value=1,
                max_value=10,
                description="Количество уровней для каждого типа"
            ),
            IndicatorParameter(
                name="tolerance",
                type="float",
                default=0.02,
                min_value=0.001,
                max_value=0.1,
                description="Толерантность для кластеризации (в процентах)"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Расчёт уровней поддержки и сопротивления

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.DataFrame: Колонки support_1, support_2, support_3,
                         resistance_1, resistance_2, resistance_3
                         (количество зависит от num_levels)
        """
        self._validate_data(data)

        window = self.parameters["window"]
        num_levels = self.parameters["num_levels"]
        tolerance = self.parameters["tolerance"]

        # Поиск локальных минимумов (support)
        local_mins = self._find_local_extrema(data["low"], window, "min")

        # Поиск локальных максимумов (resistance)
        local_maxs = self._find_local_extrema(data["high"], window, "max")

        # Кластеризация уровней
        support_levels = self._cluster_levels(local_mins, tolerance, num_levels)
        resistance_levels = self._cluster_levels(local_maxs, tolerance, num_levels)

        # Создание результата
        result = pd.DataFrame(index=data.index)

        # Добавление уровней поддержки
        for i, level in enumerate(support_levels, 1):
            result[f"support_{i}"] = level

        # Добавление уровней сопротивления
        for i, level in enumerate(resistance_levels, 1):
            result[f"resistance_{i}"] = level

        # Заполнение пропущенных уровней (если меньше num_levels)
        for i in range(len(support_levels) + 1, num_levels + 1):
            result[f"support_{i}"] = np.nan

        for i in range(len(resistance_levels) + 1, num_levels + 1):
            result[f"resistance_{i}"] = np.nan

        return result

    def _find_local_extrema(
        self,
        series: pd.Series,
        window: int,
        extrema_type: str
    ) -> List[float]:
        """
        Поиск локальных экстремумов

        Args:
            series: Серия данных
            window: Окно для поиска
            extrema_type: 'min' или 'max'

        Returns:
            List[float]: Значения локальных экстремумов
        """
        extrema = []

        for i in range(window, len(series) - window):
            window_data = series.iloc[i - window:i + window + 1]

            if extrema_type == "min":
                if series.iloc[i] == window_data.min():
                    extrema.append(series.iloc[i])
            else:  # max
                if series.iloc[i] == window_data.max():
                    extrema.append(series.iloc[i])

        return extrema

    def _cluster_levels(
        self,
        levels: List[float],
        tolerance: float,
        num_clusters: int
    ) -> List[float]:
        """
        Кластеризация близких уровней

        Args:
            levels: Список уровней
            tolerance: Толерантность (в процентах)
            num_clusters: Количество кластеров

        Returns:
            List[float]: Средние значения кластеров
        """
        if not levels:
            return []

        levels = sorted(levels)
        clusters = []
        current_cluster = [levels[0]]

        for level in levels[1:]:
            # Проверка, находится ли уровень в пределах толерантности
            cluster_mean = np.mean(current_cluster)
            relative_diff = abs(level - cluster_mean) / cluster_mean

            if relative_diff <= tolerance:
                current_cluster.append(level)
            else:
                # Сохранить текущий кластер и начать новый
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]

        # Добавить последний кластер
        if current_cluster:
            clusters.append(np.mean(current_cluster))

        # Отсортировать кластеры по частоте касаний (количество уровней в кластере)
        # Здесь упрощение: просто берём первые num_clusters
        return clusters[:num_clusters]
