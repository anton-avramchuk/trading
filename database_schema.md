# 🗄️ Схема базы данных Trading Signals v3

## 📊 Обзор

База данных PostgreSQL с TimescaleDB для временных рядов. Версия схемы: **v3** (2025-01-04)

**Основные изменения v3:**
- ✅ Добавлена нормализация валют (Currency)
- ✅ Добавлена нормализация стран (Country)
- ✅ Добавлена таблица бэктестов (Backtest)
- ✅ Расширены поля Instrument (isin, board, lot_size, tick_size, metadata)
- ✅ Добавлены FK для Currency в Instrument и Index
- ✅ Добавлен FK для Country в Index

## 📋 Список таблиц

| № | Таблица | Описание | Записей (примерно) |
|---|---------|----------|-------------------|
| 1 | currencies | Валюты (ISO 4217) | 9+ |
| 2 | countries | Страны (ISO 3166) | 7+ |
| 3 | timeframes | Таймфреймы | 7 |
| 4 | indexes | Биржевые индексы | 10-50 |
| 5 | instruments | Финансовые инструменты | 100-1000 |
| 6 | ohlcv | OHLCV свечные данные | 1M-100M |
| 7 | strategies | Торговые стратегии | 10-100 |
| 8 | signals | Торговые сигналы | 10K-100K |
| 9 | backtests | Результаты бэктестов | 100-10K |
| 10 | download_log | Логи загрузок MOEX | 1K-10K |

## 🔗 ER-диаграмма (упрощенная)

```
currencies ──┐
             ├──> instruments ──> ohlcv
countries ───┤                 └──> signals ──> strategies ──> backtests
             └──> indexes ────┘               timeframes ────┘
                                                     └──> download_log
```

## 📋 Детальное описание таблиц

### 1. currencies (Валюты)

Справочник валют по ISO 4217.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| code | VARCHAR(3) UK | Код валюты (RUB, USD, EUR) |
| numeric_code | VARCHAR(3) | Цифровой код ISO 4217 |
| name | VARCHAR(100) | Название (Российский рубль) |
| name_en | VARCHAR(100) | Название EN (Russian Ruble) |
| symbol | VARCHAR(10) | Символ (₽, $, €) |
| decimal_places | INTEGER | Десятичных знаков (обычно 2) |
| is_active | INTEGER | Активна ли (1/0) |
| created_at | DATETIME | Дата создания |

**Начальные данные:** RUB, USD, EUR, CNY, GBP, JPY, BTC, ETH, USDT

### 2. countries (Страны)

Справочник стран по ISO 3166.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| code | VARCHAR(2) UK | Код страны (RU, US, GB) |
| code3 | VARCHAR(3) | Код alpha-3 (RUS, USA, GBR) |
| name | VARCHAR(100) | Название (Россия) |
| name_en | VARCHAR(100) | Название EN (Russia) |
| region | VARCHAR(50) | Регион (Europe, Asia, Americas) |
| is_active | INTEGER | Активна ли (1/0) |
| created_at | DATETIME | Дата создания |

**Начальные данные:** RU, US, GB, CN, JP, DE, FR

### 3. timeframes (Таймфреймы)

Справочник допустимых таймфреймов.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| code | VARCHAR(10) UK | Код (1m, 10m, 1h, 1d, 1w, 1M, 1Q) |
| name | VARCHAR(50) | Название (1 минута, 1 день) |
| description | TEXT | Описание |
| minutes | INTEGER | Количество минут |
| moex_interval | INTEGER | Интервал MOEX API |
| created_at | DATETIME | Дата создания |
| is_active | INTEGER | Активен ли (1/0) |

**Начальные данные:** 7 таймфреймов (1m, 10m, 1h, 1d, 1w, 1M, 1Q)

### 4. indexes (Биржевые индексы)

Биржевые индексы (IMOEX, RTS, S&P500).

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| ticker | VARCHAR(20) UK | Тикер (IMOEX, SPX) |
| name | VARCHAR(255) | Название |
| description | VARCHAR(1000) | Описание |
| currency_id | INTEGER FK | Валюта индекса → currencies.id |
| country_id | INTEGER FK | Страна индекса → countries.id |
| created_at | DATETIME | Дата создания |
| updated_at | DATETIME | Дата обновления |

