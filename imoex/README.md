# IMOEX Service

Микросервис для загрузки исторических данных с Московской биржи (MOEX ISS API).

## Особенности

- ✅ **Валидация таймфреймов**: загружаются только таймфреймы, существующие в БД
- 🚀 **Асинхронная работа**: FastAPI + aiohttp + asyncpg
- 📊 **MOEX ISS API**: интеграция с официальным API Московской биржи
- 🔄 **Rate limiting**: ограничение 10 запросов/сек к MOEX API
- 📝 **Логирование**: полная история всех загрузок в таблице download_log
- 🐳 **Docker ready**: готов к деплою в контейнере

## Архитектура

```
imoex/
├── app/
│   ├── core/
│   │   └── moex_client.py        # MOEX ISS API клиент с валидацией таймфреймов
│   ├── api/v1/
│   │   ├── health.py             # Health checks
│   │   ├── timeframes.py         # Получение доступных таймфреймов
│   │   ├── instruments.py        # Управление инструментами
│   │   └── download.py           # Загрузка данных
│   ├── services/
│   │   ├── timeframe_service.py  # Работа с таймфреймами
│   │   ├── instrument_service.py # Работа с инструментами
│   │   └── data_downloader.py    # Загрузка и сохранение данных
│   ├── schemas/
│   │   ├── timeframe.py          # Pydantic схемы для таймфреймов
│   │   ├── instrument.py         # Pydantic схемы для инструментов
│   │   └── download.py           # Pydantic схемы для загрузки
│   ├── models/                   # Импорт моделей из backend
│   ├── config.py                 # Настройки приложения
│   ├── dependencies.py           # Dependency injection
│   └── main.py                   # FastAPI приложение
├── Dockerfile
├── requirements.txt
└── .env.example
```

## API Endpoints

### Health

- `GET /health` - Проверка работоспособности сервиса
- `GET /health/db` - Проверка подключения к БД

### Timeframes

- `GET /api/v1/timeframes` - Список доступных таймфреймов
- `GET /api/v1/timeframes/{code}` - Информация о таймфрейме

### Instruments

- `GET /api/v1/instruments` - Список инструментов с фильтрами
- `GET /api/v1/instruments/{ticker}` - Информация об инструменте

### Download

- `POST /api/v1/download` - Загрузить данные с MOEX (синхронно)
- `POST /api/v1/download/background` - Загрузить данные в фоне
- `GET /api/v1/download/logs` - История загрузок
- `GET /api/v1/download/logs/{log_id}` - Детали конкретной загрузки
- `GET /api/v1/download/stats` - Статистика загрузок

## Использование

### Запуск локально

```bash
# Создать .env файл
cp .env.example .env

# Установить зависимости
pip install -r requirements.txt

# Запустить сервис
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Запуск в Docker

```bash
docker build -t imoex:latest .
docker run -p 8001:8001 --env-file .env imoex:latest
```

### Примеры запросов

#### Получить список доступных таймфреймов

```bash
curl http://localhost:8001/api/v1/timeframes
```

Ответ:
```json
[
  {
    "id": 1,
    "code": "1m",
    "name": "1 минута",
    "description": null,
    "minutes": 1,
    "moex_interval": 1,
    "is_active": 1,
    "created_at": "2024-01-01T00:00:00"
  },
  ...
]
```

#### Загрузить данные GAZP 1h за последние 30 дней

```bash
curl -X POST http://localhost:8001/api/v1/download \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "GAZP",
    "timeframe": "1h",
    "market": "stock",
    "board": "TQBR",
    "days_back": 30
  }'
```

Ответ:
```json
{
  "success": true,
  "message": "Successfully downloaded 360 records",
  "log_id": 123,
  "ticker": "GAZP",
  "timeframe": "1h",
  "records_imported": 360,
  "duration_seconds": 5.23,
  "error": null
}
```

#### Загрузить данные с указанием дат

```bash
curl -X POST http://localhost:8001/api/v1/download \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "SBER",
    "timeframe": "1d",
    "market": "stock",
    "board": "TQBR",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-12-31T23:59:59"
  }'
```

#### Получить статистику загрузок

```bash
curl http://localhost:8001/api/v1/download/stats
```

Ответ:
```json
{
  "total_downloads": 150,
  "successful_downloads": 145,
  "failed_downloads": 5,
  "total_records": 125000,
  "average_duration": 3.45,
  "last_download": "2024-01-15T10:30:00"
}
```

#### Получить историю загрузок для GAZP

```bash
curl "http://localhost:8001/api/v1/download/logs?ticker=GAZP&limit=10"
```

## Валидация таймфреймов

**КРИТИЧЕСКИ ВАЖНО**: Сервис загружает данные **только** для таймфреймов, которые существуют в таблице `timeframes` базы данных.

При попытке загрузить данные для несуществующего таймфрейма:

```bash
curl -X POST http://localhost:8001/api/v1/download \
  -d '{"ticker": "GAZP", "timeframe": "5m", ...}'
```

Ответ:
```json
{
  "success": false,
  "message": "Invalid timeframe: 5m",
  "ticker": "GAZP",
  "timeframe": "5m",
  "error": "Invalid timeframe '5m'. Valid timeframes from database: 1m, 10m, 1h, 1d, 1w, 1M, 1Q"
}
```

## Таймфреймы MOEX

Сервис автоматически маппит коды таймфреймов на интервалы MOEX ISS API:

| Код | Название | Минут | MOEX Interval |
|-----|----------|-------|---------------|
| 1m  | 1 минута | 1     | 1             |
| 10m | 10 минут | 10    | 10            |
| 1h  | 1 час    | 60    | 60            |
| 1d  | 1 день   | 1440  | 24            |
| 1w  | 1 неделя | 10080 | 7             |
| 1M  | 1 месяц  | 43200 | 31            |
| 1Q  | 1 квартал| 129600| 4             |

## Логирование

Все загрузки записываются в таблицу `download_log`:

```sql
SELECT
  ticker,
  timeframe,
  status,
  records_imported,
  duration_seconds,
  started_at,
  error
FROM download_log
ORDER BY started_at DESC
LIMIT 10;
```

## Переменные окружения

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/trading

# MOEX API
MOEX_BASE_URL=https://iss.moex.com/iss
MOEX_RATE_LIMIT=10
MOEX_TIMEOUT=30
MOEX_MAX_RETRIES=3

# Service
SERVICE_NAME=imoex
SERVICE_PORT=8001
SERVICE_HOST=0.0.0.0
LOG_LEVEL=INFO

# Redis
REDIS_URL=redis://redis:6379/1
CACHE_TTL=3600
```

## Интеграция с основным backend

IMOEX - это микросервис, который работает с **той же БД**, что и основной backend, но отвечает только за загрузку данных с MOEX.

Взаимодействие:
1. IMOEX загружает данные → таблица `ohlcv`
2. Backend читает данные из `ohlcv` для анализа и генерации сигналов
3. Оба сервиса используют общие модели: `Instrument`, `Timeframe`, `OHLCV`, `DownloadLog`

## Мониторинг

- Эндпоинт `/health` для health checks
- Логи всех операций через loguru
- Статистика загрузок через `/api/v1/download/stats`
- История операций в таблице `download_log`

## Roadmap

- [ ] Планировщик для автоматической загрузки (APScheduler)
- [ ] WebSocket для real-time уведомлений
- [ ] Caching в Redis для повторных запросов
- [ ] Metrics (Prometheus)
- [ ] Batch загрузка множества инструментов
- [ ] Инкрементальная загрузка (только новые данные)
