import { Component, inject, model } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'info' | 'warning' | 'danger';
}

/**
 * Компонент диалога подтверждения
 * Используется для подтверждения важных действий
 */
@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (isOpen()) {
      <div class="dialog-overlay" (click)="onCancel()">
        <div class="dialog-container" [class]="'dialog-' + data().type" (click)="$event.stopPropagation()">
          <div class="dialog-header">
            <h3>{{ data().title }}</h3>
            <button class="btn-close-x" (click)="onCancel()">&times;</button>
          </div>

          <div class="dialog-body">
            <p>{{ data().message }}</p>
          </div>

          <div class="dialog-footer">
            <button class="btn btn-cancel" (click)="onCancel()">
              {{ data().cancelText || 'Отмена' }}
            </button>
            <button
              class="btn btn-confirm"
              [class.btn-danger]="data().type === 'danger'"
              [class.btn-warning]="data().type === 'warning'"
              (click)="onConfirm()">
              {{ data().confirmText || 'Подтвердить' }}
            </button>
          </div>
        </div>
      </div>
    }
  `,
  styles: [`
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

    .dialog-body p {
      margin: 0;
      color: #374151;
      line-height: 1.5;
    }

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
      padding: 1.5rem;
      border-top: 1px solid #e5e7eb;
    }

    .btn {
      padding: 0.5rem 1.25rem;
      border: none;
      border-radius: 0.375rem;
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 500;
      transition: all 0.2s;
    }

    .btn-cancel {
      background-color: #f3f4f6;
      color: #374151;
    }

    .btn-cancel:hover {
      background-color: #e5e7eb;
    }

    .btn-confirm {
      background-color: #3b82f6;
      color: white;
    }

    .btn-confirm:hover {
      background-color: #2563eb;
    }

    .btn-danger {
      background-color: #ef4444;
    }

    .btn-danger:hover {
      background-color: #dc2626;
    }

    .btn-warning {
      background-color: #f59e0b;
    }

    .btn-warning:hover {
      background-color: #d97706;
    }

    .dialog-danger .dialog-header {
      border-bottom-color: #fecaca;
    }

    .dialog-warning .dialog-header {
      border-bottom-color: #fde68a;
    }
  `]
})
export class ConfirmDialogComponent {
  /** Открыт ли диалог */
  isOpen = model<boolean>(false);

  /** Данные диалога */
  data = model<ConfirmDialogData>({
    title: 'Подтверждение',
    message: 'Вы уверены?',
    type: 'info'
  });

  /** Callback при подтверждении */
  onConfirmCallback?: () => void;

  /** Callback при отмене */
  onCancelCallback?: () => void;

  /**
   * Открыть диалог
   */
  open(data: ConfirmDialogData, onConfirm?: () => void, onCancel?: () => void): void {
    this.data.set({
      ...data,
      confirmText: data.confirmText || 'Подтвердить',
      cancelText: data.cancelText || 'Отмена',
      type: data.type || 'info'
    });
    this.onConfirmCallback = onConfirm;
    this.onCancelCallback = onCancel;
    this.isOpen.set(true);
  }

  /**
   * Обработчик подтверждения
   */
  onConfirm(): void {
    this.isOpen.set(false);
    if (this.onConfirmCallback) {
      this.onConfirmCallback();
    }
  }

  /**
   * Обработчик отмены
   */
  onCancel(): void {
    this.isOpen.set(false);
    if (this.onCancelCallback) {
      this.onCancelCallback();
    }
  }
}
