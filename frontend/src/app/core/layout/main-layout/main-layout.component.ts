import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

/**
 * Основной layout приложения
 * Включает header с навигацией и область контента
 */
@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="app-container">
      <header class="app-header">
        <div class="header-content">
          <div class="logo">
            <h1>Trading Signals</h1>
          </div>

          <nav class="main-nav">
            <a routerLink="/dashboard" routerLinkActive="active" class="nav-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
              </svg>
              <span>Dashboard</span>
            </a>

            <a routerLink="/instruments" routerLinkActive="active" class="nav-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
              <span>Инструменты</span>
            </a>

            <a routerLink="/indicators" routerLinkActive="active" class="nav-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              <span>Индикаторы</span>
            </a>

            <a routerLink="/strategies" routerLinkActive="active" class="nav-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
              <span>Стратегии</span>
            </a>

            <a routerLink="/signals" routerLinkActive="active" class="nav-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span>Сигналы</span>
            </a>

            <a routerLink="/backtesting" routerLinkActive="active" class="nav-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
              <span>Бэктестинг</span>
            </a>
          </nav>
        </div>
      </header>

      <main class="app-main">
        <router-outlet></router-outlet>
      </main>

      <footer class="app-footer">
        <p>&copy; 2025 Trading Signals System</p>
      </footer>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    .app-header {
      background-color: #1e293b;
      color: white;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      position: sticky;
      top: 0;
      z-index: 1000;
    }

    .header-content {
      display: flex;
      align-items: center;
      padding: 0 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }

    .logo {
      margin-right: 3rem;
    }

    .logo h1 {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 600;
      color: #3b82f6;
    }

    .main-nav {
      display: flex;
      gap: 0.5rem;
      flex: 1;
    }

    .nav-link {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 1rem 1.25rem;
      color: #94a3b8;
      text-decoration: none;
      border-bottom: 3px solid transparent;
      transition: all 0.2s;
      font-size: 0.95rem;
      font-weight: 500;
    }

    .nav-link:hover {
      color: white;
      background-color: rgba(255, 255, 255, 0.05);
    }

    .nav-link.active {
      color: white;
      border-bottom-color: #3b82f6;
      background-color: rgba(59, 130, 246, 0.1);
    }

    .nav-link svg {
      stroke-width: 2;
    }

    .app-main {
      flex: 1;
      padding: 2rem;
      max-width: 1400px;
      width: 100%;
      margin: 0 auto;
    }

    .app-footer {
      background-color: #f8fafc;
      border-top: 1px solid #e2e8f0;
      padding: 1.5rem 2rem;
      text-align: center;
      color: #64748b;
      font-size: 0.875rem;
    }

    .app-footer p {
      margin: 0;
    }

    @media (max-width: 1024px) {
      .header-content {
        flex-direction: column;
        padding: 1rem;
      }

      .logo {
        margin-right: 0;
        margin-bottom: 1rem;
      }

      .main-nav {
        width: 100%;
        overflow-x: auto;
      }

      .nav-link span {
        display: none;
      }

      .nav-link {
        padding: 1rem;
      }

      .app-main {
        padding: 1rem;
      }
    }
  `]
})
export class MainLayoutComponent {}
