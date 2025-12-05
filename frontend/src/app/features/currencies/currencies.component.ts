import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { CurrenciesService } from '../../core/services/currencies.service';
import { Currency, CurrencyCreate } from '../../core/models/currency.model';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';

/**
 * Компонент управления валютами
 * CRUD операции для валют (ISO 4217 + криптовалюты)
 */
@Component({
  selector: 'app-currencies',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    LoaderComponent,
    ErrorMessageComponent
  ],
  template: `
    <div class="page">
      <header class="page-header">
        <div>
          <h2>Валюты</h2>
          <p>Управление валютами (ISO 4217, криптовалюты)</p>
        </div>
        <button class="btn btn-primary" (click)="showAddForm()">
          + Добавить валюту
        </button>
      </header>

      @if (loading()) {
        <app-loader [message]="'Загрузка валют...'" />
      } @else if (error()) {
        <app-error-message
          [title]="'Ошибка загрузки'"
          [message]="error()!"
          (retry)="loadCurrencies()" />
      } @else {
        <div class="content">
          <!-- Форма добавления/редактирования -->
          @if (showForm()) {
            <div class="form-card">
              <h3>{{ editingCurrency() ? 'Редактировать' : 'Добавить' }} валюту</h3>
              <form (ngSubmit)="saveCurrency()">
                <div class="form-grid">
                  <div class="form-group">
                    <label for="code">Код *</label>
                    <input
                      type="text"
                      id="code"
                      [(ngModel)]="formData.code"
                      name="code"
                      [disabled]="!!editingCurrency()"
                      required
                      maxlength="10"
                      placeholder="RUB / BTC / USDT" />
                    <small>ISO 4217 код или тикер криптовалюты</small>
                  </div>

                  <div class="form-group">
                    <label for="numeric_code">Цифровой код</label>
                    <input
                      type="text"
                      id="numeric_code"
                      [(ngModel)]="formData.numeric_code"
                      name="numeric_code"
                      maxlength="3"
                      placeholder="643" />
                    <small>ISO 4217 numeric code (опционально)</small>
                  </div>

                  <div class="form-group">
                    <label for="name">Название *</label>
                    <input
                      type="text"
                      id="name"
                      [(ngModel)]="formData.name"
                      name="name"
                      required
                      maxlength="100"
                      placeholder="Российский рубль" />
                  </div>

                  <div class="form-group">
                    <label for="name_en">Название (EN)</label>
                    <input
                      type="text"
                      id="name_en"
                      [(ngModel)]="formData.name_en"
                      name="name_en"
                      maxlength="100"
                      placeholder="Russian Ruble" />
                  </div>

                  <div class="form-group">
                    <label for="symbol">Символ</label>
                    <input
                      type="text"
                      id="symbol"
                      [(ngModel)]="formData.symbol"
                      name="symbol"
                      maxlength="10"
                      placeholder="₽" />
                    <small>₽, $, €, ¥, ₮</small>
                  </div>

                  <div class="form-group">
                    <label for="decimal_places">Знаков после запятой *</label>
                    <input
                      type="number"
                      id="decimal_places"
                      [(ngModel)]="formData.decimal_places"
                      name="decimal_places"
                      required
                      min="0"
                      max="18"
                      placeholder="2" />
                    <small>Обычно 2, для крипты 8</small>
                  </div>

                  <div class="form-group">
                    <label>
                      <input
                        type="checkbox"
                        [(ngModel)]="formData.is_active_bool"
                        name="is_active" />
                      Активна
                    </label>
                  </div>
                </div>

                <div class="form-actions">
                  <button type="button" class="btn btn-secondary" (click)="cancelEdit()">
                    Отмена
                  </button>
                  <button type="submit" class="btn btn-primary" [disabled]="saving()">
                    {{ saving() ? 'Сохранение...' : 'Сохранить' }}
                  </button>
                </div>
              </form>
            </div>
          }

          <!-- Фильтры -->
          <div class="filters">
            <label>
              <input type="checkbox" [(ngModel)]="showActiveOnly" (change)="loadCurrencies()" />
              Только активные
            </label>
          </div>

          <!-- Список валют -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Код</th>
                  <th>Символ</th>
                  <th>Название</th>
                  <th>Название (EN)</th>
                  <th>Знаков</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                @if (currencies().length === 0) {
                  <tr>
                    <td colspan="7" class="no-data">
                      Валюты не найдены. Добавьте первую валюту.
                    </td>
                  </tr>
                }
                @for (currency of currencies(); track currency.id) {
                  <tr>
                    <td><strong>{{ currency.code }}</strong></td>
                    <td>
                      @if (currency.symbol) {
                        <span class="currency-symbol">{{ currency.symbol }}</span>
                      } @else {
                        <span class="text-muted">—</span>
                      }
                    </td>
                    <td>{{ currency.name }}</td>
                    <td>
                      @if (currency.name_en) {
                        {{ currency.name_en }}
                      } @else {
                        <span class="text-muted">—</span>
                      }
                    </td>
                    <td>{{ currency.decimal_places }}</td>
                    <td>
                      <span [class]="currency.is_active === 1 ? 'badge badge-success' : 'badge badge-secondary'">
                        {{ currency.is_active === 1 ? 'Активна' : 'Неактивна' }}
                      </span>
                    </td>
                    <td>
                      <div class="actions">
                        <button class="btn btn-sm btn-secondary" (click)="editCurrency(currency)">
                          Редактировать
                        </button>
                        <button class="btn btn-sm btn-danger" (click)="confirmDelete(currency)">
                          Удалить
                        </button>
                      </div>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </div>
      }

      <!-- Диалог подтверждения удаления -->
      @if (deletingCurrency()) {
        <div class="dialog-overlay" (click)="cancelDelete()">
          <div class="dialog-container" (click)="$event.stopPropagation()">
            <div class="dialog-header">
              <h3>Удалить валюту?</h3>
              <button class="btn-close-x" (click)="cancelDelete()">&times;</button>
            </div>
            <div class="dialog-body">
              <p>Вы уверены, что хотите удалить валюту {{ deletingCurrency()!.code }}?</p>
            </div>
            <div class="dialog-footer">
              <button class="btn btn-cancel" (click)="cancelDelete()">Отмена</button>
              <button class="btn btn-danger" (click)="deleteCurrency()">Удалить</button>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .page {
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }

    .page-header h2 {
      margin: 0 0 0.5rem 0;
      font-size: 2rem;
    }

    .page-header p {
      margin: 0;
      color: #666;
    }

    .form-card {
      background: white;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 2rem;
      margin-bottom: 2rem;
    }

    .form-card h3 {
      margin: 0 0 1.5rem 0;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }

    .form-group {
      display: flex;
      flex-direction: column;
    }

    .form-group label {
      font-weight: 500;
      margin-bottom: 0.5rem;
    }

    .form-group small {
      font-size: 0.875rem;
      color: #666;
      margin-top: 0.25rem;
    }

    .form-group input[type="text"],
    .form-group input[type="number"] {
      padding: 0.5rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 1rem;
    }

    .form-group input[type="checkbox"] {
      width: auto;
      margin-right: 0.5rem;
    }

    .form-actions {
      display: flex;
      gap: 1rem;
      justify-content: flex-end;
    }

    .filters {
      margin-bottom: 1rem;
      padding: 1rem;
      background: #f5f5f5;
      border-radius: 4px;
    }

    .filters label {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
    }

    .table-container {
      overflow-x: auto;
      background: white;
      border: 1px solid #ddd;
      border-radius: 8px;
    }

    .data-table {
      width: 100%;
      border-collapse: collapse;
    }

    .data-table th,
    .data-table td {
      padding: 1rem;
      text-align: left;
      border-bottom: 1px solid #eee;
    }

    .data-table th {
      background: #f5f5f5;
      font-weight: 600;
    }

    .data-table tbody tr:hover {
      background: #f9f9f9;
    }

    .currency-symbol {
      font-size: 1.5rem;
      font-weight: bold;
    }

    .no-data {
      text-align: center !important;
      padding: 3rem !important;
      color: #999;
    }

    .actions {
      display: flex;
      gap: 0.5rem;
    }

    .badge {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.875rem;
      font-weight: 500;
    }

    .badge-success {
      background: #d4edda;
      color: #155724;
    }

    .badge-secondary {
      background: #e2e3e5;
      color: #383d41;
    }

    .text-muted {
      color: #999;
    }

    .btn {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 1rem;
      font-weight: 500;
      transition: all 0.2s;
    }

    .btn-primary {
      background: #007bff;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background: #0056b3;
    }

    .btn-secondary {
      background: #6c757d;
      color: white;
    }

    .btn-secondary:hover {
      background: #545b62;
    }

    .btn-danger {
      background: #dc3545;
      color: white;
    }

    .btn-danger:hover {
      background: #c82333;
    }

    .btn-sm {
      padding: 0.25rem 0.75rem;
      font-size: 0.875rem;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .dialog-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
    }

    .dialog-container {
      background: white;
      border-radius: 0.5rem;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
      min-width: 400px;
      max-width: 600px;
    }

    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem;
      border-bottom: 1px solid #e5e7eb;
    }

    .dialog-header h3 {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
    }

    .btn-close-x {
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: #6b7280;
      padding: 0;
      width: 2rem;
      height: 2rem;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 0.25rem;
      transition: background-color 0.2s;
    }

    .btn-close-x:hover {
      background-color: #f3f4f6;
    }

    .dialog-body {
      padding: 1.5rem;
    }

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
      padding: 1rem 1.5rem;
      border-top: 1px solid #e5e7eb;
    }

    .btn-cancel {
      background-color: #6b7280;
      color: white;
    }

    .btn-cancel:hover {
      background-color: #4b5563;
    }
  `]
})
export class CurrenciesComponent implements OnInit {
  private currenciesService = inject(CurrenciesService);

