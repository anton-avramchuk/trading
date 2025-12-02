import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Компонент отображения ошибок
 * Показывает сообщение об ошибке с возможностью закрытия и повторной попытки
 */
@Component({
  selector: 'app-error-message',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="error-container" [class]="'error-' + type()">
      <div class="error-icon">
        @switch (type()) {
          @case ('error') {
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          }
          @case ('warning') {
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          }
        }
      </div>

      <div class="error-content">
        <h4 class="error-title">{{ title() }}</h4>
        <p class="error-message">{{ message() }}</p>

        @if (details()) {
          <details class="error-details">
            <summary>Подробности</summary>
            <pre>{{ details() }}</pre>
          </details>
        }
      </div>

      <div class="error-actions">
        @if (showRetry()) {
          <button class="btn btn-retry" (click)="retry.emit()">
            Повторить
          </button>
        }
        @if (showClose()) {
          <button class="btn btn-close" (click)="close.emit()">
            Закрыть
          </button>
        }
      </div>
    </div>
  `,
  styles: [`
    .error-container {
      display: flex;
      gap: 1rem;
      padding: 1rem;
      border-radius: 0.5rem;
      border: 1px solid;
      margin: 1rem 0;
    }

    .error-error {
      background-color: #fee;
      border-color: #fcc;
      color: #c33;
    }

    .error-warning {
      background-color: #ffc;
      border-color: #fc9;
      color: #963;
    }

    .error-icon {
      flex-shrink: 0;
    }

    .error-icon svg {
      width: 24px;
      height: 24px;
    }

    .error-content {
      flex: 1;
    }

    .error-title {
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
      font-weight: 600;
    }

    .error-message {
      margin: 0;
      font-size: 0.9rem;
    }

    .error-details {
      margin-top: 0.5rem;
      font-size: 0.85rem;
    }

    .error-details summary {
      cursor: pointer;
      font-weight: 500;
      margin-bottom: 0.5rem;
    }

    .error-details pre {
      margin: 0;
      padding: 0.5rem;
      background-color: rgba(0, 0, 0, 0.05);
      border-radius: 0.25rem;
      overflow-x: auto;
      font-size: 0.8rem;
    }

    .error-actions {
      display: flex;
      gap: 0.5rem;
      align-items: flex-start;
    }

    .btn {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 0.25rem;
      cursor: pointer;
      font-size: 0.875rem;
      transition: opacity 0.2s;
    }

    .btn:hover {
      opacity: 0.8;
    }

    .btn-retry {
      background-color: #007bff;
      color: white;
    }

    .btn-close {
      background-color: transparent;
      color: inherit;
      border: 1px solid currentColor;
    }
  `]
})
export class ErrorMessageComponent {
  /** Заголовок ошибки */
  title = input<string>('Ошибка');

  /** Текст сообщения об ошибке */
  message = input<string>('Произошла неизвестная ошибка');

  /** Детали ошибки (опционально) */
  details = input<string>('');

  /** Тип сообщения */
  type = input<'error' | 'warning'>('error');

  /** Показать кнопку "Повторить" */
  showRetry = input<boolean>(true);

  /** Показать кнопку "Закрыть" */
  showClose = input<boolean>(true);

  /** Событие при нажатии "Повторить" */
  retry = output<void>();

  /** Событие при нажатии "Закрыть" */
  close = output<void>();
}
