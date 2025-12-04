# IMOEX Service - Integration Guide

## Интеграция с основным проектом

IMOEX микросервис интегрирован в проект Trading Signals и работает совместно с основным backend.

### Архитектура

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│             │      │             │      │              │
│   Frontend  │─────▶│    Nginx    │─────▶│   Backend    │
│  (Angular)  │      │   (Port 80) │      │  (Port 8000) │
│             │      │             │      │              │
└─────────────┘      └──────┬──────┘      └───────┬──────┘
                            │                      │
                            │                      │
                            │             ┌────────▼──────┐
                            │             │               │
                            └────────────▶│ IMOEX Service │
                                          │  (Port 8001)  │
                                          │               │
                                          └───────┬───────┘
                                                  │
                    ┌─────────────────────────────┴─────┐
                    │                                   │
          ┌─────────▼──────┐              ┌────────────▼────┐
          │                │              │                 │
          │   PostgreSQL   │              │      Redis      │
          │  (TimescaleDB) │              │   (Cache/Rate)  │
          │                │              │                 │
          └────────────────┘              └─────────────────┘
```

### Маршрутизация через Nginx

Все запросы к IMOEX сервису проксируются через Nginx:

- `http://localhost/imoex/*` → `http://imoex:8001/*`
- `http://localhost/api/*` → `http://backend:8000/api/*`
- `http://localhost/*` → `http://frontend:80/*`

### Прямой доступ

При локальной разработке можно обращаться напрямую:

- IMOEX API: `http://localhost:8001`
- IMOEX Docs: `http://localhost:8001/docs`
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:80`

### Доступ через Nginx (Production)

В продакшене используйте только Nginx:

- IMOEX API: `http://localhost/imoex/api/v1/*`
- IMOEX Docs: `http://localhost/imoex/docs`
- Backend API: `http://localhost/api/v1/*`

## Workflow загрузки данных

### 1. Проверка доступных таймфреймов

```bash
curl http://localhost/imoex/api/v1/timeframes
```

### 2. Загрузка данных

```bash
curl -X POST http://localhost/imoex/api/v1/download \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "GAZP",
    "timeframe": "1h",
    "market": "stock",
    "board": "TQBR",
    "days_back": 30
  }'
```

### 3. Проверка статуса загрузки

```bash
curl http://localhost/imoex/api/v1/download/logs?ticker=GAZP
```

### 4. Использование данных в Backend

Backend автоматически использует загруженные данные из таблицы `ohlcv`:

```python
# Backend может читать данные загруженные IMOEX сервисом
from app.core.data_loader import DataLoader

loader = DataLoader(db)
df = await loader.load_from_db("GAZP", "1h")
```

## Общие таблицы БД

IMOEX и Backend используют следующие общие таблицы:

### Читает и пишет IMOEX:
- `instruments` - создаёт инструменты при первой загрузке
- `ohlcv` - записывает свечные данные
- `download_log` - логирует все загрузки

### Только читает IMOEX:
- `timeframes` - валидирует запросы на загрузку

### Читает и пишет Backend:
- `instruments` - управление инструментами
- `indexes` - биржевые индексы
- `ohlcv` - читает данные для анализа
- `signals` - генерирует торговые сигналы
- `strategies` - управление стратегиями

## Frontend интеграция

### Создание сервиса для IMOEX

```typescript
// frontend/src/app/core/services/imoex.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ImoexService {
  private apiUrl = '/imoex/api/v1';

  constructor(private http: HttpClient) {}

  getTimeframes(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/timeframes`);
  }

  downloadData(request: {
    ticker: string;
    timeframe: string;
    market?: string;
    board?: string;
    days_back?: number;
  }): Observable<any> {
    return this.http.post(`${this.apiUrl}/download`, request);
  }

  getDownloadLogs(params?: {
    ticker?: string;
    timeframe?: string;
    status?: string;
    limit?: number;
  }): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/download/logs`, { params });
  }

  getDownloadStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/download/stats`);
  }
}
```

### Использование в компоненте

```typescript
// frontend/src/app/features/data-loader/data-loader.component.ts
import { Component, OnInit } from '@angular/core';
import { ImoexService } from '@core/services/imoex.service';

