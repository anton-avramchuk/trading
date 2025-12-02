import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { SignalsService } from '../../core/services/signals.service';
import { StrategiesService } from '../../core/services/strategies.service';
import { InstrumentsService } from '../../core/services/instruments.service';
import { Signal, SignalGenerateRequest } from '../../core/models/signal.model';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';

/**
 * Компонент работы с сигналами
 * Генерация и просмотр торговых сигналов
 */
@Component({
  selector: 'app-signals',
  standalone: true,
  imports: [CommonModule, FormsModule, LoaderComponent, ErrorMessageComponent],
  template: `
    <div class="page">
      <header class="page-header">
        <div>
          <h2>Торговые сигналы</h2>
          <p>Генерация и анализ торговых сигналов</p>
        </div>
        <button class="btn btn-primary" (click)="showGenerateForm()">
          + Сгенерировать сигналы
        </button>
      </header>

      <!-- Форма генерации -->
      @if (showForm()) {
        <div class="form-card">
          <h3>Генерация сигналов</h3>
          <form (ngSubmit)="generateSignals()">
            <div class="form-grid">
              <div class="form-group">
                <label for="strategy">Стратегия *</label>
                <select id="strategy" [(ngModel)]="formData.strategy_name" name="strategy" required>
                  <option value="">Выберите стратегию</option>
                  @for (strategy of strategies(); track strategy.name) {
                    <option [value]="strategy.name">{{ strategy.name }}</option>
                  }
                </select>
              </div>

              <div class="form-group">
                <label for="ticker">Тикер *</label>
                <select id="ticker" [(ngModel)]="formData.ticker" name="ticker" required>
                  <option value="">Выберите тикер</option>
                  @for (instrument of instruments(); track instrument.ticker) {
                    <option [value]="instrument.ticker">{{ instrument.ticker }} - {{ instrument.name }}</option>
                  }
                </select>
              </div>

              <div class="form-group">
                <label for="start">Начальная дата</label>
                <input type="date" id="start" [(ngModel)]="formData.start_date" name="start" />
              </div>

              <div class="form-group">
                <label for="end">Конечная дата</label>
                <input type="date" id="end" [(ngModel)]="formData.end_date" name="end" />
              </div>

              <div class="form-group">
                <label for="risk">
                  <input type="checkbox" id="risk" [(ngModel)]="formData.use_risk_manager" name="risk" />
                  Использовать риск-менеджмент
                </label>
              </div>

              <div class="form-group">
                <label for="save">
                  <input type="checkbox" id="save" [(ngModel)]="formData.save_to_db" name="save" />
                  Сохранить в базу данных
                </label>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-secondary" (click)="cancelGenerate()">
                Отмена
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="generating()">
                {{ generating() ? 'Генерация...' : 'Сгенерировать' }}
              </button>
            </div>
          </form>
        </div>
      }

      <!-- Список сигналов -->
      @if (loading()) {
        <app-loader [message]="'Загрузка сигналов...'" />
      } @else if (error()) {
        <app-error-message
          [title]="'Ошибка загрузки'"
          [message]="error()!"
          (retry)="loadSignals()" />
      } @else {
        <div class="content">
          <!-- Фильтры -->
          <div class="filters">
            <select [(ngModel)]="filterStrategy" (ngModelChange)="applyFilters()" class="filter-select">
              <option value="">Все стратегии</option>
              @for (strategy of strategies(); track strategy.name) {
                <option [value]="strategy.name">{{ strategy.name }}</option>
              }
            </select>

            <select [(ngModel)]="filterType" (ngModelChange)="applyFilters()" class="filter-select">
              <option value="">Все типы</option>
              <option value="BUY">Покупка (BUY)</option>
              <option value="SELL">Продажа (SELL)</option>
              <option value="HOLD">Удержание (HOLD)</option>
            </select>

            <input
              type="text"
              [(ngModel)]="filterTicker"
              (ngModelChange)="applyFilters()"
              placeholder="Фильтр по тикеру"
              class="filter-input" />
          </div>

          <!-- Таблица сигналов -->
          @if (filteredSignals().length === 0) {
            <div class="empty-state">
              <p>Нет сигналов</p>
              <button class="btn btn-primary" (click)="showGenerateForm()">
                Сгенерировать сигналы
              </button>
            </div>
          } @else {
            <div class="table-card">
              <div class="table-header">
                <h4>Сигналы ({{ filteredSignals().length }})</h4>
              </div>
              <div class="table-wrapper">
                <table class="signals-table">
                  <thead>
                    <tr>
                      <th>Дата/Время</th>
                      <th>Тикер</th>
                      <th>Стратегия</th>
                      <th>Тип</th>
                      <th>Цена</th>
                      <th>Уверенность</th>
                      <th>Размер позиции</th>
                      <th>Stop Loss</th>
                      <th>Take Profit</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (signal of filteredSignals(); track signal.id) {
                      <tr>
                        <td>{{ formatDateTime(signal.timestamp) }}</td>
                        <td class="ticker">{{ signal.ticker }}</td>
                        <td>{{ signal.strategy_name }}</td>
                        <td>
                          <span class="signal-type" [class]="'signal-' + signal.signal_type.toLowerCase()">
                            {{ signal.signal_type }}
                          </span>
                        </td>
                        <td class="price">{{ signal.price.toFixed(2) }}</td>
                        <td>
                          @if (signal.confidence) {
                            <span class="confidence">{{ (signal.confidence * 100).toFixed(0) }}%</span>
                          } @else {
                            <span class="text-muted">—</span>
                          }
                        </td>
                        <td>
                          @if (signal.position_size) {
                            {{ signal.position_size.toFixed(2) }}
                          } @else {
                            <span class="text-muted">—</span>
                          }
                        </td>
                        <td>
                          @if (signal.stop_loss) {
                            <span class="sl">{{ signal.stop_loss.toFixed(2) }}</span>
                          } @else {
                            <span class="text-muted">—</span>
                          }
                        </td>
                        <td>
                          @if (signal.take_profit) {
                            <span class="tp">{{ signal.take_profit.toFixed(2) }}</span>
                          } @else {
                            <span class="text-muted">—</span>
                          }
                        </td>
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
  styleUrl: './signals.component.scss'
})
export class SignalsComponent implements OnInit {
  private signalsService = inject(SignalsService);
  private strategiesService = inject(StrategiesService);
  private instrumentsService = inject(InstrumentsService);

  // State
  loading = signal(true);
  error = signal<string | null>(null);
  generating = signal(false);
  signals = signal<Signal[]>([]);
  filteredSignals = signal<Signal[]>([]);
  strategies = signal<any[]>([]);
  instruments = signal<any[]>([]);
  showForm = signal(false);

  // Filters
  filterStrategy = '';
  filterType = '';
  filterTicker = '';

  // Form data
  formData: SignalGenerateRequest = {
    strategy_name: '',
    ticker: '',
    start_date: undefined,
    end_date: undefined,
    use_risk_manager: true,
    save_to_db: true
  };

  ngOnInit(): void {
    this.loadSignals();
    this.loadStrategies();
    this.loadInstruments();
  }

  /**
   * Загрузка сигналов
   */
  loadSignals(): void {
    this.loading.set(true);
    this.error.set(null);

    this.signalsService.getSignals(undefined, undefined, undefined, undefined, undefined, 0, 500).subscribe({
      next: (data) => {
        this.signals.set(data);
        this.filteredSignals.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Load signals error:', err);
        this.error.set(err.message || 'Не удалось загрузить сигналы');
        this.loading.set(false);
      }
    });
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
   * Показать форму генерации
   */
  showGenerateForm(): void {
    this.formData = {
      strategy_name: '',
      ticker: '',
      start_date: undefined,
      end_date: undefined,
      use_risk_manager: true,
      save_to_db: true
    };
    this.showForm.set(true);
  }

  /**
   * Отменить генерацию
   */
  cancelGenerate(): void {
    this.showForm.set(false);
  }

  /**
   * Сгенерировать сигналы
   */
  generateSignals(): void {
    this.generating.set(true);

    this.signalsService.generateSignals(this.formData).subscribe({
      next: (response) => {
        this.generating.set(false);
        this.showForm.set(false);
        alert(`Сгенерировано ${response.signals_generated} сигналов (BUY: ${response.buy_signals}, SELL: ${response.sell_signals})`);
        this.loadSignals();
      },
      error: (err) => {
        console.error('Generate signals error:', err);
        alert(err.message || 'Ошибка при генерации сигналов');
        this.generating.set(false);
      }
    });
  }

  /**
   * Применить фильтры
   */
  applyFilters(): void {
    let filtered = this.signals();

    if (this.filterStrategy) {
      filtered = filtered.filter(s => s.strategy_name === this.filterStrategy);
    }

    if (this.filterType) {
      filtered = filtered.filter(s => s.signal_type === this.filterType);
    }

    if (this.filterTicker) {
      filtered = filtered.filter(s =>
        s.ticker.toLowerCase().includes(this.filterTicker.toLowerCase())
      );
    }

    this.filteredSignals.set(filtered);
  }

  /**
   * Форматировать дату и время
   */
  formatDateTime(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}