**Relationships:**
- → instruments (1:N)
- → Currency (N:1)
- → Country (N:1)

### 5. instruments (Финансовые инструменты)

Центральная таблица для всех торгуемых инструментов.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| ticker | VARCHAR(20) UK | Тикер (GAZP, SBER, AAPL) |
| name | VARCHAR(255) | Полное название |
| market | VARCHAR(50) | Биржа (MOEX, NYSE) |
| instrument_type | VARCHAR(50) | Тип (stock, future, index) |
| index_id | INTEGER FK | ID индекса → indexes.id |
| currency_id | INTEGER FK | Валюта → currencies.id |
| isin | VARCHAR(12) | ISIN код (RU0007661625) |
| board | VARCHAR(50) | Режим торгов (TQBR, RFUD) |
| lot_size | INTEGER | Размер лота |
| tick_size | VARCHAR(20) | Шаг цены |
| metadata | JSON | Дополнительные данные |
| created_at | DATETIME | Дата создания |
| updated_at | DATETIME | Дата обновления |

**Relationships:**
- → Index (N:1)
- → Currency (N:1)
- → ohlcv (1:N, CASCADE)
- → signals (1:N, CASCADE)
- → download_log (1:N, SET NULL)

### 6. ohlcv (Свечные данные)

Исторические OHLCV данные (TimescaleDB hypertable).

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGINT PK | Первичный ключ |
| instrument_id | INTEGER FK | → instruments.id (CASCADE) |
| timeframe_id | INTEGER FK | → timeframes.id |
| timeframe | VARCHAR(10) | Код таймфрейма (backward compat) |
| timestamp | DATETIME | Временная метка (UTC) |
| open | FLOAT | Цена открытия |
| high | FLOAT | Максимальная цена |
| low | FLOAT | Минимальная цена |
| close | FLOAT | Цена закрытия |
| volume | BIGINT | Объём торгов |
| created_at | DATETIME | Дата создания |

**Constraints:**
- UNIQUE (instrument_id, timeframe_id, timestamp)
- INDEX (instrument_id, timeframe_id, timestamp)

**TimescaleDB:**
- Hypertable partitioned by timestamp
- Compression policy: 3 months
- Retention policy: 5 years

### 7. strategies (Торговые стратегии)

Конфигурация торговых стратегий.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| name | VARCHAR(255) UK | Название стратегии |
| description | TEXT | Описание логики |
| config | JSON | Конфигурация (индикаторы, правила) |
| is_active | INTEGER | Активна ли (1/0) |
| created_at | DATETIME | Дата создания |
| updated_at | DATETIME | Дата обновления |

**Relationships:**
- → signals (1:N)
- → backtests (1:N, CASCADE)

### 8. signals (Торговые сигналы)

Сигналы, сгенерированные стратегиями.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| instrument_id | INTEGER FK | → instruments.id (CASCADE) |
| strategy_id | INTEGER FK | → strategies.id (SET NULL) |
| strategy_name | VARCHAR(255) | Название стратегии (backward compat) |
| signal_type | VARCHAR(10) | Тип (BUY, SELL, HOLD) |
| timestamp | DATETIME | Время сигнала (UTC) |
| price | FLOAT | Цена в момент сигнала |
| confidence | FLOAT | Уверенность (0.0-1.0) |
| position_size | FLOAT | Размер позиции |
| stop_loss | FLOAT | Стоп-лосс |
| take_profit | FLOAT | Тейк-профит |
| created_at | DATETIME | Дата создания |

**Relationships:**
- → Instrument (N:1, CASCADE)
- → Strategy (N:1, SET NULL)

### 9. backtests (Результаты бэктестов)