@Component({
  selector: 'app-data-loader',
  template: `
    <h2>Загрузка данных с MOEX</h2>

    <form (ngSubmit)="onSubmit()">
      <input [(ngModel)]="ticker" placeholder="Тикер (GAZP)" />

      <select [(ngModel)]="timeframe">
        <option *ngFor="let tf of timeframes" [value]="tf.code">
          {{ tf.name }}
        </option>
      </select>

      <input type="number" [(ngModel)]="daysBack" placeholder="Дней назад" />

      <button type="submit">Загрузить</button>
    </form>

    <div *ngIf="result">
      {{ result.message }}
      <p>Загружено записей: {{ result.records_imported }}</p>
    </div>
  `
})
export class DataLoaderComponent implements OnInit {
  timeframes: any[] = [];
  ticker = 'GAZP';
  timeframe = '1h';
  daysBack = 30;
  result: any = null;

  constructor(private imoexService: ImoexService) {}

  ngOnInit() {
    this.imoexService.getTimeframes().subscribe(
      timeframes => this.timeframes = timeframes
    );
  }

  onSubmit() {
    this.imoexService.downloadData({
      ticker: this.ticker,
      timeframe: this.timeframe,
      days_back: this.daysBack
    }).subscribe(
      result => this.result = result,
      error => console.error('Download failed:', error)
    );
  }
}
```

## Environment Variables

Добавьте в `.env`:

```env
# IMOEX Service
IMOEX_PORT=8001
```

## Docker Compose

IMOEX сервис уже добавлен в `docker-compose.yml`:

```yaml
imoex:
  build:
    context: ./imoex
    dockerfile: Dockerfile
  container_name: trading_imoex
  ports:
    - "${IMOEX_PORT:-8001}:8001"
  depends_on:
    - postgres
    - redis
```

## Мониторинг

### Health Checks

```bash
# IMOEX service
curl http://localhost/imoex/health

# Database connection
curl http://localhost/imoex/health/db
```

### Логи

```bash
# Docker logs
docker logs trading_imoex -f

# Download stats
curl http://localhost/imoex/api/v1/download/stats
```

## Типичные сценарии

### 1. Первоначальная загрузка данных для инструмента

```bash
# Загрузить GAZP за последний год (1d)
curl -X POST http://localhost/imoex/api/v1/download \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "GAZP",
    "timeframe": "1d",
    "days_back": 365
  }'

# Загрузить часовые данные за последний месяц
curl -X POST http://localhost/imoex/api/v1/download \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "GAZP",
    "timeframe": "1h",
    "days_back": 30
  }'
```

### 2. Обновление данных для существующего инструмента

```bash
# Загрузить последние 3 дня
curl -X POST http://localhost/imoex/api/v1/download \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "GAZP",
    "timeframe": "1d",
    "days_back": 3
  }'
```

### 3. Загрузка фьючерсов

```bash
curl -X POST http://localhost/imoex/api/v1/download \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "SiZ4",
    "timeframe": "1h",
    "market": "futures",
    "board": "RFUD",
    "days_back": 7
  }'
```

## Troubleshooting

### IMOEX сервис не запускается

```bash
# Проверить логи
docker logs trading_imoex

# Проверить доступность БД
docker exec trading_imoex curl http://localhost:8001/health/db
```

### Таймфрейм не найден

Убедитесь что таймфрейм существует в БД:

```sql
SELECT * FROM timeframes WHERE is_active = 1;
```

Если таймфреймов нет, выполните миграцию:

```bash
cd backend
alembic upgrade head
```

### Данные не загружаются

1. Проверьте доступность MOEX API:
   ```bash
   curl https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/GAZP/candles.json?interval=60
   ```

2. Проверьте логи загрузок:
   ```bash
   curl http://localhost/imoex/api/v1/download/logs?status=failed
   ```

3. Проверьте параметры:
   - Корректность тикера
   - Валидность market и board
   - Наличие таймфрейма в БД

## Best Practices

1. **Начинайте с дневных данных** (`1d`) - быстрее загружаются
2. **Затем загружайте часовые** (`1h`) для нужного периода
3. **Минутные данные** (`1m`, `10m`) - только для краткосрочного анализа
4. **Используйте background загрузку** для больших объёмов:
   ```bash
   curl -X POST http://localhost/imoex/api/v1/download/background \
     -H "Content-Type: application/json" \
     -d '{"ticker": "GAZP", "timeframe": "1m", "days_back": 7}'
   ```
5. **Мониторьте rate limit** - MOEX ISS API ограничивает 10 запросов/сек
6. **Проверяйте download_log** для отладки проблем

## Security

- Rate limiting настроен в nginx (10 req/s для API)
- MOEX ISS API имеет свои ограничения
- Используйте переменные окружения для чувствительных данных
- В продакшене настройте CORS правильно (не используйте `*`)
