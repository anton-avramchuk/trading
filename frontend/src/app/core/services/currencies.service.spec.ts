import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { CurrenciesService } from './currencies.service';
import { Currency, CurrencyCreate, CurrencyUpdate } from '../models/currency.model';

describe('CurrenciesService', () => {
  let service: CurrenciesService;
  let httpMock: HttpTestingController;
  const baseUrl = '/api/v1/currencies';

  const mockCurrency: Currency = {
    id: 1,
    code: 'RUB',
    numeric_code: '643',
    name: 'Российский рубль',
    name_en: 'Russian Ruble',
    symbol: '₽',
    decimal_places: 2,
    is_active: 1,
    created_at: '2025-01-01T00:00:00Z'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        CurrenciesService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });
    service = TestBed.inject(CurrenciesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getCurrencies', () => {
    it('should fetch currencies list', () => {
      const mockCurrencies: Currency[] = [mockCurrency];

      service.getCurrencies().subscribe(currencies => {
        expect(currencies.length).toBe(1);
        expect(currencies[0]).toEqual(mockCurrency);
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('GET');
      req.flush(mockCurrencies);
    });

    it('should fetch currencies with parameters', () => {
      const mockCurrencies: Currency[] = [mockCurrency];
      const params = { skip: 10, limit: 50, active_only: true };

      service.getCurrencies(params).subscribe(currencies => {
        expect(currencies).toEqual(mockCurrencies);
      });

      const req = httpMock.expectOne(req => req.url === baseUrl);
      expect(req.request.method).toBe('GET');
      expect(req.request.params.get('skip')).toBe('10');
      expect(req.request.params.get('limit')).toBe('50');
      expect(req.request.params.get('active_only')).toBe('true');
      req.flush(mockCurrencies);
    });

    it('should handle empty list', () => {
      service.getCurrencies().subscribe(currencies => {
        expect(currencies).toEqual([]);
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush([]);
    });
  });

  describe('getCurrency', () => {
    it('should fetch currency by ID', () => {
      service.getCurrency(1).subscribe(currency => {
        expect(currency).toEqual(mockCurrency);
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockCurrency);
    });

    it('should handle 404 error', () => {
      service.getCurrency(999).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('getCurrencyByCode', () => {
    it('should fetch currency by code', () => {
      service.getCurrencyByCode('RUB').subscribe(currency => {
        expect(currency).toEqual(mockCurrency);
      });

      const req = httpMock.expectOne(`${baseUrl}/code/RUB`);
      expect(req.request.method).toBe('GET');
      req.flush(mockCurrency);
    });

    it('should handle 404 for non-existent code', () => {
      service.getCurrencyByCode('XXX').subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/code/XXX`);
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('createCurrency', () => {
    it('should create new currency', () => {
      const newCurrency: CurrencyCreate = {
        code: 'USD',
        numeric_code: '840',
        name: 'Доллар США',
        name_en: 'US Dollar',
        symbol: '$',
        decimal_places: 2,
        is_active: 1
      };

      service.createCurrency(newCurrency).subscribe(currency => {
        expect(currency.code).toBe('USD');
        expect(currency.id).toBe(2);
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newCurrency);
      req.flush({ ...newCurrency, id: 2, created_at: '2025-01-02T00:00:00Z' });
    });

    it('should handle validation errors', () => {
      const invalidCurrency: CurrencyCreate = {
        code: '',
        name: 'Invalid'
      };

      service.createCurrency(invalidCurrency).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(400);
        }
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush('Validation error', { status: 400, statusText: 'Bad Request' });
    });
  });

  describe('updateCurrency', () => {
    it('should update currency', () => {
      const update: CurrencyUpdate = {
        symbol: '₽₽'
      };

      service.updateCurrency(1, update).subscribe(currency => {
        expect(currency.symbol).toBe('₽₽');
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual(update);
      req.flush({ ...mockCurrency, symbol: '₽₽' });
    });

    it('should handle 404 on update', () => {
      const update: CurrencyUpdate = { symbol: '$' };

      service.updateCurrency(999, update).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('deleteCurrency', () => {
    it('should delete currency', () => {
      service.deleteCurrency(1).subscribe(() => {
        expect(true).toBe(true);
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle 404 on delete', () => {
      service.deleteCurrency(999).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });
});
