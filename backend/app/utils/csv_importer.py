"""
Импорт CSV данных в базу данных
"""
from pathlib import Path
from typing import List, Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.core.data_loader import DataLoader
from app.models import Instrument


class CSVImporter:
    """Класс для импорта CSV файлов в базу данных"""

    def __init__(self, db: Session):
        """
        Инициализация импортера

        Args:
            db: Сессия базы данных
        """
        self.db = db

    def import_file(
        self,
        csv_path: str,
        ticker: str,
        timeframe: str,
        date_column: str = "date",
        datetime_format: Optional[str] = None,
        create_instrument: bool = False,
        instrument_name: Optional[str] = None,
        market: str = "MOEX",
        instrument_type: str = "stock"
    ) -> dict:
        """
        Импорт одного CSV файла

        Args:
            csv_path: Путь к CSV файлу
            ticker: Тикер инструмента
            timeframe: Таймфрейм данных
            date_column: Название колонки с датой
            datetime_format: Формат даты/времени
            create_instrument: Создать инструмент если не существует
            instrument_name: Название инструмента (для создания)
            market: Рынок (для создания)
            instrument_type: Тип инструмента (для создания)

        Returns:
            dict с результатами импорта

        Raises:
            ValueError: Если инструмент не найден и create_instrument=False
            FileNotFoundError: Если CSV файл не найден
        """
        logger.info(f"Starting import: {csv_path} -> {ticker} {timeframe}")

        # Проверка существования инструмента
        instrument = self.db.query(Instrument).filter(
            Instrument.ticker == ticker.upper()
        ).first()

        if not instrument:
            if create_instrument:
                # Создание инструмента
                instrument = Instrument(
                    ticker=ticker.upper(),
                    name=instrument_name or ticker.upper(),
                    market=market,
                    instrument_type=instrument_type
                )
                self.db.add(instrument)
                self.db.commit()
                logger.info(f"Created new instrument: {ticker}")
            else:
                raise ValueError(
                    f"Instrument {ticker} not found. "
                    f"Set create_instrument=True to create it."
                )

        # Миграция CSV в БД
        try:
            saved_count = DataLoader.migrate_csv_to_db(
                db=self.db,
                csv_path=csv_path,
                ticker=ticker,
                timeframe=timeframe,
                date_column=date_column,
                datetime_format=datetime_format
            )

            result = {
                "status": "success",
                "ticker": ticker,
                "timeframe": timeframe,
                "records_imported": saved_count,
                "csv_path": csv_path
            }

            logger.info(f"Import completed: {saved_count} records")
            return result

        except Exception as e:
            logger.error(f"Import failed: {e}")
            result = {
                "status": "error",
                "ticker": ticker,
                "timeframe": timeframe,
                "error": str(e),
                "csv_path": csv_path
            }
            return result

    def import_directory(
        self,
        directory: str,
        pattern: str = "*.csv",
        timeframe: str = "1d",
        ticker_from_filename: bool = True,
        date_column: str = "date",
        datetime_format: Optional[str] = None,
        create_instruments: bool = True,
        market: str = "MOEX",
        instrument_type: str = "stock"
    ) -> List[dict]:
        """
        Импорт всех CSV файлов из директории

        Args:
            directory: Путь к директории с CSV файлами
            pattern: Паттерн для поиска файлов (например, "*.csv", "GAZP*.csv")
            timeframe: Таймфрейм данных (по умолчанию для всех файлов)
            ticker_from_filename: Извлекать тикер из имени файла
            date_column: Название колонки с датой
            datetime_format: Формат даты/времени
            create_instruments: Создавать инструменты если не существуют
            market: Рынок (для создания инструментов)
            instrument_type: Тип инструмента (для создания)

        Returns:
            List[dict] с результатами импорта каждого файла

        Raises:
            FileNotFoundError: Если директория не найдена
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        # Поиск CSV файлов
        csv_files = list(dir_path.glob(pattern))
        if not csv_files:
            logger.warning(f"No CSV files found in {directory} matching {pattern}")
            return []

        logger.info(f"Found {len(csv_files)} CSV files in {directory}")

        results = []
        for csv_file in csv_files:
            # Извлечение тикера из имени файла
            if ticker_from_filename:
                # Формат: TICKER_timeframe.csv или TICKER.csv
                filename = csv_file.stem  # Без расширения
                ticker = filename.split("_")[0].upper()
            else:
                # Нужно указать тикер вручную, пропускаем
                logger.warning(f"Skipping {csv_file}: ticker_from_filename=False")
                continue

            # Попытка извлечь таймфрейм из имени файла
            if "_" in filename:
                parts = filename.split("_")
                if len(parts) > 1:
                    file_timeframe = parts[1]
                else:
                    file_timeframe = timeframe
            else:
                file_timeframe = timeframe

            # Импорт файла
            result = self.import_file(
                csv_path=str(csv_file),
                ticker=ticker,
                timeframe=file_timeframe,
                date_column=date_column,
                datetime_format=datetime_format,
                create_instrument=create_instruments,
                instrument_name=ticker,
                market=market,
                instrument_type=instrument_type
            )

            results.append(result)

        # Статистика
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = sum(1 for r in results if r["status"] == "error")
        total_records = sum(r.get("records_imported", 0) for r in results)

        logger.info(
            f"Batch import complete: {success_count} succeeded, "
            f"{error_count} failed, {total_records} total records"
        )

        return results

    def get_import_summary(self, results: List[dict]) -> dict:
        """
        Получить сводку по результатам импорта

        Args:
            results: Список результатов импорта

        Returns:
            dict со сводной информацией
        """
        total_files = len(results)
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = sum(1 for r in results if r["status"] == "error")
        total_records = sum(r.get("records_imported", 0) for r in results)

        errors = [
            {"ticker": r["ticker"], "error": r["error"]}
            for r in results if r["status"] == "error"
        ]

        return {
            "total_files": total_files,
            "successful": success_count,
            "failed": error_count,
            "total_records_imported": total_records,
            "errors": errors
        }