  // State signals
  currencies = signal<Currency[]>([]);
  loading = signal(false);
  saving = signal(false);
  error = signal<string | null>(null);
  showForm = signal(false);
  editingCurrency = signal<Currency | null>(null);
  deletingCurrency = signal<Currency | null>(null);

  // Filters
  showActiveOnly = false;

  // Form data
  formData: CurrencyCreate & { is_active_bool: boolean } = this.getEmptyFormData();

  ngOnInit() {
    this.loadCurrencies();
  }

  loadCurrencies() {
    this.loading.set(true);
    this.error.set(null);

    const params = this.showActiveOnly ? { active_only: true } : undefined;

    this.currenciesService.getCurrencies(params).subscribe({
      next: (data) => {
        this.currencies.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Не удалось загрузить валюты');
        this.loading.set(false);
      }
    });
  }

  showAddForm() {
    this.formData = this.getEmptyFormData();
    this.editingCurrency.set(null);
    this.showForm.set(true);
  }

  editCurrency(currency: Currency) {
    this.formData = {
      code: currency.code,
      numeric_code: currency.numeric_code,
      name: currency.name,
      name_en: currency.name_en,
      symbol: currency.symbol,
      decimal_places: currency.decimal_places,
      is_active: currency.is_active,
      is_active_bool: currency.is_active === 1
    };
    this.editingCurrency.set(currency);
    this.showForm.set(true);
  }

