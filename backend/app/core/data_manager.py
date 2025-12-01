"""
Управление данными с поддержкой multi-timeframe
"""
from datetime import datetime
from typing import Dict, List

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session

from app.core.data_loader import DataLoader
from app.utils.data_validator import DataValidator


class DataManager:
    """Класс для управления OHLCV данными"""

    def __init__(self, db: Session):
        """
        Инициализация менеджера данных

        Args:
            db: Сессия базы данных
        """
        self.db = db

    def get_data(
        self,
        ticker: str,
        timeframe: str,
        start: datetime,
        end: datetime
    ) -> pd.DataFrame:
        """
        Получение данных для одного таймфрейма

        Args:
            ticker: Тикер инструмента
            timeframe: Таймфрейм
            start: Начальная дата
            end: Конечная дата

        Returns:
            DataFrame с OHLCV данными
        """
        logger.debug(f"Getting data: {ticker} {timeframe} {start}-{end}")

        return DataLoader.load_from_db(
            db=self.db,
            ticker=ticker,
            timeframe=timeframe,
            start=start,
            end=end
        )

    def get_multi_timeframe_data(
        self,
        ticker: str,
        timeframes: List[str],
        start: datetime,
        end: datetime
    ) -> Dict[str, pd.DataFrame]:
        """
        Получение данных для нескольких таймфреймов

        Args:
            ticker: Тикер инструмента
            timeframes: Список таймфреймов
            start: Начальная дата
            end: Конечная дата

        Returns:
            Dict[str, pd.DataFrame]: Словарь {timeframe: DataFrame}
        """
        logger.info(
            f"Getting multi-timeframe data: {ticker}, "
            f"timeframes={timeframes}, {start}-{end}"
        )

        data_dict = {}

        for tf in timeframes:
            try:
                df = self.get_data(ticker, tf, start, end)
                if not df.empty:
                    data_dict[tf] = df
                else:
                    logger.warning(f"No data found for {ticker} {tf}")
            except Exception as e:
                logger.error(f"Error loading data for {ticker} {tf}: {e}")

        return data_dict

    def save_data(
        self,
        ticker: str,
        timeframe: str,
        data: pd.DataFrame
    ) -> int:
        """
        Сохранение данных в базу данных

        Args:
            ticker: Тикер инструмента
            timeframe: Таймфрейм
            data: DataFrame с OHLCV данными

        Returns:
            Количество сохранённых записей
        """
        logger.info(f"Saving data: {ticker} {timeframe}, {len(data)} rows")

        # Валидация и очистка данных
        data, warnings = DataValidator.validate_and_clean(data, timeframe)
        if warnings:
            logger.warning(f"Data validation warnings: {warnings}")

        # Сохранение в БД
        return DataLoader.save_to_db(
            db=self.db,
            ticker=ticker,
            timeframe=timeframe,
            data=data
        )

    def resample_timeframe(
        self,
        data: pd.DataFrame,
        source_tf: str,
        target_tf: str
    ) -> pd.DataFrame:
        """
        Ресемплинг данных на другой таймфрейм

        Args:
            data: DataFrame с OHLCV данными
            source_tf: Исходный таймфрейм
            target_tf: Целевой таймфрейм

        Returns:
            DataFrame с данными на целевом таймфрейме

        Raises:
            ValueError: Если ресемплинг невозможен
        """
        logger.debug(f"Resampling {source_tf} -> {target_tf}")

        # Маппинг таймфреймов на pandas offset
        tf_mapping = {
            "1m": "1T",
            "5m": "5T",
            "15m": "15T",
            "30m": "30T",
            "1h": "1H",
            "4h": "4H",
            "1d": "1D",
            "1w": "1W",
            "1M": "1M"
        }

        if target_tf not in tf_mapping:
            raise ValueError(f"Unknown target timeframe: {target_tf}")

        target_offset = tf_mapping[target_tf]

        # Ресемплинг
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

    def get_latest_timestamp(
        self,
        ticker: str,
        timeframe: str
    ) -> datetime | None:
        """
        Получение последней временной метки для инструмента

        Args:
            ticker: Тикер инструмента
            timeframe: Таймфрейм

        Returns:
            Последняя временная метка или None если данных нет
        """
        from app.models import Instrument, OHLCV

        instrument = self.db.query(Instrument).filter(
            Instrument.ticker == ticker.upper()
        ).first()

        if not instrument:
            return None

        latest = self.db.query(OHLCV).filter(
            OHLCV.instrument_id == instrument.id,
            OHLCV.timeframe == timeframe
        ).order_by(OHLCV.timestamp.desc()).first()

        return latest.timestamp if latest else None

    def check_data_availability(
        self,
        ticker: str,
        timeframes: List[str],
        start: datetime,
        end: datetime
    ) -> Dict[str, bool]:
        """
        Проверка наличия данных для таймфреймов

        Args:
            ticker: Тикер инструмента
            timeframes: Список таймфреймов
            start: Начальная дата
            end: Конечная дата

        Returns:
            Dict[str, bool]: {timeframe: is_available}
        """
        availability = {}

        for tf in timeframes:
            try:
                df = self.get_data(ticker, tf, start, end)
                availability[tf] = not df.empty
            except Exception as e:
                logger.error(f"Error checking data for {ticker} {tf}: {e}")
                availability[tf] = False

        return availability
