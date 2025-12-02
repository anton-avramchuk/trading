import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

import { IndicatorsService } from '../../core/services/indicators.service';
import { IndicatorInfo } from '../../core/models/indicator.model';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';

/**
 * Компонент работы с индикаторами
 * Список индикаторов, группировка по категориям
 */
@Component({
  selector: 'app-indicators',
  standalone: true,
  imports: [CommonModule, LoaderComponent, ErrorMessageComponent],
  template: `
    <div class="page">
      <header class="page-header">
        <div>
          <h2>Индикаторы</h2>
          <p>Технические индикаторы и их расчёт</p>
        </div>
      </header>

      @if (loading()) {
        <app-loader [message]="'Загрузка индикаторов...'" />
      } @else if (error()) {
        <app-error-message
          [title]="'Ошибка загрузки'"
          [message]="error()!"
          (retry)="loadIndicators()" />
      } @else {
        <div class="content">
          <!-- Фильтр по категориям -->
          <div class="filter-section">
            <button
              class="category-btn"
              [class.active]="selectedCategory() === null"
              (click)="filterByCategory(null)">
              Все ({{ indicators().length }})
            </button>
            @for (category of categories(); track category) {
              <button
                class="category-btn"
                [class.active]="selectedCategory() === category"
                (click)="filterByCategory(category)">
                {{ category }} ({{ getIndicatorsByCategory(category).length }})
              </button>
            }
          </div>

          <!-- Список индикаторов -->
          <div class="indicators-grid">
            @for (indicator of filteredIndicators(); track indicator.name) {
              <div class="indicator-card">
                <div class="indicator-header">
                  <h3>{{ indicator.name }}</h3>
                  <span class="category-badge">{{ indicator.category }}</span>
                </div>
                <p class="description">{{ indicator.description }}</p>

                @if (indicator.parameters.length > 0) {
                  <div class="parameters">
                    <h4>Параметры:</h4>
                    <ul>
                      @for (param of indicator.parameters; track param.name) {
                        <li>
                          <strong>{{ param.name }}</strong> ({{ param.type }})
                          @if (param.default !== undefined) {
                            — по умолчанию: {{ param.default }}
                          }
                        </li>
                      }
                    </ul>
                  </div>
                }

                <div class="actions">
                  <button class="btn btn-primary btn-sm">Рассчитать</button>
                </div>
              </div>
            }
          </div>

          @if (filteredIndicators().length === 0) {
            <div class="empty-state">
              <p>Нет индикаторов в выбранной категории</p>
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .page {
      padding: 1rem;
    }

    .page-header {
      margin-bottom: 2rem;

      h2 {
        margin: 0 0 0.5rem 0;
        font-size: 2rem;
        color: #1e293b;
      }

      p {
        margin: 0;
        color: #64748b;
      }
    }

    .content {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .filter-section {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      background: white;
      padding: 1rem;
      border-radius: 0.5rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .category-btn {
      padding: 0.5rem 1rem;
      border: 1px solid #e2e8f0;
      background: white;
      border-radius: 0.375rem;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 0.875rem;

      &:hover {
        background-color: #f8fafc;
        border-color: #cbd5e1;
      }

      &.active {
        background-color: #3b82f6;
        color: white;
        border-color: #3b82f6;
      }
    }

    .indicators-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 1.5rem;
    }

    .indicator-card {
      background: white;
      border-radius: 0.5rem;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e2e8f0;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .indicator-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;

      h3 {
        margin: 0;
        color: #1e293b;
        font-size: 1.25rem;
        font-family: monospace;
      }
    }

    .category-badge {
      padding: 0.25rem 0.75rem;
      background-color: #e0e7ff;
      color: #3730a3;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .description {
      color: #475569;
      line-height: 1.5;
      margin: 0;
    }

    .parameters {
      h4 {
        margin: 0 0 0.5rem 0;
        color: #64748b;
        font-size: 0.875rem;
        text-transform: uppercase;
        font-weight: 600;
      }

      ul {
        margin: 0;
        padding-left: 1.5rem;
        list-style: disc;
      }

      li {
        color: #475569;
        font-size: 0.875rem;
        line-height: 1.8;
      }
    }

    .actions {
      margin-top: auto;
      padding-top: 1rem;
      border-top: 1px solid #e2e8f0;
    }

    .btn {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 0.375rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-primary {
      background-color: #3b82f6;
      color: white;

      &:hover {
        background-color: #2563eb;
      }
    }

    .btn-sm {
      font-size: 0.875rem;
    }

    .empty-state {
      background: white;
      border-radius: 0.5rem;
      padding: 4rem 2rem;
      text-align: center;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

      p {
        color: #64748b;
        margin: 0;
      }
    }

    @media (max-width: 768px) {
      .indicators-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class IndicatorsComponent implements OnInit {
  private indicatorsService = inject(IndicatorsService);

  // State
  loading = signal(true);
  error = signal<string | null>(null);
  indicators = signal<IndicatorInfo[]>([]);
  categories = signal<string[]>([]);
  selectedCategory = signal<string | null>(null);
  filteredIndicators = signal<IndicatorInfo[]>([]);

  ngOnInit(): void {
    this.loadIndicators();
  }

  /**
   * Загрузка индикаторов
   */
  loadIndicators(): void {
    this.loading.set(true);
    this.error.set(null);

    this.indicatorsService.getIndicators().subscribe({
      next: (data) => {
        this.indicators.set(data.indicators);
        this.categories.set(data.categories);
        this.filteredIndicators.set(data.indicators);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Load indicators error:', err);
        this.error.set(err.message || 'Не удалось загрузить индикаторы');
        this.loading.set(false);
      }
    });
  }

  /**
   * Фильтровать по категории
   */
  filterByCategory(category: string | null): void {
    this.selectedCategory.set(category);

    if (category === null) {
      this.filteredIndicators.set(this.indicators());
    } else {
      const filtered = this.indicators().filter(ind => ind.category === category);
      this.filteredIndicators.set(filtered);
    }
  }

  /**
   * Получить индикаторы по категории
   */
  getIndicatorsByCategory(category: string): IndicatorInfo[] {
    return this.indicators().filter(ind => ind.category === category);
  }
}
