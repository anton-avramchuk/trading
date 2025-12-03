"""
Загрузка данных из различных источников
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session

from app.models import Instrument, OHLCV
from app.utils.data_validator import DataValidator


class DataLoader:
    """Класс для загрузки OHLCV данных"""

    @staticmethod
    def load_from_csv(
        csv_path: str,
        date_column: str = "date",
        datetime_format: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Загрузка данных из CSV файла

        Args:
            csv_path: Путь к CSV файлу
            date_column: Название колонки с датой/временем
            datetime_format: Формат даты/времени (опционально)

        Returns:
            DataFrame с OHLCV данными

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если данные некорректны
        """
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.info(f"Loading data from CSV: {csv_path}")

        try:
            # Загрузка CSV
            df = pd.read_csv(csv_path)

            # Проверка наличия необходимых колонок
            required_cols = ["open", "high", "low", "close", "volume"]
            if date_column not in df.columns:
                raise ValueError(f"Date column '{date_column}' not found in CSV")

            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            # Преобразование даты в datetime и установка как index
            if datetime_format:
                df[date_column] = pd.to_datetime(df[date_column], format=datetime_format)
            else:
                df[date_column] = pd.to_datetime(df[date_column])

            df.set_index(date_column, inplace=True)
            df.index.name = "timestamp"

            # Приведение типов
            for col in required_cols:
                if col == "volume":
                    df[col] = df[col].astype(int)
                else:
                    df[col] = df[col].astype(float)

            logger.info(f"Loaded {len(df)} rows from CSV")
            return df

        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise

    @staticmethod
    def load_from_db(
        db: Session,
        ticker: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Загрузка данных из базы данных

        Args:
            db: Сессия базы данных
            ticker: Тикер инструмента
            timeframe: Таймфрейм
            start: Начальная дата (опционально)
            end: Конечная дата (опционально)

        Returns:
            DataFrame с OHLCV данными

        Raises:
            ValueError: Если инструмент не найден
        """
        logger.info(f"Loading data from DB: {ticker}, {timeframe}, {start} - {end}")

        # Валидация диапазона дат (только если обе даты заданы)
        if start is not None and end is not None:
            DataValidator.validate_date_range(start, end)

        # Получение инструмента
        instrument = db.query(Instrument).filter(
            Instrument.ticker == ticker.upper()
        ).first()

        if not instrument:
            raise ValueError(f"Instrument not found: {ticker}")

        # Запрос OHLCV данных
        query = db.query(OHLCV).filter(
            OHLCV.instrument_id == instrument.id,
            OHLCV.timeframe == timeframe
        )

        # Добавляем фильтры по датам только если они заданы
        if start is not None:
            query = query.filter(OHLCV.timestamp >= start)
        if end is not None:
            query = query.filter(OHLCV.timestamp <= end)

        query = query.order_by(OHLCV.timestamp)

        results = query.all()

        if not results:
            logger.warning(f"No data found for {ticker} {timeframe} {start}-{end}")
            return pd.DataFrame()

        # Преобразование в DataFrame
        data = {
            "timestamp": [r.timestamp for r in results],
            "open": [r.open for r in results],
            "high": [r.high for r in results],
            "low": [r.low for r in results],
            "close": [r.close for r in results],
            "volume": [r.volume for r in results],
        }

        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)

        logger.info(f"Loaded {len(df)} rows from DB")
        return df

    @staticmethod
    def save_to_db(
        db: Session,
        ticker: str,
        timeframe: str,
        data: pd.DataFrame,
        batch_size: int = 1000
    ) -> int:
        """
        Сохранение данных в базу данных

        Args:
            db: Сессия базы данных
            ticker: Тикер инструмента
            timeframe: Таймфрейм
            data: DataFrame с OHLCV данными
            batch_size: Размер батча для массовой вставки

        Returns:
            Количество сохранённых записей

        Raises:
            ValueError: Если инструмент не найден
        """
        logger.info(f"Saving {len(data)} rows to DB: {ticker}, {timeframe}")

        # Получение инструмента
        instrument = db.query(Instrument).filter(
            Instrument.ticker == ticker.upper()
        ).first()

        if not instrument:
            raise ValueError(f"Instrument not found: {ticker}")

        # Подготовка данных для вставки
        records = []
        for timestamp, row in data.iterrows():
            record = OHLCV(
                instrument_id=instrument.id,
                timeframe=timeframe,
                timestamp=timestamp,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=int(row["volume"])
            )
            records.append(record)

        # Массовая вставка батчами
        saved_count = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            db.bulk_save_objects(batch)
            db.commit()
            saved_count += len(batch)
            logger.debug(f"Saved batch {i // batch_size + 1}, total: {saved_count}")

        logger.info(f"Successfully saved {saved_count} rows to DB")
        return saved_count

    @staticmethod
    def migrate_csv_to_db(
        db: Session,
        csv_path: str,
        ticker: str,
        timeframe: str,
        date_column: str = "date",
        datetime_format: Optional[str] = None
    ) -> int:
        """
        Миграция данных из CSV в базу данных

        Args:
            db: Сессия базы данных
            csv_path: Путь к CSV файлу
            ticker: Тикер инструмента
            timeframe: Таймфрейм
            date_column: Название колонки с датой
            datetime_format: Формат даты/времени

        Returns:
            Количество сохранённых записей
        """
        logger.info(f"Migrating CSV to DB: {csv_path} -> {ticker} {timeframe}")

        # 1. Загрузка из CSV
        df = DataLoader.load_from_csv(csv_path, date_column, datetime_format)

        # 2. Валидация и очистка данных
        df, warnings = DataValidator.validate_and_clean(df, timeframe)
        if warnings:
            logger.warning(f"Data validation warnings: {warnings}")

        # 3. Сохранение в БД
        saved_count = DataLoader.save_to_db(db, ticker, timeframe, df)

        logger.info(f"Migration complete: {saved_count} rows saved")
        return saved_count
