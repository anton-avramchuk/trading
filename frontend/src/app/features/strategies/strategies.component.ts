import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { StrategiesService } from '../../core/services/strategies.service';
import { StrategyInfo, StrategyDetails } from '../../core/models/strategy.model';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';

/**
 * Компонент работы со стратегиями
 * Список стратегий с детальной информацией
 */
@Component({
  selector: 'app-strategies',
  standalone: true,
  imports: [CommonModule, LoaderComponent, ErrorMessageComponent],
  template: `
    <div class="page">
      <header class="page-header">
        <div>
          <h2>Стратегии</h2>
          <p>Торговые стратегии и их конфигурация</p>
        </div>
      </header>

      @if (loading()) {
        <app-loader [message]="'Загрузка стратегий...'" />
      } @else if (error()) {
        <app-error-message
          [title]="'Ошибка загрузки'"
          [message]="error()!"
          (retry)="loadStrategies()" />
      } @else {
        <div class="content">
          @if (strategies().length === 0) {
            <div class="empty-state">
              <p>Нет доступных стратегий</p>
            </div>
          } @else {
            <div class="strategies-grid">
              @for (strategy of strategies(); track strategy.name) {
                <div class="strategy-card">
                  <div class="strategy-header">
                    <div>
                      <h3>{{ strategy.name }}</h3>
                      <span class="version">v{{ strategy.version }}</span>
                    </div>
                    <span class="category-badge">{{ strategy.category }}</span>
                  </div>

                  <p class="description">{{ strategy.description }}</p>

                  @if (strategy.parameters.length > 0) {
                    <div class="parameters">
                      <h4>Параметры:</h4>
                      <div class="params-grid">
                        @for (param of strategy.parameters; track param.name) {
                          <div class="param-item">
                            <strong>{{ param.name }}</strong>
                            <span class="param-type">{{ param.type }}</span>
                            @if (param.default !== undefined) {
                              <span class="param-default">= {{ param.default }}</span>
                            }
                          </div>
                        }
                      </div>
                    </div>
                  }

                  <div class="actions">
                    <button
                      class="btn btn-secondary btn-sm"
                      (click)="showDetails(strategy)">
                      Подробнее
                    </button>
                    <button
                      class="btn btn-primary btn-sm"
                      (click)="generateSignals(strategy)">
                      Сгенерировать сигналы
                    </button>
                  </div>
                </div>
              }
            </div>
          }

          <!-- Детали стратегии -->
          @if (selectedStrategy()) {
            <div class="modal-overlay" (click)="closeDetails()">
              <div class="modal" (click)="$event.stopPropagation()">
                <div class="modal-header">
                  <h3>{{ selectedStrategy()!.name }}</h3>
                  <button class="btn-close" (click)="closeDetails()">&times;</button>
                </div>

                <div class="modal-body">
                  @if (loadingDetails()) {
                    <app-loader [message]="'Загрузка деталей...'" />
                  } @else if (strategyDetails()) {
                    <div class="details-section">
                      <h4>Описание</h4>
                      <p>{{ selectedStrategy()!.description }}</p>
                    </div>

                    <div class="details-section">
                      <h4>Версия</h4>
                      <p>{{ selectedStrategy()!.version }}</p>
                    </div>

                    <div class="details-section">
                      <h4>Категория</h4>
                      <p>{{ selectedStrategy()!.category }}</p>
                    </div>

                    @if (strategyDetails()!.required_timeframes.length > 0) {
                      <div class="details-section">
                        <h4>Необходимые таймфреймы</h4>
                        <div class="timeframes">
                          @for (tf of strategyDetails()!.required_timeframes; track tf) {
                            <span class="timeframe-badge">{{ tf }}</span>
                          }
                        </div>
                      </div>
                    }

                    @if (strategyDetails()!.indicators_config.length > 0) {
                      <div class="details-section">
                        <h4>Используемые индикаторы</h4>
                        <div class="indicators-list">
                          @for (ind of strategyDetails()!.indicators_config; track ind.name) {
                            <div class="indicator-item">
                              <strong>{{ ind.name }}</strong>
                              <span class="timeframe-badge">{{ ind.timeframe }}</span>
                              @if (ind.alias) {
                                <span class="alias">alias: {{ ind.alias }}</span>
                              }
                            </div>
                          }
                        </div>
                      </div>
                    }
                  }
                </div>
              </div>
            </div>
          }
        </div>
      }
    </div>
  `,
  styleUrl: './strategies.component.scss'
})
export class StrategiesComponent implements OnInit {
  private strategiesService = inject(StrategiesService);
  private router = inject(Router);

  // State
  loading = signal(true);
  error = signal<string | null>(null);
  strategies = signal<StrategyInfo[]>([]);
  selectedStrategy = signal<StrategyInfo | null>(null);
  strategyDetails = signal<StrategyDetails | null>(null);
  loadingDetails = signal(false);

  ngOnInit(): void {
    this.loadStrategies();
  }

  /**
   * Загрузка стратегий
   */
  loadStrategies(): void {
    this.loading.set(true);
    this.error.set(null);

    this.strategiesService.getStrategies().subscribe({
      next: (data) => {
        this.strategies.set(data.strategies);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Load strategies error:', err);
        this.error.set(err.message || 'Не удалось загрузить стратегии');
        this.loading.set(false);
      }
    });
  }

  /**
   * Показать детали стратегии
   */
  showDetails(strategy: StrategyInfo): void {
    this.selectedStrategy.set(strategy);
    this.loadingDetails.set(true);
    this.strategyDetails.set(null);

    this.strategiesService.getStrategyDetails(strategy.name).subscribe({
      next: (details) => {
        this.strategyDetails.set(details);
        this.loadingDetails.set(false);
      },
      error: (err) => {
        console.error('Load strategy details error:', err);
        this.loadingDetails.set(false);
      }
    });
  }

  /**
   * Закрыть детали
   */
  closeDetails(): void {
    this.selectedStrategy.set(null);
    this.strategyDetails.set(null);
  }

  /**
   * Перейти к генерации сигналов
   */
  generateSignals(strategy: StrategyInfo): void {
    // Переход на страницу signals с предзаполненной стратегией
    this.router.navigate(['/signals'], {
      queryParams: { strategy: strategy.name }
    });
  }
}
