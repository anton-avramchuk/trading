import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./core/layout/main-layout/main-layout.component')
      .then(m => m.MainLayoutComponent),
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard.component')
          .then(m => m.DashboardComponent)
      },
      {
        path: 'instruments',
        loadComponent: () => import('./features/instruments/instruments.component')
          .then(m => m.InstrumentsComponent)
      },
      {
        path: 'indicators',
        loadComponent: () => import('./features/indicators/indicators.component')
          .then(m => m.IndicatorsComponent)
      },
      {
        path: 'strategies',
        loadComponent: () => import('./features/strategies/strategies.component')
          .then(m => m.StrategiesComponent)
      },
      {
        path: 'signals',
        loadComponent: () => import('./features/signals/signals.component')
          .then(m => m.SignalsComponent)
      },
      {
        path: 'backtesting',
        loadComponent: () => import('./features/backtesting/backtesting.component')
          .then(m => m.BacktestingComponent)
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];
