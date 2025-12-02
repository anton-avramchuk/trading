import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  BacktestConfig,
  BacktestResult,
  BacktestRunResponse,
  BacktestListItem
} from '../models/backtest.model';

/**
 * Сервис для работы с бэктестингом
 */
@Injectable({
  providedIn: 'root'
})
export class BacktestingService {
  private readonly api = inject(ApiService);

  /**
   * Запустить бэктест
   */
  runBacktest(config: BacktestConfig): Observable<BacktestRunResponse> {
    return this.api.post<BacktestRunResponse>('/backtest/run', config);
  }

  /**
   * Получить результат бэктеста
   */
  getBacktestResult(backtestId: string): Observable<BacktestResult> {
    return this.api.get<BacktestResult>(`/backtest/${backtestId}`);
  }

  /**
   * Получить список всех бэктестов
   */
  getBacktests(
    ticker?: string,
    strategyName?: string,
    status?: 'running' | 'completed' | 'failed',
    skip: number = 0,
    limit: number = 100
  ): Observable<BacktestListItem[]> {
    const params: any = { skip: skip.toString(), limit: limit.toString() };
    if (ticker) params.ticker = ticker;
    if (strategyName) params.strategy_name = strategyName;
    if (status) params.status = status;

    return this.api.get<BacktestListItem[]>('/backtest', params);
  }

  /**
   * Удалить бэктест
   */
  deleteBacktest(backtestId: string): Observable<{ message: string }> {
    return this.api.delete<{ message: string }>(`/backtest/${backtestId}`);
  }

  /**
   * Сравнить несколько бэктестов
   */
  compareBacktests(backtestIds: string[]): Observable<{
    backtests: BacktestResult[];
    comparison_metrics: any;
  }> {
    return this.api.post('/backtest/compare', { backtest_ids: backtestIds });
  }

  /**
   * Экспортировать результат бэктеста в CSV
   */
  exportBacktest(backtestId: string): Observable<Blob> {
    return this.api.get<Blob>(`/backtest/${backtestId}/export`);
  }
}
