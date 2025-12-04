# IMOEX Микросервис - Получение данных с Московской биржи

## 📋 Обзор

Отдельный микросервис для загрузки и обновления исторических данных с Московской биржи через MOEX ISS API. Имеет доступ к общей БД PostgreSQL и предоставляет REST API для управления загрузкой данных.

## 🎯 Цели

1. Автоматическая загрузка исторических данных для акций и фьючерсов MOEX
2. Регулярное обновление данных (daily job)
3. Поддержка всех таймфреймов (1m, 10m, 1h, 1d, 1w, 1M, 1Q)
4. Управление через REST API
5. Минимальная нагрузка на MOEX API (rate limiting, кэширование)

## 🏗 Архитектура

```
┌─────────────────────────────────────────┐
│         IMOEX Microservice              │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │       FastAPI Application          │ │
│  │  - REST API endpoints              │ │
│  │  - Background tasks                │ │
│  │  - Scheduler (APScheduler)         │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │       MOEX ISS Client              │ │
│  │  - Async HTTP client (aiohttp)    │ │
│  │  - Rate limiter                   │ │
│  │  - Retry logic                    │ │
│  │  - Data parser                    │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │       Data Processor               │ │
│  │  - Validation                     │ │
│  │  - Transformation                 │ │
│  │  - Deduplication                  │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
└──────────────────┼──────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │   PostgreSQL    │
         │   (Shared DB)   │
         │                 │
         │  - instruments  │
         │  - ohlcv        │
         │  - download_log │
         └─────────────────┘
```

## 📁 Структура проекта

```
imoex/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI приложение
│   ├── config.py               # Конфигурация
│   ├── dependencies.py         # DI для БД сессий
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── moex_client.py      # Клиент MOEX ISS API
│   │   ├── data_processor.py   # Обработка и валидация данных
│   │   ├── rate_limiter.py     # Rate limiting для MOEX API
│   │   └── scheduler.py        # APScheduler для фоновых задач
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── download.py     # Эндпоинты для загрузки
│   │   │   ├── securities.py   # Эндпоинты для списка инструментов
│   │   │   └── status.py       # Статус загрузок
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # Shared models (instrument, ohlcv)
│   │   └── download_log.py     # Лог загрузок
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── download.py         # Pydantic схемы для загрузки
│   │   └── securities.py       # Pydantic схемы для инструментов
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── download_service.py # Бизнес-логика загрузки
│   │   └── update_service.py   # Автообновление данных
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Настройка логирования
│       └── helpers.py          # Вспомогательные функции
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_moex_client.py
│   └── test_download_service.py
│
├── alembic/                     # Миграции (для download_log)
│   ├── env.py
│   └── versions/
│
├── .env.example
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🔌 API Endpoints

### 1. Загрузка данных

#### POST `/api/v1/download/single`
Загрузить данные для одного инструмента

**Request:**
```json
{
  "ticker": "GAZP",
  "timeframe": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "market": "stock",
  "board": "TQBR",
  "create_instrument": true
}
```

**Response:**
```json
{
  "ticker": "GAZP",
  "timeframe": "1d",
  "records_imported": 250,
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-12-31T23:59:59",
  "duration_seconds": 2.5,
  "message": "Успешно импортировано 250 записей"
}
```

#### POST `/api/v1/download/batch`
Массовая загрузка данных для нескольких инструментов

**Request:**
```json
{
  "tickers": ["GAZP", "SBER", "LKOH", "YNDX"],
  "timeframe": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "market": "stock",
  "board": "TQBR"
}
```

**Response:**
```json
{
  "total": 4,
  "successful": 4,
  "failed": 0,
  "results": [
    {
      "ticker": "GAZP",
      "success": true,
      "records_imported": 250
    },
    {
      "ticker": "SBER",
      "success": true,
      "records_imported": 250
    }
  ],
  "total_duration_seconds": 10.5
}
```

#### POST `/api/v1/download/update`
Обновить данные для всех инструментов в БД

**Request:**
```json
{
  "timeframe": "1d",
  "days_back": 7  // Обновить данные за последние 7 дней
}
```

**Response:**
```json
{
  "total_instruments": 50,
  "updated": 48,
  "failed": 2,
  "total_records_added": 1200
}
```

### 2. Управление инструментами

#### GET `/api/v1/securities/list`
Получить список инструментов с MOEX

**Query params:**
- `market`: stock | futures
- `board`: TQBR | RFUD | ...
- `limit`: int (default: 100)
- `offset`: int (default: 0)

**Response:**
```json
{
  "securities": [
    {
      "ticker": "GAZP",
      "name": "Газпром ао",
      "isin": "RU0007661625",
      "lot_size": 10,
      "market": "stock",
      "board": "TQBR"
    }
  ],
  "total": 250,
  "limit": 100,
  "offset": 0
}
```

#### POST `/api/v1/securities/sync`
Синхронизировать список инструментов с MOEX

**Request:**
```json
{
  "market": "stock",
  "board": "TQBR"
}
```

**Response:**
```json
{
  "instruments_added": 10,
  "instruments_updated": 5,
  "message": "Синхронизация завершена"
}
```

### 3. Статус и логи

#### GET `/api/v1/status/downloads`
Получить историю загрузок

**Response:**
```json
{
  "downloads": [
    {
      "id": 1,
      "ticker": "GAZP",
      "timeframe": "1d",
      "status": "completed",
      "records_imported": 250,
      "started_at": "2024-12-03T10:00:00",
      "completed_at": "2024-12-03T10:02:30",
      "duration_seconds": 150,
      "error": null
    }
  ]
}
```

#### GET `/api/v1/status/health`
Health check

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "moex_api": "available",
  "uptime_seconds": 3600
}
```