  saveCurrency() {
    this.saving.set(true);

    const currencyData: CurrencyCreate = {
      code: this.formData.code,
      numeric_code: this.formData.numeric_code,
      name: this.formData.name,
      name_en: this.formData.name_en,
      symbol: this.formData.symbol,
      decimal_places: this.formData.decimal_places,
      is_active: this.formData.is_active_bool ? 1 : 0
    };

    const request = this.editingCurrency()
      ? this.currenciesService.updateCurrency(this.editingCurrency()!.id, currencyData)
      : this.currenciesService.createCurrency(currencyData);

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.showForm.set(false);
        this.loadCurrencies();
      },
      error: (err) => {
        this.saving.set(false);
        alert('Ошибка: ' + (err.error?.detail || err.message));
      }
    });
  }

  cancelEdit() {
    this.showForm.set(false);
    this.editingCurrency.set(null);
  }

  confirmDelete(currency: Currency) {
    this.deletingCurrency.set(currency);
  }

  deleteCurrency() {
    const currency = this.deletingCurrency();
    if (!currency) return;

    this.currenciesService.deleteCurrency(currency.id).subscribe({
      next: () => {
        this.deletingCurrency.set(null);
        this.loadCurrencies();
      },
      error: (err) => {
        alert('Ошибка удаления: ' + (err.error?.detail || err.message));
        this.deletingCurrency.set(null);
      }
    });
  }

  cancelDelete() {
    this.deletingCurrency.set(null);
  }

  private getEmptyFormData(): CurrencyCreate & { is_active_bool: boolean } {
    return {
      code: '',
      numeric_code: undefined,
      name: '',
      name_en: undefined,
      symbol: undefined,
      decimal_places: 2,
      is_active: 1,
      is_active_bool: true
    };
  }
}
