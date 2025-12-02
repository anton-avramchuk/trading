import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Компонент Dashboard
 * Главная страница приложения с обзором системы
 */
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="dashboard">
      <header class="dashboard-header">
        <h2>Dashboard</h2>
        <p>Обзор системы торговых сигналов</p>
      </header>

      <div class="dashboard-grid">
        <div class="card">
          <h3>Инструменты</h3>
          <div class="card-value">--</div>
          <p class="card-description">Доступно для анализа</p>
        </div>

        <div class="card">
          <h3>Индикаторы</h3>
          <div class="card-value">--</div>
          <p class="card-description">Технических индикаторов</p>
        </div>

        <div class="card">
          <h3>Стратегии</h3>
          <div class="card-value">--</div>
          <p class="card-description">Доступных стратегий</p>
        </div>

        <div class="card">
          <h3>Сигналы</h3>
          <div class="card-value">--</div>
          <p class="card-description">Сгенерировано сигналов</p>
        </div>
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
      </div>
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
  `]
})
export class DashboardComponent {}
