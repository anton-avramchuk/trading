import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { OhlcvService } from './ohlcv.service';
import { ApiService } from './api.service';
import {
  OHLCVResponse,
  ImportCSVRequest,
  ImportCSVResponse,
  BatchImportRequest,
  BatchImportResponse
} from '../models/ohlcv.model';

describe('OhlcvService', () => {
  let service: OhlcvService;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockOHLCVResponse: OHLCVResponse = {
    ticker: 'GAZP',
    timeframe: '1d',
    data: [
      {
        timestamp: '2024-01-01T00:00:00Z',
        open: 150.0,
        high: 155.0,
        low: 148.0,
        close: 152.0,
        volume: 1000000
      }
    ],
    count: 1
  };

  const mockImportRequest: ImportCSVRequest = {
    csv_path: '/data/GAZP_1h.csv',
    ticker: 'GAZP',
    timeframe: '1h'
  };

  const mockImportResponse: ImportCSVResponse = {
    ticker: 'GAZP',
    timeframe: '1h',
    records_imported: 1000,
    instrument_created: false,
    message: 'Successfully imported 1000 records'
  };

  const mockBatchImportRequest: BatchImportRequest = {
    directory: '/data/moex',
    timeframe: '1d'
  };

  const mockBatchImportResponse: BatchImportResponse = {
    total_files: 10,
    successful: 10,
    failed: 0,
    results: [
      {
        ticker: 'GAZP',
        timeframe: '1d',
        records_imported: 1000,
        instrument_created: false,
        message: 'Successfully imported 1000 records'
      }
    ]
  };

  beforeEach(() => {
    const spy = jasmine.createSpyObj('ApiService', ['get', 'post']);

    TestBed.configureTestingModule({
      providers: [
        OhlcvService,
        { provide: ApiService, useValue: spy }
      ]
    });

    service = TestBed.inject(OhlcvService);
    apiServiceSpy = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get OHLCV data with required params only', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockOHLCVResponse));

    service.getOHLCV('GAZP', '1d').subscribe(response => {
      expect(response).toEqual(mockOHLCVResponse);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/data/GAZP', { timeframe: '1d' });
      done();
    });
  });

  it('should get OHLCV data with all params', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockOHLCVResponse));

    service.getOHLCV('GAZP', '1d', '2024-01-01', '2024-12-31', 100).subscribe(response => {
      expect(response).toEqual(mockOHLCVResponse);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/data/GAZP', {
        timeframe: '1d',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        limit: '100'
      });
      done();
    });
  });

  it('should get OHLCV data with partial optional params', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockOHLCVResponse));

    service.getOHLCV('GAZP', '1d', '2024-01-01').subscribe(response => {
      expect(response).toEqual(mockOHLCVResponse);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/data/GAZP', {
        timeframe: '1d',
        start_date: '2024-01-01'
      });
      done();
    });
  });

  it('should import CSV file', (done) => {
    apiServiceSpy.post.and.returnValue(of(mockImportResponse));

    service.importCSV(mockImportRequest).subscribe(response => {
      expect(response).toEqual(mockImportResponse);
      expect(apiServiceSpy.post).toHaveBeenCalledWith('/data/import-csv', mockImportRequest);
      done();
    });
  });

  it('should perform batch import', (done) => {
    apiServiceSpy.post.and.returnValue(of(mockBatchImportResponse));

    service.batchImport(mockBatchImportRequest).subscribe(response => {
      expect(response).toEqual(mockBatchImportResponse);
      expect(apiServiceSpy.post).toHaveBeenCalledWith('/data/batch-import', mockBatchImportRequest);
      done();
    });
  });

  it('should check data availability', (done) => {
    const mockAvailability = {
      has_data: true,
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      count: 1000
    };
    apiServiceSpy.get.and.returnValue(of(mockAvailability));

    service.checkDataAvailability('GAZP', '1d').subscribe(response => {
      expect(response).toEqual(mockAvailability);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/data/GAZP/availability', { timeframe: '1d' });
      done();
    });
  });

  it('should check data availability when no data exists', (done) => {
    const mockAvailability = {
      has_data: false
    };
    apiServiceSpy.get.and.returnValue(of(mockAvailability));

    service.checkDataAvailability('UNKNOWN', '1d').subscribe(response => {
      expect(response).toEqual(mockAvailability);
      expect(response.has_data).toBe(false);
      done();
    });
  });
});
