import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Компонент загрузки (spinner)
 * Используется для индикации загрузки данных
 */
@Component({
  selector: 'app-loader',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="loader-container" [class.overlay]="overlay()">
      <div class="spinner" [style.width.px]="size()" [style.height.px]="size()">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">{{ message() }}</span>
        </div>
      </div>
      @if (message()) {
        <p class="loader-message">{{ message() }}</p>
      }
    </div>
  `,
  styles: [`
    .loader-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }

    .loader-container.overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.5);
      z-index: 9999;
    }

    .spinner {
      display: inline-block;
    }

    .spinner-border {
      display: inline-block;
      width: 100%;
      height: 100%;
      vertical-align: text-bottom;
      border: 0.25em solid currentColor;
      border-right-color: transparent;
      border-radius: 50%;
      animation: spinner-border 0.75s linear infinite;
    }

    @keyframes spinner-border {
      to {
        transform: rotate(360deg);
      }
    }

    .loader-message {
      margin-top: 1rem;
      color: #333;
      font-size: 0.9rem;
    }

    .overlay .loader-message {
      color: #fff;
    }

    .visually-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border-width: 0;
    }
  `]
})
export class LoaderComponent {
  /** Сообщение загрузки */
  message = input<string>('Загрузка...');

  /** Размер spinner в пикселях */
  size = input<number>(40);

  /** Показывать как overlay поверх всей страницы */
  overlay = input<boolean>(false);
}
