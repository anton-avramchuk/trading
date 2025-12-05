import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { CountriesService } from '../../core/services/countries.service';
import { Country, CountryCreate } from '../../core/models/country.model';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';

/**
 * Компонент управления странами
 * CRUD операции для стран (ISO 3166)
 */
@Component({
  selector: 'app-countries',
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
          <h2>Страны</h2>
          <p>Управление странами (ISO 3166)</p>
        </div>
        <button class="btn btn-primary" (click)="showAddForm()">
          + Добавить страну
        </button>
      </header>

      @if (loading()) {
        <app-loader [message]="'Загрузка стран...'" />
      } @else if (error()) {
        <app-error-message
          [title]="'Ошибка загрузки'"
          [message]="error()!"
          (retry)="loadCountries()" />
      } @else {
        <div class="content">
          <!-- Форма добавления/редактирования -->
          @if (showForm()) {
            <div class="form-card">
              <h3>{{ editingCountry() ? 'Редактировать' : 'Добавить' }} страну</h3>
              <form (ngSubmit)="saveCountry()">
                <div class="form-grid">
                  <div class="form-group">
                    <label for="code">Код ISO Alpha-2 *</label>
                    <input
                      type="text"
                      id="code"
                      [(ngModel)]="formData.code"
                      name="code"
                      [disabled]="!!editingCountry()"
                      required
                      maxlength="2"
                      placeholder="RU" />
                    <small>Двухбуквенный код страны</small>
                  </div>

                  <div class="form-group">
                    <label for="code3">Код ISO Alpha-3</label>
                    <input
                      type="text"
                      id="code3"
                      [(ngModel)]="formData.code3"
                      name="code3"
                      maxlength="3"
                      placeholder="RUS" />
                    <small>Трехбуквенный код (опционально)</small>
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
                      placeholder="Россия" />
                  </div>

                  <div class="form-group">
                    <label for="name_en">Название (EN)</label>
                    <input
                      type="text"
                      id="name_en"
                      [(ngModel)]="formData.name_en"
                      name="name_en"
                      maxlength="100"
                      placeholder="Russia" />
                  </div>

                  <div class="form-group">
                    <label for="region">Регион</label>
                    <select id="region" [(ngModel)]="formData.region" name="region">
                      <option value="">Не указан</option>
                      <option value="Europe">Europe</option>
                      <option value="Asia">Asia</option>
                      <option value="Americas">Americas</option>
                      <option value="Africa">Africa</option>
                      <option value="Oceania">Oceania</option>
                    </select>
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
              <input type="checkbox" [(ngModel)]="showActiveOnly" (change)="loadCountries()" />
              Только активные
            </label>

            <label style="margin-left: 2rem;">
              Регион:
              <select [(ngModel)]="filterRegion" (change)="loadCountries()" style="margin-left: 0.5rem;">
                <option value="">Все</option>
                <option value="Europe">Europe</option>
                <option value="Asia">Asia</option>
                <option value="Americas">Americas</option>
                <option value="Africa">Africa</option>
                <option value="Oceania">Oceania</option>
              </select>
            </label>
          </div>

          <!-- Список стран -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Код</th>
                  <th>Alpha-3</th>
                  <th>Название</th>
                  <th>Название (EN)</th>
                  <th>Регион</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                @if (countries().length === 0) {
                  <tr>
                    <td colspan="7" class="no-data">
                      Страны не найдены. Добавьте первую страну.
                    </td>
                  </tr>
                }
                @for (country of countries(); track country.id) {
                  <tr>
                    <td><strong>{{ country.code }}</strong></td>
                    <td>
                      @if (country.code3) {
                        {{ country.code3 }}
                      } @else {
                        <span class="text-muted">—</span>
                      }
                    </td>
                    <td>{{ country.name }}</td>
                    <td>
                      @if (country.name_en) {
                        {{ country.name_en }}
                      } @else {
                        <span class="text-muted">—</span>
                      }
                    </td>
                    <td>
                      @if (country.region) {
                        <span class="badge badge-info">{{ country.region }}</span>
                      } @else {
                        <span class="text-muted">—</span>
                      }
                    </td>
                    <td>
                      <span [class]="country.is_active === 1 ? 'badge badge-success' : 'badge badge-secondary'">
                        {{ country.is_active === 1 ? 'Активна' : 'Неактивна' }}
                      </span>
                    </td>
                    <td>
                      <div class="actions">
                        <button class="btn btn-sm btn-secondary" (click)="editCountry(country)">
                          Редактировать
                        </button>
                        <button class="btn btn-sm btn-danger" (click)="confirmDelete(country)">
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
      @if (deletingCountry()) {
        <div class="dialog-overlay" (click)="cancelDelete()">
          <div class="dialog-container" (click)="$event.stopPropagation()">
            <div class="dialog-header">
              <h3>Удалить страну?</h3>
              <button class="btn-close-x" (click)="cancelDelete()">&times;</button>
            </div>
            <div class="dialog-body">
              <p>Вы уверены, что хотите удалить страну {{ deletingCountry()!.name }}?</p>
            </div>
            <div class="dialog-footer">
              <button class="btn btn-cancel" (click)="cancelDelete()">Отмена</button>
              <button class="btn btn-danger" (click)="deleteCountry()">Удалить</button>
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
    .form-group select {
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
      display: flex;
      align-items: center;
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

    .badge-info {
      background: #d1ecf1;
      color: #0c5460;
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
export class CountriesComponent implements OnInit {
  private countriesService = inject(CountriesService);

  // State signals
  countries = signal<Country[]>([]);
  loading = signal(false);
  saving = signal(false);
  error = signal<string | null>(null);
  showForm = signal(false);
  editingCountry = signal<Country | null>(null);
  deletingCountry = signal<Country | null>(null);

  // Filters
  showActiveOnly = false;
  filterRegion = '';

  // Form data
  formData: CountryCreate & { is_active_bool: boolean } = this.getEmptyFormData();

  ngOnInit() {
    this.loadCountries();
  }

  loadCountries() {
    this.loading.set(true);
    this.error.set(null);

    const params: any = {};
    if (this.showActiveOnly) params.active_only = true;
    if (this.filterRegion) params.region = this.filterRegion;

    this.countriesService.getCountries(Object.keys(params).length > 0 ? params : undefined).subscribe({
      next: (data) => {
        this.countries.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Не удалось загрузить страны');
        this.loading.set(false);
      }
    });
  }

  showAddForm() {
    this.formData = this.getEmptyFormData();
    this.editingCountry.set(null);
    this.showForm.set(true);
  }

  editCountry(country: Country) {
    this.formData = {
      code: country.code,
      code3: country.code3,
      name: country.name,
      name_en: country.name_en,
      region: country.region,
      is_active: country.is_active,
      is_active_bool: country.is_active === 1
    };
    this.editingCountry.set(country);
    this.showForm.set(true);
  }

  saveCountry() {
    this.saving.set(true);

    const countryData: CountryCreate = {
      code: this.formData.code,
      code3: this.formData.code3,
      name: this.formData.name,
      name_en: this.formData.name_en,
      region: this.formData.region,
      is_active: this.formData.is_active_bool ? 1 : 0
    };

    const request = this.editingCountry()
      ? this.countriesService.updateCountry(this.editingCountry()!.id, countryData)
      : this.countriesService.createCountry(countryData);

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.showForm.set(false);
        this.loadCountries();
      },
      error: (err) => {
        this.saving.set(false);
        alert('Ошибка: ' + (err.error?.detail || err.message));
      }
    });
  }

  cancelEdit() {
    this.showForm.set(false);
    this.editingCountry.set(null);
  }

  confirmDelete(country: Country) {
    this.deletingCountry.set(country);
  }

  deleteCountry() {
    const country = this.deletingCountry();
    if (!country) return;

    this.countriesService.deleteCountry(country.id).subscribe({
      next: () => {
        this.deletingCountry.set(null);
        this.loadCountries();
      },
      error: (err) => {
        alert('Ошибка удаления: ' + (err.error?.detail || err.message));
        this.deletingCountry.set(null);
      }
    });
  }

  cancelDelete() {
    this.deletingCountry.set(null);
  }

  private getEmptyFormData(): CountryCreate & { is_active_bool: boolean } {
    return {
      code: '',
      code3: undefined,
      name: '',
      name_en: undefined,
      region: undefined,
      is_active: 1,
      is_active_bool: true
    };
  }
}
