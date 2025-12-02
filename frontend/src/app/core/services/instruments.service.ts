import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  Instrument,
  InstrumentCreate,
  InstrumentUpdate,
  Index,
  IndexCreate
} from '../models/instrument.model';

/**
 * Сервис для работы с инструментами и индексами
 */
@Injectable({
  providedIn: 'root'
})
export class InstrumentsService {
  private readonly api = inject(ApiService);

  /**
   * Получить список всех инструментов
   */
  getInstruments(skip: number = 0, limit: number = 100): Observable<Instrument[]> {
    return this.api.get<Instrument[]>('/instruments', { skip: skip.toString(), limit: limit.toString() });
  }

  /**
   * Получить инструмент по тикеру
   */
  getInstrument(ticker: string): Observable<Instrument> {
    return this.api.get<Instrument>(`/instruments/${ticker}`);
  }

  /**
   * Создать новый инструмент
   */
  createInstrument(data: InstrumentCreate): Observable<Instrument> {
    return this.api.post<Instrument>('/instruments', data);
  }

  /**
   * Обновить инструмент
   */
  updateInstrument(ticker: string, data: InstrumentUpdate): Observable<Instrument> {
    return this.api.put<Instrument>(`/instruments/${ticker}`, data);
  }

  /**
   * Удалить инструмент
   */
  deleteInstrument(ticker: string): Observable<{ message: string }> {
    return this.api.delete<{ message: string }>(`/instruments/${ticker}`);
  }

  /**
   * Получить список всех индексов
   */
  getIndexes(): Observable<Index[]> {
    return this.api.get<Index[]>('/indexes');
  }

  /**
   * Получить индекс по тикеру
   */
  getIndex(ticker: string): Observable<Index> {
    return this.api.get<Index>(`/indexes/${ticker}`);
  }

  /**
   * Создать новый индекс
   */
  createIndex(data: IndexCreate): Observable<Index> {
    return this.api.post<Index>('/indexes', data);
  }

  /**
   * Удалить индекс
   */
  deleteIndex(ticker: string): Observable<{ message: string }> {
    return this.api.delete<{ message: string }>(`/indexes/${ticker}`);
  }

  /**
   * Получить инструменты, входящие в индекс
   */
  getInstrumentsByIndex(indexTicker: string): Observable<Instrument[]> {
    return this.api.get<Instrument[]>(`/indexes/${indexTicker}/instruments`);
  }
}