Результаты бэктестинга стратегий.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| strategy_id | INTEGER FK | → strategies.id (CASCADE) |
| instruments | JSON | Список тикеров ["GAZP", "SBER"] |
| timeframe_id | INTEGER FK | → timeframes.id |
| start_date | DATETIME | Начало периода |
| end_date | DATETIME | Конец периода |
| initial_capital | FLOAT | Начальный капитал |
| final_capital | FLOAT | Финальный капитал |
| total_return | FLOAT | Общая доходность (%) |
| annual_return | FLOAT | Годовая доходность (%) |
| sharpe_ratio | FLOAT | Коэффициент Шарпа |
| max_drawdown | FLOAT | Максимальная просадка (%) |
| total_trades | INTEGER | Всего сделок |
| winning_trades | INTEGER | Прибыльных сделок |
| losing_trades | INTEGER | Убыточных сделок |
| win_rate | FLOAT | Процент прибыльных (%) |
| avg_win | FLOAT | Средняя прибыль |
| avg_loss | FLOAT | Средний убыток |
| profit_factor | FLOAT | Profit Factor |
| metrics | JSON | Детальные метрики |
| status | VARCHAR(20) | Статус (pending, running, completed, failed) |
| started_at | DATETIME | Время начала |
| completed_at | DATETIME | Время завершения |
| error | TEXT | Текст ошибки |
| created_at | DATETIME | Дата создания |

**Relationships:**
- → Strategy (N:1, CASCADE)
- → Timeframe (N:1)

### 10. download_log (Логи загрузок)

Отслеживание загрузок данных с MOEX ISS API.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Первичный ключ |
| instrument_id | INTEGER FK | → instruments.id (SET NULL) |
| timeframe_id | INTEGER FK | → timeframes.id |
| ticker | VARCHAR(20) | Тикер |
| timeframe | VARCHAR(10) | Код таймфрейма |
| market | VARCHAR(50) | Рынок (stock, futures) |
| board | VARCHAR(50) | Режим торгов (TQBR, RFUD) |
| status | VARCHAR(20) | Статус (pending, running, completed, failed) |
| records_imported | INTEGER | Загружено записей |
| start_date | DATETIME | Начало периода |
| end_date | DATETIME | Конец периода |
| started_at | DATETIME | Время начала |
| completed_at | DATETIME | Время завершения |
| duration_seconds | FLOAT | Длительность (сек) |
| error | TEXT | Текст ошибки |
| metadata | JSON | Дополнительная информация |
| created_at | DATETIME | Дата создания |

**Relationships:**
- → Instrument (N:1, SET NULL)
- → Timeframe (N:1)

## 🔗 Foreign Keys Summary

| From | Column | To | OnDelete |
|------|--------|----|---------:|
| instruments | index_id | indexes.id | SET NULL |
| instruments | currency_id | currencies.id | SET NULL |
| indexes | currency_id | currencies.id | SET NULL |
| indexes | country_id | countries.id | SET NULL |
| ohlcv | instrument_id | instruments.id | CASCADE |
| ohlcv | timeframe_id | timeframes.id | RESTRICT |
| signals | instrument_id | instruments.id | CASCADE |
| signals | strategy_id | strategies.id | SET NULL |
| backtests | strategy_id | strategies.id | CASCADE |
| backtests | timeframe_id | timeframes.id | RESTRICT |
| download_log | instrument_id | instruments.id | SET NULL |
| download_log | timeframe_id | timeframes.id | RESTRICT |

## 📈 Примеры запросов

### Получить инструмент с валютой и страной индекса:
```sql
SELECT
    i.ticker,
    i.name,
    c.code as currency,
    idx.name as index_name,
    cnt.name as country
FROM instruments i
LEFT JOIN currencies c ON i.currency_id = c.id
LEFT JOIN indexes idx ON i.index_id = idx.id
LEFT JOIN countries cnt ON idx.country_id = cnt.id
WHERE i.ticker = 'GAZP';
```

### Получить топ стратегий по Sharpe Ratio:
```sql
SELECT
    s.name,
    AVG(b.sharpe_ratio) as avg_sharpe,
    AVG(b.total_return) as avg_return,
    COUNT(*) as backtest_count
FROM strategies s
JOIN backtests b ON s.id = b.strategy_id
WHERE b.status = 'completed'
GROUP BY s.id, s.name
ORDER BY avg_sharpe DESC
LIMIT 10;
```

