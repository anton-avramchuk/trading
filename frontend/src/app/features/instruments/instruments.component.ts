import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { InstrumentsService } from '../../core/services/instruments.service';
import { Instrument, InstrumentCreate, Index } from '../../core/models/instrument.model';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';
import { ConfirmDialogComponent } from '../../shared/components/confirm-dialog/confirm-dialog.component';

/**
 * Компонент управления инструментами
 * CRUD операции для инструментов и индексов
 */
@Component({
  selector: 'app-instruments',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    LoaderComponent,
    ErrorMessageComponent,
    ConfirmDialogComponent
  ],
  template: `
    <div class="page">
      <header class="page-header">
        <div>
          <h2>Инструменты</h2>
          <p>Управление торговыми инструментами и индексами</p>
        </div>
        <button class="btn btn-primary" (click)="showAddForm()">
          + Добавить инструмент
        </button>
      </header>

      @if (loading()) {
        <app-loader [message]="'Загрузка инструментов...'" />
      } @else if (error()) {
        <app-error-message
          [title]="'Ошибка загрузки'"
          [message]="error()!"
          (retry)="loadInstruments()" />
      } @else {
        <div class="content">
          <!-- Форма добавления/редактирования -->
          @if (showForm()) {
            <div class="form-card">
              <h3>{{ editingInstrument() ? 'Редактировать' : 'Добавить' }} инструмент</h3>
              <form (ngSubmit)="saveInstrument()">
                <div class="form-grid">
                  <div class="form-group">
                    <label for="ticker">Тикер *</label>
                    <input
                      type="text"
                      id="ticker"
                      [(ngModel)]="formData.ticker"
                      name="ticker"
                      [disabled]="!!editingInstrument()"
                      required
                      placeholder="GAZP" />
                  </div>

                  <div class="form-group">
                    <label for="name">Название *</label>
                    <input
                      type="text"
                      id="name"
                      [(ngModel)]="formData.name"
                      name="name"
                      required
                      placeholder="Газпром" />
                  </div>

                  <div class="form-group">
                    <label for="market">Рынок *</label>
                    <select id="market" [(ngModel)]="formData.market" name="market" required>
                      <option value="MOEX">MOEX</option>
                      <option value="SPB">SPB</option>
                      <option value="CME">CME</option>
                      <option value="OTHER">Другой</option>
                    </select>
                  </div>

                  <div class="form-group">
                    <label for="type">Тип *</label>
                    <select id="type" [(ngModel)]="formData.instrument_type" name="type" required>
                      <option value="stock">Акция</option>
                      <option value="future">Фьючерс</option>
                      <option value="bond">Облигация</option>
                      <option value="index">Индекс</option>
                      <option value="currency">Валюта</option>
                    </select>
                  </div>

                  <div class="form-group">
                    <label for="index">Индекс</label>
                    <select id="index" [(ngModel)]="formData.index_id" name="index">
                      <option [ngValue]="undefined">Не указан</option>
                      @for (index of indexes(); track index.id) {
                        <option [ngValue]="index.id">{{ index.name }} ({{ index.ticker }})</option>
                      }
                    </select>
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

          <!-- Таблица инструментов -->
          @if (instruments().length === 0) {
            <div class="empty-state">
              <p>Нет добавленных инструментов</p>
              <button class="btn btn-primary" (click)="showAddForm()">
                Добавить первый инструмент
              </button>
            </div>
          } @else {
            <div class="table-card">
              <table class="instruments-table">
                <thead>
                  <tr>
                    <th>Тикер</th>
                    <th>Название</th>
                    <th>Рынок</th>
                    <th>Тип</th>
                    <th>Индекс</th>
                    <th>Дата создания</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  @for (instrument of instruments(); track instrument.id) {
                    <tr>
                      <td class="ticker">{{ instrument.ticker }}</td>
                      <td>{{ instrument.name }}</td>
                      <td>{{ instrument.market }}</td>
                      <td>
                        <span class="badge" [class]="'badge-' + instrument.instrument_type">
                          {{ getTypeLabel(instrument.instrument_type) }}
                        </span>
                      </td>
                      <td>
                        @if (instrument.index) {
                          {{ instrument.index.name }}
                        } @else {
                          <span class="text-muted">—</span>
                        }
                      </td>
                      <td>{{ formatDate(instrument.created_at) }}</td>
                      <td>
                        <div class="action-buttons">
                          <button
                            class="btn-icon"
                            (click)="editInstrument(instrument)"
                            title="Редактировать">
                            ✏️
                          </button>
                          <button
                            class="btn-icon btn-danger"
                            (click)="confirmDelete(instrument)"
                            title="Удалить">
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
        </div>
      }

      <!-- Диалог подтверждения удаления -->
      <app-confirm-dialog />
    </div>
  `,
  styleUrl: './instruments.component.scss'
})
export class InstrumentsComponent implements OnInit {
  private instrumentsService = inject(InstrumentsService);

