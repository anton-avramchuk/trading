import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { BacktestingService } from '../../core/services/backtesting.service';
import { StrategiesService } from '../../core/services/strategies.service';
import { InstrumentsService } from '../../core/services/instruments.service';
import { BacktestConfig, BacktestResult } from '../../core/models/backtest.model';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';

/**
 * Компонент бэктестинга
 * Запуск и просмотр результатов бэктестов
 */
@Component({
  selector: 'app-backtesting',
  standalone: true,
  imports: [CommonModule, FormsModule, LoaderComponent, ErrorMessageComponent],
  template: `
    <div class="page">
      <header class="page-header">
        <div>
          <h2>Бэктестинг</h2>
          <p>Тестирование стратегий на исторических данных</p>
        </div>
      </header>

      <!-- Форма запуска бэктеста -->
      <div class="form-card">
        <h3>Запуск бэктеста</h3>
        <form (ngSubmit)="runBacktest()">
          <div class="form-grid">
            <div class="form-group">
              <label for="strategy">Стратегия *</label>
              <select id="strategy" [(ngModel)]="config.strategy_name" name="strategy" required>
                <option value="">Выберите стратегию</option>
                @for (strategy of strategies(); track strategy.name) {
                  <option [value]="strategy.name">{{ strategy.name }}</option>
                }
              </select>
            </div>

            <div class="form-group">
              <label for="ticker">Тикер *</label>
              <select id="ticker" [(ngModel)]="config.ticker" name="ticker" required>
                <option value="">Выберите тикер</option>
                @for (instrument of instruments(); track instrument.ticker) {
                  <option [value]="instrument.ticker">{{ instrument.ticker }} - {{ instrument.name }}</option>
                }
              </select>
            </div>

            <div class="form-group">
              <label for="start">Начальная дата *</label>
              <input type="date" id="start" [(ngModel)]="config.start_date" name="start" required />
            </div>

            <div class="form-group">
              <label for="end">Конечная дата *</label>
              <input type="date" id="end" [(ngModel)]="config.end_date" name="end" required />
            </div>

            <div class="form-group">
              <label for="capital">Начальный капитал *</label>
              <input type="number" id="capital" [(ngModel)]="config.initial_capital" name="capital" required min="0" step="1000" />
            </div>

            <div class="form-group">
              <label for="commission">Комиссия (%) *</label>
              <input type="number" id="commission" [(ngModel)]="config.commission" name="commission" required min="0" max="100" step="0.01" />
            </div>

            <div class="form-group">
              <label for="slippage">Проскальзывание (%) *</label>
              <input type="number" id="slippage" [(ngModel)]="config.slippage" name="slippage" required min="0" max="100" step="0.01" />
            </div>

            <div class="form-group">
              <label for="risk">
                <input type="checkbox" id="risk" [(ngModel)]="config.use_risk_manager" name="risk" />
                Использовать риск-менеджмент
              </label>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-lg" [disabled]="running()">
              {{ running() ? 'Запуск бэктеста...' : 'Запустить бэктест' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Результаты бэктеста -->
      @if (running()) {
        <app-loader [message]="'Выполнение бэктеста...'" />
      } @else if (error()) {
        <app-error-message
          [title]="'Ошибка бэктеста'"
          [message]="error()!"
          (retry)="runBacktest()" />
      } @else if (result()) {
        <div class="results">
          <!-- Метрики -->
          <div class="metrics-card">
            <h3>Результаты бэктеста</h3>
            <div class="metrics-grid">
              <div class="metric">
                <div class="metric-label">Общая доходность</div>
                <div class="metric-value positive">
                  {{ result()!.metrics.total_return.toFixed(2) }}
                  ({{ result()!.metrics.total_return_percent.toFixed(2) }}%)
                </div>
              </div>

              <div class="metric">
                <div class="metric-label">Sharpe Ratio</div>
                <div class="metric-value">{{ result()!.metrics.sharpe_ratio.toFixed(2) }}</div>
              </div>

              <div class="metric">
                <div class="metric-label">Max Drawdown</div>
                <div class="metric-value negative">
                  {{ result()!.metrics.max_drawdown.toFixed(2) }}
                  ({{ result()!.metrics.max_drawdown_percent.toFixed(2) }}%)
                </div>
              </div>

              <div class="metric">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{{ (result()!.metrics.win_rate * 100).toFixed(1) }}%</div>
              </div>

              <div class="metric">
                <div class="metric-label">Profit Factor</div>
                <div class="metric-value">{{ result()!.metrics.profit_factor.toFixed(2) }}</div>
              </div>

              <div class="metric">
                <div class="metric-label">Всего сделок</div>
                <div class="metric-value">{{ result()!.metrics.total_trades }}</div>
              </div>

              <div class="metric">
                <div class="metric-label">Прибыльных сделок</div>
                <div class="metric-value positive">{{ result()!.metrics.winning_trades }}</div>
              </div>

              <div class="metric">
                <div class="metric-label">Убыточных сделок</div>
                <div class="metric-value negative">{{ result()!.metrics.losing_trades }}</div>
              </div>

              <div class="metric">
                <div class="metric-label">Средняя прибыль</div>
                <div class="metric-value positive">
                  {{ result()!.metrics.avg_win.toFixed(2) }}
                  ({{ result()!.metrics.avg_win_percent.toFixed(2) }}%)
                </div>
              </div>

              <div class="metric">
                <div class="metric-label">Средний убыток</div>
                <div class="metric-value negative">
                  {{ result()!.metrics.avg_loss.toFixed(2) }}
                  ({{ result()!.metrics.avg_loss_percent.toFixed(2) }}%)
                </div>
              </div>

              <div class="metric">
                <div class="metric-label">Наибольшая прибыль</div>
                <div class="metric-value positive">{{ result()!.metrics.largest_win.toFixed(2) }}</div>
              </div>

              <div class="metric">
                <div class="metric-label">Наибольший убыток</div>
                <div class="metric-value negative">{{ result()!.metrics.largest_loss.toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <!-- Сделки -->
          @if (result()!.trades.length > 0) {
            <div class="trades-card">
              <h3>Сделки ({{ result()!.trades.length }})</h3>
              <div class="table-wrapper">
                <table class="trades-table">
                  <thead>
                    <tr>
                      <th>Вход</th>
                      <th>Выход</th>
                      <th>Сторона</th>
                      <th>Размер</th>
                      <th>Цена входа</th>
                      <th>Цена выхода</th>
                      <th>P&L</th>
                      <th>P&L %</th>
                      <th>Длительность</th>
                      <th>Причина выхода</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (trade of result()!.trades; track $index) {
                      <tr>
                        <td>{{ formatDate(trade.entry_date) }}</td>
                        <td>{{ formatDate(trade.exit_date) }}</td>
                        <td>
                          <span class="side" [class]="'side-' + trade.side.toLowerCase()">
                            {{ trade.side }}
                          </span>
                        </td>
                        <td>{{ trade.size }}</td>
                        <td class="price">{{ trade.entry_price.toFixed(2) }}</td>
                        <td class="price">{{ trade.exit_price.toFixed(2) }}</td>
                        <td [class]="trade.pnl >= 0 ? 'positive' : 'negative'">
                          {{ trade.pnl.toFixed(2) }}
                        </td>
                        <td [class]="trade.pnl_percent >= 0 ? 'positive' : 'negative'">
                          {{ trade.pnl_percent.toFixed(2) }}%
                        </td>
                        <td>{{ trade.duration_bars }} баров</td>
                        <td class="exit-reason">{{ trade.exit_reason }}</td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
            </div>
          }
        </div>
      }
    </div>
  `,
  styleUrl: './backtesting.component.scss'
})
export class BacktestingComponent implements OnInit {
  private backtestingService = inject(BacktestingService);
  private strategiesService = inject(StrategiesService);
  private instrumentsService = inject(InstrumentsService);

