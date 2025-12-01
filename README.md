# Trading Signals - Система торговых сигналов

Система для анализа исторических данных российского фондового рынка и товарных фьючерсов с генерацией торговых сигналов и бэктестингом стратегий.

## Ключевые возможности

- 📊 Анализ исторических данных по множественным таймфреймам
- 🔧 Расширяемая система кастомных индикаторов
- 🎯 Индикаторы из разных таймфреймов в одной стратегии
- 🔗 Связывание тикеров с индексами
- 📈 Генерация торговых сигналов с риск-менеджментом
- 🧪 Бэктестинг стратегий
- 🌐 Веб-интерфейс для визуализации
- 💾 Миграция с CSV на базу данных

## Технологический стек

### Backend
- Python 3.11+
- FastAPI - REST API и веб-сервер
- PostgreSQL (TimescaleDB) - база данных временных рядов
- Redis - кэширование индикаторов
- SQLAlchemy + Alembic - ORM и миграции
- Pandas/Polars, NumPy - обработка данных
- TA-Lib/Pandas-TA - технические индикаторы

### Frontend
- Angular 17+ (standalone компоненты)
- TypeScript, RxJS, Angular Signals
- Apache ECharts (через ngx-echarts) - графики
- Angular Material или PrimeNG - UI компоненты

## Быстрый старт

### Предварительные требования

- Python 3.11+
- Node.js 20+
- Docker и Docker Compose (опционально)
- PostgreSQL 16+ с TimescaleDB (или через Docker)

### Установка

1. **Клонируйте репозиторий**
```bash
git clone <repository-url>
cd trading
```

2. **Настройте переменные окружения**
```bash
cp .env.example .env
# Отредактируйте .env под ваши нужды
```

3. **Запуск с Docker Compose (рекомендуется)**
```bash
docker-compose up -d
```

4. **Или запуск локально:**

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend (будет добавлено позже):**
```bash
cd frontend
npm install
ng serve
```

### Доступ к сервисам

- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Frontend (когда будет готов): http://localhost:4200
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Структура проекта

```
trading-signals/
├── backend/                # Python FastAPI бэкенд
│   ├── app/
│   │   ├── core/          # Data loading, timeframe management
│   │   ├── models/        # SQLAlchemy модели
│   │   ├── indicators/    # Технические индикаторы
│   │   ├── signals/       # Генерация сигналов
│   │   ├── strategies/    # Торговые стратегии
│   │   ├── backtesting/   # Движок бэктестинга
│   │   ├── api/v1/        # REST API endpoints
│   │   └── schemas/       # Pydantic схемы
│   └── migrations/        # Alembic миграции
│
├── frontend/              # Angular фронтенд (будет добавлен)
│   └── src/app/
│       ├── core/          # Сервисы, interceptors
│       ├── shared/        # Общие компоненты
│       └── features/      # Функциональные модули
│
├── data/                  # CSV файлы с данными
│   ├── moex/             # Московская биржа
│   ├── futures/          # Фьючерсы
│   └── indexes/          # Индексы
│
├── scripts/              # Утилиты и скрипты
├── docker-compose.yml    # Docker конфигурация
├── .env.example          # Пример переменных окружения
└── steps.md             # Детальный план разработки
```

## Основные концепции

### Multi-Timeframe поддержка

Система поддерживает анализ данных с разных таймфреймов в одной стратегии:

```python
@register_strategy
class TrendFollowing(BaseStrategy):
    def __init__(self):
        self.ma_daily = MovingAverage(period=50, timeframe="1d")
        self.rsi_hourly = RSI(period=14, timeframe="1h")

    def generate_signal(self, data: dict[str, pd.DataFrame]):
        # data содержит данные для всех таймфреймов
        daily_data = data["1d"]
        hourly_data = data["1h"]
        # ... логика стратегии
```

### Расширяемая система индикаторов

Легко добавляйте собственные индикаторы:

```python
@register_indicator
class MyIndicator(BaseIndicator):
    name = "MyIndicator"

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # Ваша логика расчёта
        return result
```

## Разработка

### План разработки

Детальный план реализации находится в [steps.md](steps.md).

**Основные фазы:**
1. ✅ Фаза 0: Инициализация проекта
2. 🔄 Фаза 1: Основа Backend (MVP)
3. ⏳ Фаза 2: API Endpoints
4. ⏳ Фаза 3: Система индикаторов
5. ⏳ Фаза 4: Timeframe Manager
6. ⏳ Фаза 5: Система стратегий
7. ⏳ Фаза 6: Генерация сигналов
8. ⏳ Фаза 7: Backtesting Engine
9. ⏳ Фазы 8-12: Frontend
10. ⏳ Фазы 13-15: Оптимизация и Deployment

### Тестирование

```bash
# Backend тесты
cd backend
pytest --cov=app

# Frontend тесты (когда будет готов)
cd frontend
ng test
```

### Линтинг и форматирование

```bash
cd backend
black app tests
isort app tests
flake8 app tests
mypy app
```

## API Документация

После запуска backend, документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Основные эндпоинты

```
GET  /health                          # Health check
GET  /api/v1/instruments              # Список инструментов
POST /api/v1/instruments              # Добавить инструмент
GET  /api/v1/data/{ticker}            # OHLCV данные
POST /api/v1/data/import              # Импорт CSV
GET  /api/v1/indicators               # Доступные индикаторы
POST /api/v1/indicators/calculate     # Расчёт индикатора
GET  /api/v1/strategies               # Список стратегий
POST /api/v1/signals/generate         # Генерация сигналов
POST /api/v1/backtest/run             # Запуск бэктеста
```

## Примеры использования

### Импорт CSV данных

```python
from app.utils.csv_importer import CSVImporter

importer = CSVImporter()
importer.import_file(
    csv_path="data/moex/GAZP_1h.csv",
    ticker="GAZP",
    timeframe="1h"
)
```

### Создание стратегии

См. примеры в `backend/app/strategies/examples/`

### Запуск бэктеста

```bash
curl -X POST http://localhost:8000/api/v1/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": 1,
    "tickers": ["GAZP"],
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 1000000
  }'
```

## Архитектура

Подробная архитектура описана в [trading_signals_arch.md](trading_signals_arch.md).

## Принципы разработки

- **SOLID принципы** - чистый и расширяемый код
- **Тестирование** - >80% покрытие кода тестами
- **Типизация** - использование type hints в Python
- **Документация** - docstrings для всех публичных функций
- **Code review** - перед каждым merge

## Лицензия

MIT

## Контакты

Для вопросов и предложений:
- GitHub Issues
- Email: support@trading-signals.local

---

**Версия:** 0.1.0
**Статус:** В разработке
**Последнее обновление:** 2025-12-01
