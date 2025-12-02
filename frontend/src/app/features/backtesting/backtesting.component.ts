import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Компонент бэктестинга
 * Placeholder для будущей реализации
 */
@Component({
  selector: 'app-backtesting',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="page">
      <header class="page-header">
        <h2>Бэктестинг</h2>
        <p>Тестирование стратегий на исторических данных</p>
      </header>

      <div class="content">
        <p>Страница в разработке</p>
      </div>
    </div>
  `,
  styles: [`
    .page {
      padding: 1rem;
    }

    .page-header {
      margin-bottom: 2rem;
    }

    .page-header h2 {
      margin: 0 0 0.5rem 0;
      font-size: 2rem;
      color: #1e293b;
    }

    .page-header p {
      margin: 0;
      color: #64748b;
    }

    .content {
      background: white;
      border-radius: 0.5rem;
      padding: 2rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e2e8f0;
    }
  `]
})
export class BacktestingComponent {}