## 🗄️ Модель данных

### DownloadLog (новая таблица для микросервиса)

```python
class DownloadLog(Base):
    __tablename__ = "download_log"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False, index=True)
    timeframe = Column(String, nullable=False)
    market = Column(String, nullable=False)
    board = Column(String, nullable=False)

    status = Column(String, nullable=False)  # pending, running, completed, failed
    records_imported = Column(Integer, default=0)

    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    error = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Дополнительная информация

    created_at = Column(DateTime, default=datetime.utcnow)
```

### Использование общих таблиц

Микросервис использует таблицы из основной БД:
- `instruments` - список инструментов
- `ohlcv` - свечные данные
- `indexes` - биржевые индексы (опционально)

## ⚙️ Конфигурация

### Переменные окружения (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/trading

# MOEX API
MOEX_BASE_URL=https://iss.moex.com/iss
MOEX_RATE_LIMIT=10  # requests per second
MOEX_TIMEOUT=30     # seconds
MOEX_MAX_RETRIES=3

# Service
SERVICE_PORT=8001
SERVICE_HOST=0.0.0.0
LOG_LEVEL=INFO

# Scheduler
ENABLE_SCHEDULER=true
UPDATE_SCHEDULE="0 19 * * 1-5"  # Ежедневно в 19:00 по будням
UPDATE_TIMEFRAMES=1d,1h
UPDATE_DAYS_BACK=3

