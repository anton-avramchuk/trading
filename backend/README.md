# Trading Signals Backend

Backend для системы анализа торговых сигналов и бэктестинга.

## Технологии

- Python 3.11+
- FastAPI
- PostgreSQL + TimescaleDB
- Redis
- SQLAlchemy + Alembic
- Pandas + NumPy
- TA-Lib / Pandas-TA

## Установка

### 1. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте переменные:

```bash
cp ../.env.example ../.env
```

### 4. Запуск PostgreSQL и Redis

Используйте Docker Compose из корня проекта:

```bash
cd ..
docker-compose up -d postgres redis
cd backend
```

### 5. Применение миграций

```bash
alembic upgrade head
```

## Запуск

### Режим разработки

```bash
uvicorn app.main:app --reload
```

или

```bash
python -m app.main
```

API будет доступен по адресу: http://localhost:8000

### Документация API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Работа с миграциями

### Создание новой миграции

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1
```

### История миграций

```bash
alembic history
```

## Структура проекта

```
backend/
├── app/
│   ├── core/              # Основная бизнес-логика
│   ├── models/            # SQLAlchemy модели
│   ├── indicators/        # Технические индикаторы
│   ├── signals/           # Генерация сигналов
│   ├── strategies/        # Торговые стратегии
│   ├── backtesting/       # Бэктестинг
│   ├── api/v1/            # REST API endpoints
│   ├── schemas/           # Pydantic схемы
│   ├── utils/             # Утилиты
│   ├── config.py          # Конфигурация
│   └── main.py            # Точка входа
├── migrations/            # Alembic миграции
├── tests/                 # Тесты
├── requirements.txt       # Python зависимости
└── pyproject.toml         # Конфигурация проекта
```

## Тестирование

### Запуск всех тестов

```bash
pytest
```

### Запуск с покрытием

```bash
pytest --cov=app --cov-report=html
```

### Запуск конкретного теста

```bash
pytest tests/unit/test_models.py
```

## Линтинг и форматирование

### Black (форматирование)

```bash
black app tests
```

### isort (сортировка импортов)

```bash
isort app tests
```

### Flake8 (линтинг)

```bash
flake8 app tests
```

### MyPy (проверка типов)

```bash
mypy app
```

## Docker

### Сборка образа

```bash
docker build -t trading-signals-backend .
```

### Запуск контейнера

```bash
docker run -p 8000:8000 --env-file ../.env trading-signals-backend
```

## Основные эндпоинты

- `GET /` - Информация о сервисе
- `GET /health` - Health check
- `GET /api/v1/instruments` - Список инструментов
- `GET /api/v1/data/{ticker}` - OHLCV данные
- `GET /api/v1/indicators` - Доступные индикаторы
- `POST /api/v1/signals/generate` - Генерация сигналов
- `POST /api/v1/backtest/run` - Запуск бэктеста

## Разработка

### Добавление нового индикатора

1. Создайте файл в `app/indicators/custom/`
2. Наследуйте `BaseIndicator`
3. Используйте декоратор `@register_indicator`
4. Реализуйте метод `calculate()`

### Добавление новой стратегии

1. Создайте файл в `app/strategies/examples/`
2. Наследуйте `BaseStrategy`
3. Используйте декоратор `@register_strategy`
4. Реализуйте метод `generate_signal()`

## Поддержка

Для вопросов и проблем создавайте issue в репозитории.
