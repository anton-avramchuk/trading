"""
API endpoints для OHLCV данных
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.data_manager import DataManager
from app.models import Instrument
from app.schemas import (
    OHLCVImportRequest,
    OHLCVQuery,
    OHLCVRead,
    TimeframeList,
)
from app.utils.csv_importer import CSVImporter

router = APIRouter()

# Поддерживаемые таймфреймы
SUPPORTED_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]


# ===== OHLCV Data Endpoints =====

@router.get("/{ticker}", response_model=List[OHLCVRead])
def get_ohlcv_data(
    ticker: str,
    query: OHLCVQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    Получить OHLCV данные для инструмента

    Args:
        ticker: Тикер инструмента
        query: Параметры запроса (timeframe, start_date, end_date, limit)

    Returns:
        List[OHLCVRead]: Список OHLCV свечей

    Raises:
        HTTPException: 404 если инструмент не найден
        HTTPException: 400 если некорректные параметры запроса
    """
    # Проверка существования инструмента
    instrument = db.query(Instrument).filter(
        Instrument.ticker == ticker.upper()
    ).first()

    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {ticker} not found"
        )

    # Валидация таймфрейма
    if query.timeframe not in SUPPORTED_TIMEFRAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported timeframe: {query.timeframe}. "
                   f"Supported: {', '.join(SUPPORTED_TIMEFRAMES)}"
        )

    # Получение данных через DataManager
    try:
        data_manager = DataManager(db)
        df = data_manager.get_data(
            ticker=ticker.upper(),
            timeframe=query.timeframe,
            start=query.start_date,
            end=query.end_date
        )

        if df.empty:
            logger.warning(f"No data found for {ticker} {query.timeframe}")
            return []

        # Применение лимита (если указан)
        if query.limit:
            df = df.tail(query.limit)

        # Конвертация в список Pydantic моделей
        ohlcv_list = []
        for idx, row in df.iterrows():
            ohlcv_list.append(
                OHLCVRead(
                    timestamp=idx,
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=int(row["volume"])
                )
            )

        logger.info(
            f"Retrieved {len(ohlcv_list)} OHLCV records for {ticker} {query.timeframe}"
        )
        return ohlcv_list

    except Exception as e:
        logger.error(f"Error retrieving OHLCV data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving data: {str(e)}"
        )


@router.post("/import", status_code=status.HTTP_201_CREATED)
def import_ohlcv_data(
    import_request: OHLCVImportRequest,
    db: Session = Depends(get_db)
):
    """
    Импорт OHLCV данных из CSV файла

    Args:
        import_request: Параметры импорта (csv_path, ticker, timeframe, и т.д.)

    Returns:
        dict: Результат импорта (status, records_imported)

    Raises:
        HTTPException: 404 если файл не найден
        HTTPException: 400 если некорректные параметры
        HTTPException: 500 если ошибка импорта
    """
    logger.info(
        f"Starting CSV import: {import_request.csv_path} -> "
        f"{import_request.ticker} {import_request.timeframe}"
    )

    # Валидация таймфрейма
    if import_request.timeframe not in SUPPORTED_TIMEFRAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported timeframe: {import_request.timeframe}"
        )

    # Импорт через CSVImporter
    try:
        importer = CSVImporter(db)
        result = importer.import_file(
            csv_path=import_request.csv_path,
            ticker=import_request.ticker,
            timeframe=import_request.timeframe,
            date_column=import_request.date_column,
            datetime_format=import_request.datetime_format,
            create_instrument=import_request.create_instrument,
            instrument_name=import_request.instrument_name,
            market=import_request.market,
            instrument_type=import_request.instrument_type
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        logger.info(f"CSV import completed: {result['records_imported']} records")
        return result

    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CSV file not found: {import_request.csv_path}"
        )
    except ValueError as e:
        logger.error(f"Import validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import error: {str(e)}"
        )