# Redis (для кэширования и rate limiting)
REDIS_URL=redis://redis:6379/1
CACHE_TTL=3600  # 1 hour
```

## 🔄 MOEX ISS Client - Детальная реализация

### Ключевые возможности:

1. **Постраничная загрузка**
   - MOEX возвращает максимум 500 свечей за запрос
   - Автоматическая постраничная загрузка больших объёмов

2. **Rate Limiting**
   - Не более 10 запросов в секунду
   - Использование Redis для распределённого rate limiting

3. **Retry Logic**
   - Экспоненциальный backoff при ошибках
   - Максимум 3 попытки

4. **Кэширование**
   - Кэширование списков инструментов (TTL: 1 час)
   - Кэширование метаданных

5. **Поддержка рынков**
   - **Акции**: TQBR (Т+ Акции и ДР), TQTF (Т+ Иностранные ЦБ)
   - **Фьючерсы**: RFUD (FORTS)
   - **Облигации**: TQCB (Т+ Облигации корпоративные)

6. **Таймфреймы MOEX**
   - `1` - 1 минута
   - `10` - 10 минут
   - `60` - 1 час
   - `24` - 1 день
   - `7` - 1 неделя
   - `31` - 1 месяц
   - `4` - квартал

## 📊 Фоновые задачи (APScheduler)

### 1. Daily Update Job
Ежедневное обновление данных для всех инструментов

```python
@scheduler.scheduled_job('cron', hour=19, minute=0, day_of_week='mon-fri')
async def daily_update_job():
    """Обновление данных за прошедший день"""
    timeframes = ["1d", "1h"]
    days_back = 3

    # Получить все активные инструменты
    instruments = await get_active_instruments()

    # Обновить данные
    for instrument in instruments:
        await download_service.update_instrument(
            ticker=instrument.ticker,
            timeframes=timeframes,
            days_back=days_back
        )
```

### 2. Weekly Full Sync
Еженедельная полная синхронизация списка инструментов

```python
@scheduler.scheduled_job('cron', day_of_week='sun', hour=2, minute=0)
async def weekly_sync_job():
    """Синхронизация списка инструментов с MOEX"""
    markets = [("stock", "TQBR"), ("futures", "RFUD")]

    for market, board in markets:
        await securities_service.sync_securities(
            market=market,
            board=board
        )
```

### 3. Health Check
Регулярная проверка доступности MOEX API

```python
@scheduler.scheduled_job('interval', minutes=5)
async def health_check_job():
    """Проверка доступности MOEX API"""
    try:
        await moex_client.ping()
        update_health_status("moex_api", "available")
    except Exception as e:
        update_health_status("moex_api", "unavailable")
        logger.error(f"MOEX API недоступен: {e}")
```

## 🐳 Docker Configuration

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY ./app ./app
COPY alembic.ini .
COPY ./alembic ./alembic

# Запуск миграций и сервиса
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8001"]
```

### docker-compose.yml (для основного проекта)

```yaml
services:
  imoex:
    build:
      context: ./imoex
      dockerfile: Dockerfile
    container_name: trading-imoex
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql+asyncpg://trading_user:password@db:5432/trading
      - REDIS_URL=redis://redis:6379/1
      - ENABLE_SCHEDULER=true
    depends_on:
      - db
      - redis
    networks:
      - trading-network
    restart: unless-stopped
    volumes:
      - ./imoex/logs:/app/logs
```

## 🔐 Безопасность

1. **Rate Limiting**
   - Лимит запросов к микросервису (FastAPI Limiter)
   - Лимит запросов к MOEX API

2. **Валидация**
   - Pydantic валидация всех входных данных
   - Валидация OHLC данных (H >= max(O,C), L <= min(O,C))

3. **Логирование**
   - Все операции логируются
   - Structured logging с JSON форматом

4. **Мониторинг**
   - Health check endpoint
   - Prometheus metrics (опционально)

## 📈 Производительность

### Оптимизации:

1. **Batch Insert**
   - Групповая вставка записей в БД (по 1000 за раз)
   - Использование `INSERT ... ON CONFLICT DO NOTHING`

2. **Async Operations**
   - Асинхронная загрузка через aiohttp
   - Параллельная обработка нескольких инструментов

3. **Connection Pooling**
   - SQLAlchemy async engine с pool
   - Redis connection pool

4. **Кэширование**
   - Кэширование списков инструментов
   - Кэширование результатов валидации

## 🧪 Тестирование

### Unit Tests

```python
# tests/test_moex_client.py
@pytest.mark.asyncio
async def test_get_candles():
    async with MOEXClient() as client:
        df = await client.get_candles(
            ticker="GAZP",
            timeframe="1d",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )

        assert not df.empty
        assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]
        assert (df["high"] >= df["low"]).all()
```

