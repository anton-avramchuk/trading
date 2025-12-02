import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  OHLCVResponse,
  ImportCSVRequest,
  ImportCSVResponse,
  BatchImportRequest,
  BatchImportResponse
} from '../models/ohlcv.model';

/**
 * Сервис для работы с OHLCV данными
 */
@Injectable({
  providedIn: 'root'
})
export class OhlcvService {
  private readonly api = inject(ApiService);

  /**
   * Получить OHLCV данные для инструмента
   */
  getOHLCV(
    ticker: string,
    timeframe: string,
    startDate?: string,
    endDate?: string,
    limit?: number
  ): Observable<OHLCVResponse> {
    const params: any = { timeframe };
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (limit) params.limit = limit.toString();

    return this.api.get<OHLCVResponse>(`/data/${ticker}`, params);
  }

  /**
   * Импортировать CSV файл
   */
  importCSV(data: ImportCSVRequest): Observable<ImportCSVResponse> {
    return this.api.post<ImportCSVResponse>('/data/import-csv', data);
  }

  /**
   * Массовый импорт CSV файлов из директории
   */
  batchImport(data: BatchImportRequest): Observable<BatchImportResponse> {
    return this.api.post<BatchImportResponse>('/data/batch-import', data);
  }

  /**
   * Проверить наличие данных для инструмента
   */
  checkDataAvailability(ticker: string, timeframe: string): Observable<{
    has_data: boolean;
    start_date?: string;
    end_date?: string;
    count?: number;
  }> {
    return this.api.get(`/data/${ticker}/availability`, { timeframe });
  }
}