@router.post("/import/batch", status_code=status.HTTP_201_CREATED)
def import_batch_ohlcv_data(
    directory: str,
    pattern: str = "*.csv",
    timeframe: str = "1d",
    ticker_from_filename: bool = True,
    date_column: str = "date",
    datetime_format: str | None = None,
    create_instruments: bool = True,
    market: str = "MOEX",
    instrument_type: str = "stock",
    db: Session = Depends(get_db)
):
    """
    Массовый импорт OHLCV данных из директории с CSV файлами

    Args:
        directory: Путь к директории с CSV файлами
        pattern: Паттерн для поиска файлов (например, "*.csv", "GAZP*.csv")
        timeframe: Таймфрейм по умолчанию (если не указан в имени файла)
        ticker_from_filename: Извлекать тикер из имени файла
        date_column: Название колонки с датой
        datetime_format: Формат даты/времени
        create_instruments: Создавать инструменты если не существуют
        market: Рынок (для создания инструментов)
        instrument_type: Тип инструмента

    Returns:
        dict: Сводка по результатам импорта

    Raises:
        HTTPException: 404 если директория не найдена
        HTTPException: 500 если ошибка импорта
    """
    logger.info(f"Starting batch CSV import from directory: {directory}")

    try:
        importer = CSVImporter(db)
        results = importer.import_directory(
            directory=directory,
            pattern=pattern,
            timeframe=timeframe,
            ticker_from_filename=ticker_from_filename,
            date_column=date_column,
            datetime_format=datetime_format,
            create_instruments=create_instruments,
            market=market,
            instrument_type=instrument_type
        )

        # Получение сводки
        summary = importer.get_import_summary(results)

        logger.info(
            f"Batch import completed: {summary['successful']} succeeded, "
            f"{summary['failed']} failed, {summary['total_records_imported']} total records"
        )

        return {
            "status": "completed",
            "summary": summary,
            "details": results
        }

    except FileNotFoundError as e:
        logger.error(f"Directory not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Directory not found: {directory}"
        )
    except Exception as e:
        logger.error(f"Batch import error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch import error: {str(e)}"
        )


@router.get("/timeframes/", response_model=TimeframeList)
def get_supported_timeframes():
    """
    Получить список поддерживаемых таймфреймов

    Returns:
        TimeframeList: Список таймфреймов с описанием
    """
    timeframe_descriptions = {
        "1m": "1 минута",
        "5m": "5 минут",
        "15m": "15 минут",
        "30m": "30 минут",
        "1h": "1 час",
        "4h": "4 часа",
        "1d": "1 день",
        "1w": "1 неделя",
        "1M": "1 месяц"
    }

    return TimeframeList(
        timeframes=SUPPORTED_TIMEFRAMES,
        descriptions=timeframe_descriptions
    )


@router.get("/{ticker}/latest", response_model=OHLCVRead | None)
def get_latest_ohlcv(
    ticker: str,
    timeframe: str = "1d",
    db: Session = Depends(get_db)
):
    """
    Получить последнюю свечу для инструмента

    Args:
        ticker: Тикер инструмента
        timeframe: Таймфрейм

    Returns:
        OHLCVRead: Последняя свеча или None

    Raises:
        HTTPException: 404 если инструмент не найден
    """
    # Проверка существования инструмента
    instrument = db.query(Instrument).filter(
        Instrument.ticker == ticker.upper()
    ).first()

    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {ticker} not found"
        )

    # Валидация таймфрейма
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported timeframe: {timeframe}"
        )

    try:
        data_manager = DataManager(db)
        latest_timestamp = data_manager.get_latest_timestamp(
            ticker=ticker.upper(),
            timeframe=timeframe
        )

        if not latest_timestamp:
            logger.warning(f"No data found for {ticker} {timeframe}")
            return None

        # Получение последней свечи
        from app.models import OHLCV

        latest_ohlcv = db.query(OHLCV).filter(
            OHLCV.instrument_id == instrument.id,
            OHLCV.timeframe == timeframe,
            OHLCV.timestamp == latest_timestamp
        ).first()

        if not latest_ohlcv:
            return None

        return OHLCVRead(
            timestamp=latest_ohlcv.timestamp,
            open=latest_ohlcv.open,
            high=latest_ohlcv.high,
            low=latest_ohlcv.low,
            close=latest_ohlcv.close,
            volume=latest_ohlcv.volume
        )

    except Exception as e:
        logger.error(f"Error retrieving latest OHLCV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving latest data: {str(e)}"
        )


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ohlcv_data(
    ticker: str,
    timeframe: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db)
):
    """
    Удалить OHLCV данные для инструмента

    Args:
        ticker: Тикер инструмента
        timeframe: Таймфрейм (опционально, если не указан - удаляются все)
        start_date: Начальная дата (опционально)
        end_date: Конечная дата (опционально)

    Raises:
        HTTPException: 404 если инструмент не найден
    """
    # Проверка существования инструмента
    instrument = db.query(Instrument).filter(
        Instrument.ticker == ticker.upper()
    ).first()

    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {ticker} not found"
        )

    try:
        from app.models import OHLCV

        # Построение запроса на удаление
        query = db.query(OHLCV).filter(OHLCV.instrument_id == instrument.id)

        if timeframe:
            query = query.filter(OHLCV.timeframe == timeframe)

        if start_date:
            query = query.filter(OHLCV.timestamp >= start_date)

        if end_date:
            query = query.filter(OHLCV.timestamp <= end_date)

        # Подсчёт записей для удаления
        count = query.count()

        # Удаление
        query.delete(synchronize_session=False)
        db.commit()

        logger.info(
            f"Deleted {count} OHLCV records for {ticker}"
            f"{f' {timeframe}' if timeframe else ''}"
        )

        return None

    except Exception as e:
        logger.error(f"Error deleting OHLCV data: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting data: {str(e)}"
        )