### Integration Tests

```python
# tests/test_download_service.py
@pytest.mark.asyncio
async def test_download_and_save(db_session):
    service = DownloadService()
    result = await service.download_and_save(
        db=db_session,
        ticker="SBER",
        timeframe="1d",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31)
    )

    assert result["records_imported"] > 0
    assert result["ticker"] == "SBER"
```

## 📝 Примеры использования

### 1. Загрузка исторических данных для одного тикера

```bash
curl -X POST http://localhost:8001/api/v1/download/single \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "GAZP",
    "timeframe": "1d",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

### 2. Массовая загрузка индекса IMOEX

```bash
curl -X POST http://localhost:8001/api/v1/download/batch \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["GAZP", "SBER", "LKOH", "YNDX", "GMKN", "NVTK", "ROSN", "TATN", "MGNT", "MTSS"],
    "timeframe": "1d",
    "start_date": "2023-01-01",
    "end_date": "2024-12-31"
  }'
```

### 3. Ежедневное обновление

```bash
curl -X POST http://localhost:8001/api/v1/download/update \
  -H "Content-Type: application/json" \
  -d '{
    "timeframe": "1d",
    "days_back": 3
  }'
```

## 🚀 Deployment

### Запуск в development

```bash
cd imoex
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Запуск в production (Docker)

```bash
cd trading
docker-compose up -d imoex
docker-compose logs -f imoex
```

## 📊 Мониторинг и метрики

### Prometheus Metrics (опционально)

```
# Количество успешных загрузок
moex_downloads_total{status="success"}

# Количество ошибок
moex_downloads_total{status="error"}

# Среднее время загрузки
moex_download_duration_seconds

# Количество загруженных записей
moex_records_imported_total

# Доступность MOEX API
moex_api_available{status="up|down"}
```

## 🔄 Взаимодействие с основным backend

Основной backend может вызывать IMOEX микросервис для:

1. **Загрузки новых инструментов**
   - Пользователь добавляет новый тикер через UI
   - Backend отправляет запрос к IMOEX для загрузки данных

2. **Обновления данных**
   - Периодическое обновление через scheduler
   - Ручное обновление по запросу пользователя

3. **Проверки доступности данных**
   - IMOEX предоставляет информацию о наличии данных

## 📋 Roadmap

### Phase 1 (MVP)
- [x] Базовая структура микросервиса
- [ ] MOEX ISS Client с основными функциями
- [ ] API endpoints для загрузки
- [ ] Интеграция с PostgreSQL
- [ ] Docker контейнеризация

### Phase 2 (Production Ready)
- [ ] Rate limiting и retry logic
- [ ] APScheduler для фоновых задач
- [ ] Полное логирование и мониторинг
- [ ] Unit и integration тесты
- [ ] Документация API (Swagger)

### Phase 3 (Advanced Features)
- [ ] Redis кэширование
- [ ] Prometheus метрики
- [ ] Websocket для real-time обновлений
- [ ] Поддержка дополнительных рынков (облигации, опционы)
- [ ] Incremental updates (только новые данные)

### Phase 4 (Optimization)
- [ ] Batch processing оптимизация
- [ ] Параллельная загрузка
- [ ] Data compression
- [ ] Advanced caching strategies

## 🎯 Ключевые особенности

1. **Независимость** - отдельный микросервис с собственным lifecycle
2. **Масштабируемость** - легко масштабируется горизонтально
3. **Надёжность** - retry logic, error handling, logging
4. **Производительность** - async operations, batch processing
5. **Мониторинг** - health checks, metrics, structured logging
6. **Гибкость** - поддержка различных рынков и таймфреймов
7. **Простота интеграции** - REST API для взаимодействия

## 📚 Полезные ссылки

- [MOEX ISS API Documentation](https://iss.moex.com/iss/reference/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [aiohttp](https://docs.aiohttp.org/)
