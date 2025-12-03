import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { HttpParams } from '@angular/common/http';
import { ApiService } from './api.service';
import { environment } from '../../../environments/environment';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;
  const apiUrl = environment.apiUrl;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        ApiService
      ]
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('GET requests', () => {
    it('should make GET request without params', () => {
      const endpoint = '/test';
      const mockResponse = { data: 'test' };

      service.get(endpoint).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should make GET request with params', () => {
      const endpoint = '/test';
      const params = { id: '123', name: 'test' };
      const mockResponse = { data: 'test' };

      service.get(endpoint, params).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${apiUrl}${endpoint}` &&
        request.params.get('id') === '123' &&
        request.params.get('name') === 'test'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });
  });

  describe('POST requests', () => {
    it('should make POST request', () => {
      const endpoint = '/test';
      const body = { name: 'test', value: 123 };
      const mockResponse = { id: 1, ...body };

      service.post(endpoint, body).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(body);
      req.flush(mockResponse);
    });

    it('should make POST request with custom headers', () => {
      const endpoint = '/test';
      const body = { name: 'test' };
      const mockResponse = { success: true };

      service.post(endpoint, body, {
        headers: { 'X-Custom-Header': 'value' } as any
      }).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      expect(req.request.method).toBe('POST');
      expect(req.request.headers.get('X-Custom-Header')).toBe('value');
      req.flush(mockResponse);
    });
  });

  describe('PUT requests', () => {
    it('should make PUT request', () => {
      const endpoint = '/test/1';
      const body = { name: 'updated' };
      const mockResponse = { id: 1, ...body };

      service.put(endpoint, body).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(body);
      req.flush(mockResponse);
    });
  });

  describe('PATCH requests', () => {
    it('should make PATCH request', () => {
      const endpoint = '/test/1';
      const body = { name: 'patched' };
      const mockResponse = { id: 1, name: 'patched', value: 123 };

      service.patch(endpoint, body).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual(body);
      req.flush(mockResponse);
    });
  });

  describe('DELETE requests', () => {
    it('should make DELETE request', () => {
      const endpoint = '/test/1';
      const mockResponse = { message: 'Deleted successfully' };

      service.delete(endpoint).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      expect(req.request.method).toBe('DELETE');
      req.flush(mockResponse);
    });
  });

  describe('Error handling', () => {
    it('should handle HTTP error', () => {
      const endpoint = '/test';
      const errorMessage = 'Not Found';

      service.get(endpoint).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
          expect(error.statusText).toBe(errorMessage);
        }
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      req.flush(null, { status: 404, statusText: errorMessage });
    });

    it('should handle network error', () => {
      const endpoint = '/test';
      const errorEvent = new ErrorEvent('Network error');

      service.get(endpoint).subscribe({
        next: () => fail('should have failed with network error'),
        error: (error) => {
          expect(error.error).toBe(errorEvent);
        }
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      req.error(errorEvent);
    });
  });

  describe('Edge cases', () => {
    it('should handle GET with HttpParams object', () => {
      const endpoint = '/test';
      const params = new HttpParams().set('key', 'value').set('foo', 'bar');
      const mockResponse = { data: 'test' };

      service.get(endpoint, params).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${apiUrl}${endpoint}` &&
        request.params.get('key') === 'value' &&
        request.params.get('foo') === 'bar'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should handle POST without options', () => {
      const endpoint = '/test';
      const body = { data: 'test' };
      const mockResponse = { success: true };

      service.post(endpoint, body).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}${endpoint}`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(body);
      req.flush(mockResponse);
    });

    it('should handle GET with array params', () => {
      const endpoint = '/test';
      const params = { ids: ['1', '2', '3'] };
      const mockResponse = { data: [] };

      service.get(endpoint, params).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(request => request.url === `${apiUrl}${endpoint}`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });
  });
});
