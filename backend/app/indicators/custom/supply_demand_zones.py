"""
Индикатор зон спроса и предложения (Supply & Demand Zones)
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator
from app.indicators.result_types import IndicatorResult, Shape, ShapeType


@register_indicator
class SupplyDemandZones(BaseIndicator):
    """
    Индикатор зон спроса и предложения

    Определяет зоны на основе паттернов:
    - Rally-Base-Rally (RBR) - зона спроса (demand)
    - Drop-Base-Drop (DBD) - зона предложения (supply)
    - Rally-Base-Drop (RBD) - зона предложения (supply)
    - Drop-Base-Rally (DBR) - зона спроса (demand)

    Возвращает прямоугольные зоны с координатами и метаданными.
    """

    name = "SupplyDemandZones"
    category = "custom"
    description = "Определение зон спроса и предложения"

    def __init__(
        self,
        timeframe: str = "1d",
        **parameters
    ):
        super().__init__(timeframe=timeframe, **parameters)

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        """Схема параметров индикатора"""
        return [
            IndicatorParameter(
                name="swing_strength",
                type="int",
                default=5,
                min_value=3,
                max_value=10,
                description="Количество свечей для определения swing high/low"
            ),
            IndicatorParameter(
                name="base_tolerance",
                type="float",
                default=0.01,
                min_value=0.005,
                max_value=0.05,
                description="Допустимое отклонение для определения базы (% от цены)"
            ),
            IndicatorParameter(
                name="min_zone_strength",
                type="float",
                default=0.015,
                min_value=0.01,
                max_value=0.1,
                description="Минимальная сила зоны (% движения от базы)"
            ),
            IndicatorParameter(
                name="max_zones",
                type="int",
                default=10,
                min_value=5,
                max_value=50,
                description="Максимальное количество зон для отображения"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """
        Расчёт зон спроса и предложения

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            IndicatorResult с геометрическими фигурами (зонами)
        """
        self._validate_data(data)

        if len(data) < 20:
            return IndicatorResult.from_shapes(
                shapes=[],
                metadata={"zones_found": 0}
            )

        # Параметры
        swing_strength = self.parameters["swing_strength"]
        base_tolerance = self.parameters["base_tolerance"]
        min_zone_strength = self.parameters["min_zone_strength"]
        max_zones = self.parameters["max_zones"]

        # Найти swing highs и lows
        df = data.copy()
        df["swing_high"] = False
        df["swing_low"] = False

        for i in range(swing_strength, len(df) - swing_strength):
            # Swing High - максимум выше всех соседей
            if df["high"].iloc[i] == df["high"].iloc[i-swing_strength:i+swing_strength+1].max():
                df.iloc[i, df.columns.get_loc("swing_high")] = True

            # Swing Low - минимум ниже всех соседей
            if df["low"].iloc[i] == df["low"].iloc[i-swing_strength:i+swing_strength+1].min():
                df.iloc[i, df.columns.get_loc("swing_low")] = True

        zones: List[Shape] = []

        # Поиск паттернов зон
        swing_points = []
        for i in range(len(df)):
            if df["swing_high"].iloc[i]:
                swing_points.append((i, "high", df["high"].iloc[i]))
            elif df["swing_low"].iloc[i]:
                swing_points.append((i, "low", df["low"].iloc[i]))

        # Анализ последовательностей swing points для паттернов
        for i in range(2, len(swing_points)):
            idx1, type1, price1 = swing_points[i-2]
            idx2, type2, price2 = swing_points[i-1]
            idx3, type3, price3 = swing_points[i]

            # Rally-Base-Rally (RBR) - зона спроса
            if type1 == "low" and type2 == "low" and type3 == "high":
                # Проверка что база достаточно плоская
                base_range = abs(price2 - price1) / price1
                if base_range < base_tolerance:
                    # Проверка силы движения от зоны
                    rally_strength = (price3 - price2) / price2
                    if rally_strength > min_zone_strength:
                        zones.append(self._create_zone(
                            df=df,
                            start_idx=idx1,
                            end_idx=idx2,
                            zone_type="demand",
                            label="RBR Demand",
                            strength=rally_strength
                        ))

            # Drop-Base-Drop (DBD) - зона предложения
            if type1 == "high" and type2 == "high" and type3 == "low":
                # Проверка базы
                base_range = abs(price2 - price1) / price1
                if base_range < base_tolerance:
                    # Проверка силы движения
                    drop_strength = (price2 - price3) / price2
                    if drop_strength > min_zone_strength:
                        zones.append(self._create_zone(
                            df=df,
                            start_idx=idx1,
                            end_idx=idx2,
                            zone_type="supply",
                            label="DBD Supply",
                            strength=drop_strength
                        ))

            # Rally-Base-Drop (RBD) - зона предложения
            if type1 == "low" and type2 == "high" and type3 == "low":
                # Проверка что цена развернулась от зоны
                drop_strength = (price2 - price3) / price2
                if drop_strength > min_zone_strength:
                    zones.append(self._create_zone(
                        df=df,
                        start_idx=idx2 - swing_strength,
                        end_idx=idx2,
                        zone_type="supply",
                        label="RBD Supply",
                        strength=drop_strength
                    ))

            # Drop-Base-Rally (DBR) - зона спроса
            if type1 == "high" and type2 == "low" and type3 == "high":
                # Проверка движения от зоны
                rally_strength = (price3 - price2) / price2
                if rally_strength > min_zone_strength:
                    zones.append(self._create_zone(
                        df=df,
                        start_idx=idx2 - swing_strength,
                        end_idx=idx2,
                        zone_type="demand",
                        label="DBR Demand",
                        strength=rally_strength
                    ))

        # Сортировка зон по силе и отбор лучших
        zones_sorted = sorted(
            zones,
            key=lambda z: z.metadata.get("strength", 0),
            reverse=True
        )
        zones_final = zones_sorted[:max_zones]

        return IndicatorResult.from_shapes(
            shapes=zones_final,
            metadata={
                "zones_found": len(zones_final),
                "demand_zones": len([z for z in zones_final if z.metadata.get("zone_type") == "demand"]),
                "supply_zones": len([z for z in zones_final if z.metadata.get("zone_type") == "supply"]),
                "timeframe": self.timeframe
            }
        )

    def _create_zone(
        self,
        df: pd.DataFrame,
        start_idx: int,
        end_idx: int,
        zone_type: str,
        label: str,
        strength: float
    ) -> Shape:
        """
        Создать зону

        Args:
            df: DataFrame с данными
            start_idx: Индекс начала зоны
            end_idx: Индекс конца зоны
            zone_type: Тип зоны (demand/supply)
            label: Метка зоны
            strength: Сила зоны (% движения)

        Returns:
            Shape объект
        """
        # Определить границы зоны по ценам
        zone_data = df.iloc[start_idx:end_idx+1]
        price_low = zone_data["low"].min()
        price_high = zone_data["high"].max()

        # Расширить зону до текущего времени (или ограничить)
        start_time = df.index[start_idx]
        # Зона "активна" до текущего момента, но можно ограничить
        end_time = df.index[-1]

        # Цвет зоны
        color = "#4CAF50" if zone_type == "demand" else "#F44336"  # Зеленый/Красный

        return Shape(
            shape_type=ShapeType.ZONE,
            start_time=start_time,
            end_time=end_time,
            price_low=price_low,
            price_high=price_high,
            label=label,
            color=color,
            metadata={
                "zone_type": zone_type,
                "strength": round(strength, 4),
                "strength_pct": f"{round(strength * 100, 2)}%",
                "zone_height": round(price_high - price_low, 2),
                "zone_height_pct": f"{round((price_high - price_low) / price_low * 100, 2)}%"
            }
        )
