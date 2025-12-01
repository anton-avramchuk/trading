"""
Валидация данных OHLCV
"""
from datetime import datetime
from typing import List, Tuple

import pandas as pd
from loguru import logger


class DataValidator:
    """Класс для валидации OHLCV данных"""

    @staticmethod
    def validate_ohlc(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Валидация корректности OHLC данных

        Args:
            df: DataFrame с OHLCV данными

        Returns:
            Tuple[bool, List[str]]: (валидность, список ошибок)
        """
        errors = []

        # Проверка наличия необходимых колонок
        required_cols = ["open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            return False, errors

        # Проверка что все цены > 0
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols:
            if (df[col] <= 0).any():
                invalid_count = (df[col] <= 0).sum()
                errors.append(f"Column '{col}' has {invalid_count} non-positive values")

        # Проверка что high >= max(open, close)
        max_oc = df[["open", "close"]].max(axis=1)
        invalid_high = df[df["high"] < max_oc]
        if len(invalid_high) > 0:
            errors.append(
                f"Found {len(invalid_high)} rows where high < max(open, close)"
            )

        # Проверка что low <= min(open, close)
        min_oc = df[["open", "close"]].min(axis=1)
        invalid_low = df[df["low"] > min_oc]
        if len(invalid_low) > 0:
            errors.append(
                f"Found {len(invalid_low)} rows where low > min(open, close)"
            )

        # Проверка что volume >= 0
        if (df["volume"] < 0).any():
            invalid_count = (df["volume"] < 0).sum()
            errors.append(f"Found {invalid_count} rows with negative volume")

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def validate_timestamps(df: pd.DataFrame, timeframe: str) -> Tuple[bool, List[str]]:
        """
        Валидация временных меток

        Args:
            df: DataFrame с OHLCV данными (должен иметь datetime index)
            timeframe: Таймфрейм данных (1h, 1d, и т.д.)

        Returns:
            Tuple[bool, List[str]]: (валидность, список ошибок)
        """
        errors = []

        # Проверка что index это datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            errors.append("Index must be DatetimeIndex")
            return False, errors

        # Проверка на дубликаты
        duplicates = df.index.duplicated()
        if duplicates.any():
            duplicate_count = duplicates.sum()
            errors.append(f"Found {duplicate_count} duplicate timestamps")

        # Проверка что данные отсортированы
        if not df.index.is_monotonic_increasing:
            errors.append("Timestamps are not sorted in ascending order")

        # Проверка пропусков (опционально, можно расширить)
        # Здесь можно добавить логику проверки на пропуски в таймфрейме

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def check_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """
        Удаление дубликатов по индексу (timestamp)

        Args:
            df: DataFrame с OHLCV данными

        Returns:
            DataFrame без дубликатов
        """
        if df.index.duplicated().any():
            duplicate_count = df.index.duplicated().sum()
            logger.warning(f"Removing {duplicate_count} duplicate timestamps")
            df = df[~df.index.duplicated(keep="first")]

        return df

    @staticmethod
    def fill_missing_values(df: pd.DataFrame, method: str = "ffill") -> pd.DataFrame:
        """
        Заполнение пропущенных значений

        Args:
            df: DataFrame с OHLCV данными
            method: Метод заполнения (ffill, bfill)

        Returns:
            DataFrame с заполненными пропусками
        """
        if df.isnull().any().any():
            null_count = df.isnull().sum().sum()
            logger.warning(f"Filling {null_count} missing values using {method}")

            if method == "ffill":
                df = df.fillna(method="ffill")
            elif method == "bfill":
                df = df.fillna(method="bfill")
            else:
                raise ValueError(f"Unknown fill method: {method}")

            # Если после ffill/bfill остались NaN (в начале/конце), удаляем
            df = df.dropna()

        return df

    @staticmethod
    def validate_and_clean(df: pd.DataFrame, timeframe: str) -> Tuple[pd.DataFrame, List[str]]:
        """
        Полная валидация и очистка данных

        Args:
            df: DataFrame с OHLCV данными
            timeframe: Таймфрейм данных

        Returns:
            Tuple[pd.DataFrame, List[str]]: (очищенный DataFrame, список предупреждений)
        """
        warnings = []

        # 1. Проверка временных меток
        is_valid_ts, ts_errors = DataValidator.validate_timestamps(df, timeframe)
        if not is_valid_ts:
            warnings.extend(ts_errors)

        # 2. Удаление дубликатов
        original_len = len(df)
        df = DataValidator.check_duplicates(df)
        if len(df) < original_len:
            warnings.append(f"Removed {original_len - len(df)} duplicate rows")

        # 3. Заполнение пропусков
        if df.isnull().any().any():
            df = DataValidator.fill_missing_values(df, method="ffill")
            warnings.append("Filled missing values using forward fill")

        # 4. Валидация OHLC
        is_valid_ohlc, ohlc_errors = DataValidator.validate_ohlc(df)
        if not is_valid_ohlc:
            warnings.extend(ohlc_errors)
            # Можно добавить автоматическую коррекцию
            # Например, установить high = max(open, close, high)

        # 5. Сортировка по времени (если не отсортировано)
        if not df.index.is_monotonic_increasing:
            df = df.sort_index()
            warnings.append("Sorted data by timestamp")

        return df, warnings

    @staticmethod
    def validate_date_range(start: datetime, end: datetime) -> bool:
        """
        Валидация диапазона дат

        Args:
            start: Начальная дата
            end: Конечная дата

        Returns:
            bool: Валидность диапазона
        """
        if start >= end:
            raise ValueError("start date must be before end date")

        # Проверка что даты не в будущем
        now = datetime.utcnow()
        if start > now or end > now:
            raise ValueError("Dates cannot be in the future")

        return True
