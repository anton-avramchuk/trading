import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  IndicatorInfo,
  IndicatorListResponse,
  IndicatorCalculateRequest,
  IndicatorCalculateResponse,
  IndicatorUsageStats
} from '../models/indicator.model';

/**
 * Сервис для работы с индикаторами
 */
@Injectable({
  providedIn: 'root'
})
export class IndicatorsService {
  private readonly api = inject(ApiService);

  /**
   * Получить список всех индикаторов
   */
  getIndicators(category?: string): Observable<IndicatorListResponse> {
    const params = category ? { category } : undefined;
    return this.api.get<IndicatorListResponse>('/indicators', params);
  }

  /**
   * Получить информацию о конкретном индикаторе
   */
  getIndicatorInfo(indicatorName: string): Observable<IndicatorInfo> {
    return this.api.get<IndicatorInfo>(`/indicators/${indicatorName}`);
  }

  /**
   * Рассчитать индикатор
   */
  calculateIndicator(data: IndicatorCalculateRequest): Observable<IndicatorCalculateResponse> {
    return this.api.post<IndicatorCalculateResponse>('/indicators/calculate', data);
  }

  /**
   * Получить категории индикаторов
   */
  getCategories(): Observable<string[]> {
    return this.api.get<string[]>('/indicators/categories');
  }

  /**
   * Получить статистику использования индикаторов
   */
  getUsageStats(): Observable<IndicatorUsageStats> {
    return this.api.get<IndicatorUsageStats>('/indicators/stats');
  }
}
