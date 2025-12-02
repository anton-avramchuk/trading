"""
Менеджер для работы с множественными таймфреймами
"""
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from app.utils.timeframe_utils import TimeframeUtils


class TimeframeManager:
    """
    Менеджер для выравнивания и работы с данными разных таймфреймов

    Используется для стратегий, которые используют индикаторы
    с разных таймфреймов одновременно.
    """

    @staticmethod
    def align_timeframes(
        data_dict: Dict[str, pd.DataFrame],
        base_timeframe: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Выравнивание данных разных таймфреймов

        Приводит все данные к единому временному индексу базового таймфрейма.
        Для более высоких таймфреймов используется forward fill.

        Args:
            data_dict: Словарь {timeframe: DataFrame с OHLCV}
            base_timeframe: Базовый таймфрейм (самый низкий).
                          Если None - автоматически определяется как минимальный.

        Returns:
            Dict[str, pd.DataFrame]: Выровненные данные

        Raises:
            ValueError: Если данные пустые или некорректные
        """
        if not data_dict:
            raise ValueError("data_dict is empty")

        # Определение базового таймфрейма
        if base_timeframe is None:
            timeframes = list(data_dict.keys())
            base_timeframe = TimeframeUtils.sort_timeframes(timeframes)[0]

        logger.debug(
            f"Aligning timeframes to base: {base_timeframe}. "
            f"Timeframes: {list(data_dict.keys())}"
        )

        # Проверка наличия базового таймфрейма
        if base_timeframe not in data_dict:
            raise ValueError(f"Base timeframe {base_timeframe} not found in data_dict")

        base_data = data_dict[base_timeframe]
        if base_data.empty:
            raise ValueError(f"Base timeframe {base_timeframe} data is empty")

        # Базовый индекс времени
        base_index = base_data.index

        # Результат
        aligned_dict = {}

        for tf, df in data_dict.items():
            if df.empty:
                logger.warning(f"Timeframe {tf} data is empty, skipping")
                continue

            if tf == base_timeframe:
                # Базовый таймфрейм - оставляем как есть
                aligned_dict[tf] = df.copy()
            else:
                # Более высокий таймфрейм - выравниваем
                aligned_df = TimeframeManager._align_to_base_index(
                    df, base_index, tf, base_timeframe
                )
                aligned_dict[tf] = aligned_df

        logger.debug(f"Aligned {len(aligned_dict)} timeframes")
        return aligned_dict

    @staticmethod
    def _align_to_base_index(
        df: pd.DataFrame,
        base_index: pd.DatetimeIndex,
        source_tf: str,
        base_tf: str
    ) -> pd.DataFrame:
        """
        Выравнивание DataFrame к базовому индексу

        Args:
            df: DataFrame для выравнивания
            base_index: Базовый временной индекс
            source_tf: Таймфрейм источника
            base_tf: Базовый таймфрейм

        Returns:
            pd.DataFrame: Выровненный DataFrame
        """
        # Reindex с forward fill для более высоких таймфреймов
        aligned_df = df.reindex(base_index, method='ffill')

        # Удаление строк до первого валидного значения
        aligned_df = aligned_df.dropna(how='all')

        return aligned_df

    @staticmethod
    def get_higher_timeframe_value(
        data: pd.DataFrame,
        current_time: datetime,
        column: str = "close"
    ) -> Optional[float]:
        """
        Получить значение с более высокого таймфрейма для текущего времени

        Args:
            data: DataFrame с данными более высокого таймфрейма
            current_time: Текущее время
            column: Колонка для получения значения

        Returns:
            float: Значение или None если не найдено
        """
        if data.empty:
            return None

        # Поиск ближайшего значения (на или до current_time)
        mask = data.index <= current_time
        filtered = data[mask]

        if filtered.empty:
            return None

        # Последнее доступное значение
        return filtered[column].iloc[-1]

    @staticmethod
    def resample_ohlcv(
        data: pd.DataFrame,
        source_tf: str,
        target_tf: str
    ) -> pd.DataFrame:
        """
        Ресемплинг OHLCV данных на другой таймфрейм

        Args:
            data: DataFrame с OHLCV данными
            source_tf: Исходный таймфрейм
            target_tf: Целевой таймфрейм

        Returns:
            pd.DataFrame: Ресемплированные данные

        Raises:
            ValueError: Если ресемплинг невозможен
        """
        if not TimeframeUtils.can_resample(source_tf, target_tf):
            raise ValueError(
                f"Cannot resample from {source_tf} to {target_tf}. "
                f"Target must be higher than source."
            )

        logger.debug(f"Resampling {source_tf} -> {target_tf}")

        target_offset = TimeframeUtils.get_timeframe_offset(target_tf)

        # Ресемплинг OHLCV
        resampled = data.resample(target_offset).agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        })

        # Удаление NaN (неполные свечи)
        resampled = resampled.dropna()

        logger.debug(f"Resampled: {len(data)} -> {len(resampled)} rows")
        return resampled

    @staticmethod
    def validate_multi_timeframe_data(
        data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, List[str]]:
        """
        Валидация данных множественных таймфреймов

        Args:
            data_dict: Словарь {timeframe: DataFrame}

        Returns:
            Dict[str, List[str]]: Словарь с ошибками/предупреждениями
        """
        issues = {
            "errors": [],
            "warnings": []
        }

        if not data_dict:
            issues["errors"].append("data_dict is empty")
            return issues

        # Проверка таймфреймов
        for tf in data_dict.keys():
            if not TimeframeUtils.validate_timeframe(tf):
                issues["errors"].append(f"Invalid timeframe: {tf}")

        # Проверка данных
        for tf, df in data_dict.items():
            if df.empty:
                issues["warnings"].append(f"Timeframe {tf} has no data")

            # Проверка обязательных колонок
            required_columns = ["open", "high", "low", "close", "volume"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                issues["errors"].append(
                    f"Timeframe {tf} missing columns: {missing_columns}"
                )

        return issues

    @staticmethod
    def get_synchronized_timestamps(
        data_dict: Dict[str, pd.DataFrame]
    ) -> pd.DatetimeIndex:
        """
        Получить синхронизированные временные метки

        Возвращает временные метки, которые присутствуют во всех таймфреймах
        (с учётом forward fill для более высоких таймфреймов).

        Args:
            data_dict: Словарь {timeframe: DataFrame}

        Returns:
            pd.DatetimeIndex: Синхронизированные временные метки
        """
        if not data_dict:
            return pd.DatetimeIndex([])

        # Сортировка таймфреймов от низкого к высокому
        sorted_tfs = TimeframeUtils.sort_timeframes(list(data_dict.keys()))

        # Базовый таймфрейм (самый низкий)
        base_tf = sorted_tfs[0]
        base_index = data_dict[base_tf].index

        # Проверка, что все более высокие таймфреймы покрывают этот период
        synchronized_index = base_index

        for tf in sorted_tfs[1:]:
            tf_data = data_dict[tf]
            if tf_data.empty:
                continue

            # Первая и последняя метка более высокого таймфрейма
            tf_start = tf_data.index.min()
            tf_end = tf_data.index.max()

            # Фильтрация базового индекса
            mask = (synchronized_index >= tf_start) & (synchronized_index <= tf_end)
            synchronized_index = synchronized_index[mask]

        return synchronized_index

    @staticmethod
    def merge_multi_timeframe_indicators(
        indicators_dict: Dict[str, Dict[str, pd.Series]],
        base_timeframe: str
    ) -> pd.DataFrame:
        """
        Объединение индикаторов с разных таймфреймов в один DataFrame

        Args:
            indicators_dict: Словарь {timeframe: {indicator_name: Series}}
            base_timeframe: Базовый таймфрейм

        Returns:
            pd.DataFrame: Объединённые индикаторы с префиксами таймфреймов

        Example:
            {
                "1h": {"rsi": Series, "ma": Series},
                "1d": {"rsi": Series, "ma": Series}
            }
            ->
            DataFrame with columns: ["1h_rsi", "1h_ma", "1d_rsi", "1d_ma"]
        """
        if not indicators_dict:
            return pd.DataFrame()

        # Базовый индекс
        if base_timeframe not in indicators_dict:
            raise ValueError(f"Base timeframe {base_timeframe} not found")

        # Получаем базовый индекс из первого индикатора
        base_indicator = next(iter(indicators_dict[base_timeframe].values()))
        result_df = pd.DataFrame(index=base_indicator.index)

        # Добавление индикаторов с каждого таймфрейма
        for tf, indicators in indicators_dict.items():
            for indicator_name, indicator_series in indicators.items():
                # Название колонки: timeframe_indicator
                column_name = f"{tf}_{indicator_name}"

                if tf == base_timeframe:
                    result_df[column_name] = indicator_series
                else:
                    # Forward fill для более высоких таймфреймов
                    aligned_series = indicator_series.reindex(
                        result_df.index,
                        method='ffill'
                    )
                    result_df[column_name] = aligned_series

        return result_df