  // State
  running = signal(false);
  error = signal<string | null>(null);
  result = signal<BacktestResult | null>(null);
  strategies = signal<any[]>([]);
  instruments = signal<any[]>([]);

  // Config
  config: BacktestConfig = {
    strategy_name: '',
    ticker: '',
    start_date: '',
    end_date: '',
    initial_capital: 100000,
    commission: 0.05,
    slippage: 0.01,
    use_risk_manager: true
  };

  ngOnInit(): void {
    this.loadStrategies();
    this.loadInstruments();
  }

  /**
   * Загрузка стратегий
   */
  loadStrategies(): void {
    this.strategiesService.getStrategies().subscribe({
      next: (data) => {
        this.strategies.set(data.strategies);
      },
      error: (err) => {
        console.error('Load strategies error:', err);
      }
    });
  }

  /**
   * Загрузка инструментов
   */
  loadInstruments(): void {
    this.instrumentsService.getInstruments(0, 1000).subscribe({
      next: (data) => {
        this.instruments.set(data);
      },
      error: (err) => {
        console.error('Load instruments error:', err);
      }
    });
  }

  /**
   * Запустить бэктест
   */
  runBacktest(): void {
    this.running.set(true);
    this.error.set(null);
    this.result.set(null);

    this.backtestingService.runBacktest(this.config).subscribe({
      next: (response) => {
        if (response.status === 'completed' && response.result) {
          this.result.set(response.result);
        } else if (response.status === 'failed') {
          this.error.set(response.error || 'Бэктест завершился с ошибкой');
        }
        this.running.set(false);
      },
      error: (err) => {
        console.error('Backtest error:', err);
        this.error.set(err.message || 'Ошибка при выполнении бэктеста');
        this.running.set(false);
      }
    });
  }

  /**
   * Форматировать дату
   */
  formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  }
}
