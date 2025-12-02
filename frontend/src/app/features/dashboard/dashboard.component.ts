import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { forkJoin, catchError, of } from 'rxjs';

import { InstrumentsService } from '../../core/services/instruments.service';
import { IndicatorsService } from '../../core/services/indicators.service';
import { StrategiesService } from '../../core/services/strategies.service';
import { SignalsService } from '../../core/services/signals.service';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';

interface DashboardStats {
  instrumentsCount: number;
  indicatorsCount: number;
  strategiesCount: number;
  signalsCount: number;
}

/**
 * Компонент Dashboard
 * Главная страница приложения с обзором системы
 */
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, LoaderComponent, ErrorMessageComponent],
  template: `
    <div class="dashboard">
      <header class="dashboard-header">
        <h2>Dashboard</h2>
        <p>Обзор системы торговых сигналов</p>
      </header>

      @if (loading()) {
        <app-loader [message]="'Загрузка статистики...'" />
      } @else if (error()) {
        <app-error-message
          [title]="'Ошибка загрузки'"
          [message]="error()!"
          (retry)="loadStats()" />
      } @else {
        <div class="dashboard-grid">
          <a routerLink="/instruments" class="card card-link">
            <h3>Инструменты</h3>
            <div class="card-value">{{ stats().instrumentsCount }}</div>
            <p class="card-description">Доступно для анализа</p>
          </a>

          <a routerLink="/indicators" class="card card-link">
            <h3>Индикаторы</h3>
            <div class="card-value">{{ stats().indicatorsCount }}</div>
            <p class="card-description">Технических индикаторов</p>
          </a>

          <a routerLink="/strategies" class="card card-link">
            <h3>Стратегии</h3>
            <div class="card-value">{{ stats().strategiesCount }}</div>
            <p class="card-description">Доступных стратегий</p>
          </a>

          <a routerLink="/signals" class="card card-link">
            <h3>Сигналы</h3>
            <div class="card-value">{{ stats().signalsCount }}</div>
            <p class="card-description">Сгенерировано сигналов</p>
          </a>
        </div>

        <div class="info-section">
          <h3>Добро пожаловать в Trading Signals</h3>
          <p>
            Система анализа торговых данных и генерации сигналов для российского фондового рынка.
          </p>
          <ul>
            <li><strong>Инструменты</strong> - управление торговыми инструментами и индексами</li>
            <li><strong>Индикаторы</strong> - технические индикаторы и их расчёт</li>
            <li><strong>Стратегии</strong> - торговые стратегии с multi-timeframe поддержкой</li>
            <li><strong>Сигналы</strong> - генерация и анализ торговых сигналов</li>
            <li><strong>Бэктестинг</strong> - тестирование стратегий на исторических данных</li>
          </ul>

          <div class="quick-links">
            <h4>Быстрые действия</h4>
            <div class="button-group">
              <a routerLink="/instruments" class="btn btn-primary">
                Добавить инструмент
              </a>
              <a routerLink="/indicators" class="btn btn-secondary">
                Рассчитать индикатор
              </a>
              <a routerLink="/signals" class="btn btn-secondary">
                Сгенерировать сигналы
              </a>
              <a routerLink="/backtesting" class="btn btn-secondary">
                Запустить бэктест
              </a>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .dashboard {
      padding: 1rem;
    }

    .dashboard-header {
      margin-bottom: 2rem;
    }

    .dashboard-header h2 {
      margin: 0 0 0.5rem 0;
      font-size: 2rem;
      color: #1e293b;
    }

    .dashboard-header p {
      margin: 0;
      color: #64748b;
      font-size: 1.1rem;
    }

    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .card {
      background: white;
      border-radius: 0.5rem;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e2e8f0;
      transition: all 0.2s;
    }

    .card-link {
      display: block;
      text-decoration: none;
      color: inherit;
    }

    .card-link:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      border-color: #3b82f6;
    }

    .card h3 {
      margin: 0 0 1rem 0;
      font-size: 0.875rem;
      color: #64748b;
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.5px;
    }

    .card-value {
      font-size: 2.5rem;
      font-weight: 700;
      color: #3b82f6;
      margin-bottom: 0.5rem;
    }

    .card-description {
      margin: 0;
      color: #64748b;
      font-size: 0.875rem;
    }

    .info-section {
      background: white;
      border-radius: 0.5rem;
      padding: 2rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e2e8f0;
    }

    .info-section h3 {
      margin: 0 0 1rem 0;
      color: #1e293b;
    }

    .info-section h4 {
      margin: 2rem 0 1rem 0;
      color: #1e293b;
      font-size: 1.1rem;
    }

    .info-section p {
      color: #475569;
      line-height: 1.6;
    }

    .info-section ul {
      margin: 1rem 0 0 0;
      padding-left: 1.5rem;
    }

    .info-section li {
      color: #475569;
      line-height: 1.8;
    }

    .info-section strong {
      color: #1e293b;
    }

    .quick-links {
      margin-top: 2rem;
      padding-top: 2rem;
      border-top: 1px solid #e2e8f0;
    }

    .button-group {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .btn {
      padding: 0.75rem 1.5rem;
      border-radius: 0.375rem;
      font-weight: 500;
      text-decoration: none;
      transition: all 0.2s;
      display: inline-block;
    }

    .btn-primary {
      background-color: #3b82f6;
      color: white;
    }

    .btn-primary:hover {
      background-color: #2563eb;
      transform: translateY(-1px);
    }

    .btn-secondary {
      background-color: #f1f5f9;
      color: #475569;
      border: 1px solid #e2e8f0;
    }

    .btn-secondary:hover {
      background-color: #e2e8f0;
      border-color: #cbd5e1;
      transform: translateY(-1px);
    }
  `]
})
export class DashboardComponent implements OnInit {
  private instrumentsService = inject(InstrumentsService);
  private indicatorsService = inject(IndicatorsService);
  private strategiesService = inject(StrategiesService);
  private signalsService = inject(SignalsService);

  // Signals for state management
  loading = signal(true);
  error = signal<string | null>(null);
  stats = signal<DashboardStats>({
    instrumentsCount: 0,
    indicatorsCount: 0,
    strategiesCount: 0,
    signalsCount: 0
  });

  ngOnInit(): void {
    this.loadStats();
  }

  /**
   * Загрузка статистики с backend
   */
  loadStats(): void {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      instruments: this.instrumentsService.getInstruments(0, 1000).pipe(
        catchError(() => of([]))
      ),
      indicators: this.indicatorsService.getIndicators().pipe(
        catchError(() => of({ indicators: [], count: 0, categories: [] }))
      ),
      strategies: this.strategiesService.getStrategies().pipe(
        catchError(() => of({ strategies: [], count: 0 }))
      ),
      signals: this.signalsService.getSignalStats().pipe(
        catchError(() => of({
          total_signals: 0,
          buy_signals: 0,
          sell_signals: 0,
          unique_strategies: 0,
          unique_instruments: 0
        }))
      )
    }).subscribe({
      next: (data) => {
        this.stats.set({
          instrumentsCount: data.instruments.length,
          indicatorsCount: data.indicators.count,
          strategiesCount: data.strategies.count,
          signalsCount: data.signals.total_signals
        });
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Dashboard stats error:', err);
        this.error.set('Не удалось загрузить статистику. Проверьте подключение к серверу.');
        this.loading.set(false);
      }
    });
  }
}
