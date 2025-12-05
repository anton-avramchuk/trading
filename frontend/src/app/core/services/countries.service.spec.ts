import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { CountriesService } from './countries.service';
import { Country, CountryCreate, CountryUpdate } from '../models/country.model';

describe('CountriesService', () => {
  let service: CountriesService;
  let httpMock: HttpTestingController;
  const baseUrl = '/api/v1/countries';

  const mockCountry: Country = {
    id: 1,
    code: 'RU',
    code3: 'RUS',
    name: 'Россия',
    name_en: 'Russia',
    region: 'Europe',
    is_active: 1,
    created_at: '2025-01-01T00:00:00Z'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        CountriesService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });
    service = TestBed.inject(CountriesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getCountries', () => {
    it('should fetch countries list', () => {
      const mockCountries: Country[] = [mockCountry];

      service.getCountries().subscribe(countries => {
        expect(countries.length).toBe(1);
        expect(countries[0]).toEqual(mockCountry);
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('GET');
      req.flush(mockCountries);
    });

    it('should fetch countries with parameters', () => {
      const mockCountries: Country[] = [mockCountry];
      const params = { skip: 0, limit: 100, active_only: true, region: 'Europe' };

      service.getCountries(params).subscribe(countries => {
        expect(countries).toEqual(mockCountries);
      });

      const req = httpMock.expectOne(req => req.url === baseUrl);
      expect(req.request.method).toBe('GET');
      expect(req.request.params.get('active_only')).toBe('true');
      expect(req.request.params.get('region')).toBe('Europe');
      req.flush(mockCountries);
    });

    it('should handle empty list', () => {
      service.getCountries().subscribe(countries => {
        expect(countries).toEqual([]);
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush([]);
    });
  });

  describe('getCountry', () => {
    it('should fetch country by ID', () => {
      service.getCountry(1).subscribe(country => {
        expect(country).toEqual(mockCountry);
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockCountry);
    });

    it('should handle 404 error', () => {
      service.getCountry(999).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('getCountryByCode', () => {
    it('should fetch country by code', () => {
      service.getCountryByCode('RU').subscribe(country => {
        expect(country).toEqual(mockCountry);
      });

      const req = httpMock.expectOne(`${baseUrl}/code/RU`);
      expect(req.request.method).toBe('GET');
      req.flush(mockCountry);
    });

    it('should handle 404 for non-existent code', () => {
      service.getCountryByCode('XX').subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/code/XX`);
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('createCountry', () => {
    it('should create new country', () => {
      const newCountry: CountryCreate = {
        code: 'US',
        code3: 'USA',
        name: 'США',
        name_en: 'United States',
        region: 'Americas',
        is_active: 1
      };

      service.createCountry(newCountry).subscribe(country => {
        expect(country.code).toBe('US');
        expect(country.id).toBe(2);
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newCountry);
      req.flush({ ...newCountry, id: 2, created_at: '2025-01-02T00:00:00Z' });
    });

    it('should handle validation errors', () => {
      const invalidCountry: CountryCreate = {
        code: 'INVALID',
        name: 'Invalid'
      };

      service.createCountry(invalidCountry).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(400);
        }
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush('Validation error', { status: 400, statusText: 'Bad Request' });
    });
  });

  describe('updateCountry', () => {
    it('should update country', () => {
      const update: CountryUpdate = {
        region: 'Eastern Europe'
      };

      service.updateCountry(1, update).subscribe(country => {
        expect(country.region).toBe('Eastern Europe');
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual(update);
      req.flush({ ...mockCountry, region: 'Eastern Europe' });
    });

    it('should handle 404 on update', () => {
      const update: CountryUpdate = { region: 'Asia' };

      service.updateCountry(999, update).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('deleteCountry', () => {
    it('should delete country', () => {
      service.deleteCountry(1).subscribe(() => {
        expect(true).toBe(true);
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle 404 on delete', () => {
      service.deleteCountry(999).subscribe({
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
