import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  StrategyInfo,
  StrategyDetails,
  StrategyListResponse,
  StrategySummary
} from '../models/strategy.model';

/**
 * Сервис для работы со стратегиями
 */
@Injectable({
  providedIn: 'root'
})
export class StrategiesService {
  private readonly api = inject(ApiService);

  /**
   * Получить список всех стратегий
   */
  getStrategies(category?: string): Observable<StrategyListResponse> {
    const params = category ? { category } : undefined;
    return this.api.get<StrategyListResponse>('/strategies', params);
  }

  /**
   * Получить информацию о стратегии
   */
  getStrategyInfo(strategyName: string): Observable<StrategyInfo> {
    return this.api.get<StrategyInfo>(`/strategies/${strategyName}`);
  }

  /**
   * Получить детальную информацию о стратегии (с индикаторами)
   */
  getStrategyDetails(strategyName: string): Observable<StrategyDetails> {
    return this.api.get<StrategyDetails>(`/strategies/${strategyName}/details`);
  }

  /**
   * Получить сводку по стратегиям
   */
  getStrategySummary(): Observable<StrategySummary> {
    return this.api.get<StrategySummary>('/strategies/summary');
  }

  /**
   * Получить список категорий стратегий
   */
  getCategories(): Observable<string[]> {
    return this.api.get<string[]>('/strategies/categories');
  }
}
