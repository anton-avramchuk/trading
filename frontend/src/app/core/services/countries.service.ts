import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Country, CountryCreate, CountryUpdate } from '../models/country.model';

@Injectable({
  providedIn: 'root'
})
export class CountriesService {
  private apiService = inject(ApiService);
  private readonly baseUrl = '/countries';

  /**
   * Получить список стран
   */
  getCountries(params?: {
    skip?: number;
    limit?: number;
    active_only?: boolean;
    region?: string;
  }): Observable<Country[]> {
    const queryParams: { [key: string]: string } = {};
    if (params) {
      if (params.skip !== undefined) queryParams['skip'] = params.skip.toString();
      if (params.limit !== undefined) queryParams['limit'] = params.limit.toString();
      if (params.active_only !== undefined) queryParams['active_only'] = params.active_only.toString();
      if (params.region !== undefined) queryParams['region'] = params.region;
    }
    return this.apiService.get<Country[]>(this.baseUrl, queryParams);
  }

  /**
   * Получить страну по ID
   */
  getCountry(id: number): Observable<Country> {
    return this.apiService.get<Country>(`${this.baseUrl}/${id}`);
  }

  /**
   * Получить страну по коду
   */
  getCountryByCode(code: string): Observable<Country> {
    return this.apiService.get<Country>(`${this.baseUrl}/code/${code}`);
  }

  /**
   * Создать новую страну
   */
  createCountry(country: CountryCreate): Observable<Country> {
    return this.apiService.post<Country>(this.baseUrl, country);
  }

  /**
   * Обновить данные страны
   */
  updateCountry(id: number, country: CountryUpdate): Observable<Country> {
    return this.apiService.patch<Country>(`${this.baseUrl}/${id}`, country);
  }

  /**
   * Удалить страну
   */
  deleteCountry(id: number): Observable<void> {
    return this.apiService.delete<void>(`${this.baseUrl}/${id}`);
  }
}