### Статистика по валютам:
```sql
SELECT
    c.code,
    c.symbol,
    COUNT(i.id) as instrument_count
FROM currencies c
LEFT JOIN instruments i ON c.id = i.currency_id
GROUP BY c.id, c.code, c.symbol
ORDER BY instrument_count DESC;
```

## 🔄 Миграции

### Применение миграций:
```bash
cd backend
alembic upgrade head     # Применить все миграции
alembic current          # Текущая версия
alembic history          # История
alembic downgrade -1     # Откатить последнюю
```

### Список миграций:
1. `001_initial_schema.py` - Базовые таблицы
2. `002_add_strategies.py` - Таблица strategies
3. `003_add_timeframes_and_fks.py` - Таблица timeframes и FK
4. `004_add_currencies_countries_backtests.py` - **v3: Currency, Country, Backtest**

## 📊 Оценка размеров БД

| Таблица | Записей | Размер |
|---------|---------|--------|
| currencies | 9 | < 1 KB |
| countries | 7 | < 1 KB |
| timeframes | 7 | < 1 KB |
| indexes | 10-50 | < 100 KB |
| instruments | 100-1000 | 100 KB - 1 MB |
| ohlcv (1d) | 250K - 2.5M | 50 MB - 500 MB |
| ohlcv (1h) | 6M - 60M | 1 GB - 10 GB |
| signals | 10K - 100K | 5 MB - 50 MB |
| strategies | 10-100 | < 1 MB |
| backtests | 100-10K | 1 MB - 100 MB |
| download_log | 1K - 10K | 1 MB - 10 MB |

**Итого:** 1-20 GB (зависит от истории и количества инструментов)

## 🎯 Преимущества схемы v3

### 1. Нормализация валют
- ✅ ISO 4217 стандарт
- ✅ Символы для UI (₽, $, €)
- ✅ Decimal places для форматирования
- ✅ Поддержка криптовалют (BTC, ETH, USDT)

### 2. Нормализация стран
- ✅ ISO 3166 стандарт
- ✅ Регионы для группировки
- ✅ Поддержка 2 и 3-буквенных кодов

### 3. Backtests таблица
- ✅ Хранение результатов бэктестов
- ✅ Метрики: Sharpe, Drawdown, Win Rate, Profit Factor
- ✅ Сравнение стратегий
- ✅ Оптимизация параметров

### 4. Расширенные поля Instrument
- ✅ ISIN для международной идентификации
- ✅ Board для специфики биржи
- ✅ Lot size и tick size для расчётов
- ✅ Metadata JSON для гибкости

## 🔐 Безопасность

Рекомендации:
- Разные пользователи для backend и imoex сервисов
- SSL/TLS для соединений
- Regular backups
- Audit logging

```sql
-- Пример создания пользователя для IMOEX
CREATE USER imoex_service WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON instruments TO imoex_service;
GRANT SELECT, INSERT ON ohlcv TO imoex_service;
GRANT SELECT ON timeframes, currencies TO imoex_service;
GRANT ALL ON download_log TO imoex_service;
```

## 📝 Changelog

### v3 (2025-01-04)
- ➕ Добавлена таблица currencies (9 валют)
- ➕ Добавлена таблица countries (7 стран)
- ➕ Добавлена таблица backtests (результаты бэктестов)
- 🔄 Обновлена Instrument: + currency_id, isin, board, lot_size, tick_size, metadata
- 🔄 Обновлена Index: + currency_id, country_id
- 🔄 Обновлена Strategy: + relationship backtests

### v2 (2024-12-20)
- ➕ Добавлена таблица timeframes
- ➕ Добавлена таблица download_log
- 🔄 Обновлена OHLCV: + timeframe_id FK
- 🔄 Обновлена Signal: + strategy_id FK

### v1 (2024-12-01)
- ➕ Базовые таблицы: instruments, ohlcv, signals, strategies, indexes
