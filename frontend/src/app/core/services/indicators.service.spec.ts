import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { IndicatorsService } from './indicators.service';
import { ApiService } from './api.service';
import {
  IndicatorInfo,
  IndicatorListResponse,
  IndicatorCalculateRequest,
  IndicatorCalculateResponse,
  IndicatorUsageStats
} from '../models/indicator.model';

describe('IndicatorsService', () => {
  let service: IndicatorsService;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockIndicator: IndicatorInfo = {
    name: 'MACD',
    description: 'Moving Average Convergence Divergence',
    category: 'trend',
    parameters: [
      { name: 'fast_period', type: 'int', default: 12, description: 'Fast EMA period' },
      { name: 'slow_period', type: 'int', default: 26, description: 'Slow EMA period' },
      { name: 'signal_period', type: 'int', default: 9, description: 'Signal line period' }
    ]
  };

  const mockIndicatorListResponse: IndicatorListResponse = {
    indicators: [mockIndicator],
    count: 1,
    categories: ['trend', 'momentum', 'volatility', 'volume']
  };

  const mockCalculateRequest: IndicatorCalculateRequest = {
    indicator_name: 'MACD',
    ticker: 'GAZP',
    timeframe: '1d',
    parameters: {
      fast_period: 12,
      slow_period: 26,
      signal_period: 9
    }
  };

  const mockCalculateResponse: IndicatorCalculateResponse = {
    indicator_name: 'MACD',
    ticker: 'GAZP',
    timeframe: '1d',
    result_type: 'continuous',
    data: {
      '2024-01-01T00:00:00Z': {
        macd: 1.5,
        signal: 1.2,
        histogram: 0.3
      }
    }
  };

  const mockUsageStats: IndicatorUsageStats = {
    total_calculations: 1250,
    by_category: {
      trend: 500,
      momentum: 400,
      volatility: 250,
      volume: 100
    },
    most_used: ['MACD', 'RSI', 'SMA']
  };

  beforeEach(() => {
    const spy = jasmine.createSpyObj('ApiService', ['get', 'post']);

    TestBed.configureTestingModule({
      providers: [
        IndicatorsService,
        { provide: ApiService, useValue: spy }
      ]
    });

    service = TestBed.inject(IndicatorsService);
    apiServiceSpy = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get indicators list without category', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockIndicatorListResponse));

    service.getIndicators().subscribe(response => {
      expect(response).toEqual(mockIndicatorListResponse);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/indicators', undefined);
      done();
    });
  });

  it('should get indicators list by category', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockIndicatorListResponse));

    service.getIndicators('trend').subscribe(response => {
      expect(response).toEqual(mockIndicatorListResponse);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/indicators', { category: 'trend' });
      done();
    });
  });

  it('should get indicator info', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockIndicator));

    service.getIndicatorInfo('MACD').subscribe(indicator => {
      expect(indicator).toEqual(mockIndicator);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/indicators/MACD');
      done();
    });
  });

  it('should calculate indicator', (done) => {
    apiServiceSpy.post.and.returnValue(of(mockCalculateResponse));

    service.calculateIndicator(mockCalculateRequest).subscribe(response => {
      expect(response).toEqual(mockCalculateResponse);
      expect(apiServiceSpy.post).toHaveBeenCalledWith('/indicators/calculate', mockCalculateRequest);
      done();
    });
  });

  it('should get categories', (done) => {
    const categories = ['trend', 'momentum', 'volatility', 'volume'];
    apiServiceSpy.get.and.returnValue(of(categories));

    service.getCategories().subscribe(result => {
      expect(result).toEqual(categories);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/indicators/categories');
      done();
    });
  });

  it('should get usage stats', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockUsageStats));

    service.getUsageStats().subscribe(stats => {
      expect(stats).toEqual(mockUsageStats);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/indicators/stats');
      done();
    });
  });
});
