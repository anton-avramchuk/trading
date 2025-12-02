import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  Signal,
  SignalGenerateRequest,
  SignalGenerateResponse,
  SignalStatsResponse
} from '../models/signal.model';

/**
 * Сервис для работы с торговыми сигналами
 */
@Injectable({
  providedIn: 'root'
})
export class SignalsService {
  private readonly api = inject(ApiService);

  /**
   * Получить список сигналов
   */
  getSignals(
    ticker?: string,
    strategyName?: string,
    signalType?: 'BUY' | 'SELL' | 'HOLD',
    startDate?: string,
    endDate?: string,
    skip: number = 0,
    limit: number = 100
  ): Observable<Signal[]> {
    const params: any = { skip: skip.toString(), limit: limit.toString() };
    if (ticker) params.ticker = ticker;
    if (strategyName) params.strategy_name = strategyName;
    if (signalType) params.signal_type = signalType;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    return this.api.get<Signal[]>('/signals', params);
  }

  /**
   * Получить сигнал по ID
   */
  getSignal(signalId: number): Observable<Signal> {
    return this.api.get<Signal>(`/signals/${signalId}`);
  }

  /**
   * Сгенерировать сигналы для стратегии
   */
  generateSignals(data: SignalGenerateRequest): Observable<SignalGenerateResponse> {
    return this.api.post<SignalGenerateResponse>('/signals/generate', data);
  }

  /**
   * Удалить сигнал
   */
  deleteSignal(signalId: number): Observable<{ message: string }> {
    return this.api.delete<{ message: string }>(`/signals/${signalId}`);
  }

  /**
   * Удалить все сигналы для инструмента
   */
  deleteSignalsByTicker(ticker: string): Observable<{ message: string; deleted_count: number }> {
    return this.api.delete<{ message: string; deleted_count: number }>(`/signals/ticker/${ticker}`);
  }

  /**
   * Удалить все сигналы для стратегии
   */
  deleteSignalsByStrategy(strategyName: string): Observable<{ message: string; deleted_count: number }> {
    return this.api.delete<{ message: string; deleted_count: number }>(`/signals/strategy/${strategyName}`);
  }

  /**
   * Получить статистику по сигналам
   */
  getSignalStats(
    ticker?: string,
    strategyName?: string,
    startDate?: string,
    endDate?: string
  ): Observable<SignalStatsResponse> {
    const params: any = {};
    if (ticker) params.ticker = ticker;
    if (strategyName) params.strategy_name = strategyName;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    return this.api.get<SignalStatsResponse>('/signals/stats', params);
  }
}