  // State
  loading = signal(true);
  error = signal<string | null>(null);
  saving = signal(false);
  instruments = signal<Instrument[]>([]);
  indexes = signal<Index[]>([]);
  showForm = signal(false);
  editingInstrument = signal<Instrument | null>(null);

  // Form data
  formData: InstrumentCreate = {
    ticker: '',
    name: '',
    market: 'MOEX',
    instrument_type: 'stock',
    index_id: undefined
  };

  ngOnInit(): void {
    this.loadInstruments();
    this.loadIndexes();
  }

  /**
   * Загрузка инструментов
   */
  loadInstruments(): void {
    this.loading.set(true);
    this.error.set(null);

    this.instrumentsService.getInstruments(0, 1000).subscribe({
      next: (data) => {
        this.instruments.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Load instruments error:', err);
        this.error.set(err.message || 'Не удалось загрузить инструменты');
        this.loading.set(false);
      }
    });
  }

  /**
   * Загрузка индексов
   */
  loadIndexes(): void {
    this.instrumentsService.getIndexes().subscribe({
      next: (data) => {
        this.indexes.set(data);
      },
      error: (err) => {
        console.error('Load indexes error:', err);
      }
    });
  }

  /**
   * Показать форму добавления
   */
  showAddForm(): void {
    this.editingInstrument.set(null);
    this.formData = {
      ticker: '',
      name: '',
      market: 'MOEX',
      instrument_type: 'stock',
      index_id: undefined
    };
    this.showForm.set(true);
  }

  /**
   * Редактировать инструмент
   */
  editInstrument(instrument: Instrument): void {
    this.editingInstrument.set(instrument);
    this.formData = {
      ticker: instrument.ticker,
      name: instrument.name,
      market: instrument.market,
      instrument_type: instrument.instrument_type,
      index_id: instrument.index_id
    };
    this.showForm.set(true);
  }

  /**
   * Отменить редактирование
   */
  cancelEdit(): void {
    this.showForm.set(false);
    this.editingInstrument.set(null);
  }

  /**
   * Сохранить инструмент
   */
  saveInstrument(): void {
    this.saving.set(true);

    const operation = this.editingInstrument()
      ? this.instrumentsService.updateInstrument(this.formData.ticker, this.formData)
      : this.instrumentsService.createInstrument(this.formData);

    operation.subscribe({
      next: () => {
        this.saving.set(false);
        this.showForm.set(false);
        this.editingInstrument.set(null);
        this.loadInstruments();
      },
      error: (err) => {
        console.error('Save instrument error:', err);
        alert(err.message || 'Ошибка при сохранении инструмента');
        this.saving.set(false);
      }
    });
  }

  /**
   * Подтвердить удаление
   */
  confirmDelete(instrument: Instrument): void {
    if (confirm(`Удалить инструмент ${instrument.ticker} (${instrument.name})?`)) {
      this.deleteInstrument(instrument.ticker);
    }
  }

  /**
   * Удалить инструмент
   */
  deleteInstrument(ticker: string): void {
    this.instrumentsService.deleteInstrument(ticker).subscribe({
      next: () => {
        this.loadInstruments();
      },
      error: (err) => {
        console.error('Delete instrument error:', err);
        alert(err.message || 'Ошибка при удалении инструмента');
      }
    });
  }

  /**
   * Форматировать дату
   */
  formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU');
  }

  /**
   * Получить название типа инструмента
   */
  getTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      stock: 'Акция',
      future: 'Фьючерс',
      bond: 'Облигация',
      index: 'Индекс',
      currency: 'Валюта'
    };
    return labels[type] || type;
  }
}
