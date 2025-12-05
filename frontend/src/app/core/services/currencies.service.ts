import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Currency, CurrencyCreate, CurrencyUpdate } from '../models/currency.model';

@Injectable({
  providedIn: 'root'
})
export class CurrenciesService {
  private apiService = inject(ApiService);
  private readonly baseUrl = '/currencies';

  /**
   * Получить список валют
   */
  getCurrencies(params?: {
    skip?: number;
    limit?: number;
    active_only?: boolean;
  }): Observable<Currency[]> {
    const queryParams: { [key: string]: string } = {};
    if (params) {
      if (params.skip !== undefined) queryParams['skip'] = params.skip.toString();
      if (params.limit !== undefined) queryParams['limit'] = params.limit.toString();
      if (params.active_only !== undefined) queryParams['active_only'] = params.active_only.toString();
    }
    return this.apiService.get<Currency[]>(this.baseUrl, queryParams);
  }

  /**
   * Получить валюту по ID
   */
  getCurrency(id: number): Observable<Currency> {
    return this.apiService.get<Currency>(`${this.baseUrl}/${id}`);
  }

  /**
   * Получить валюту по коду
   */
  getCurrencyByCode(code: string): Observable<Currency> {
    return this.apiService.get<Currency>(`${this.baseUrl}/code/${code}`);
  }

  /**
   * Создать новую валюту
   */
  createCurrency(currency: CurrencyCreate): Observable<Currency> {
    return this.apiService.post<Currency>(this.baseUrl, currency);
  }

  /**
   * Обновить данные валюты
   */
  updateCurrency(id: number, currency: CurrencyUpdate): Observable<Currency> {
    return this.apiService.patch<Currency>(`${this.baseUrl}/${id}`, currency);
  }

  /**
   * Удалить валюту
   */
  deleteCurrency(id: number): Observable<void> {
    return this.apiService.delete<void>(`${this.baseUrl}/${id}`);
  }
}
