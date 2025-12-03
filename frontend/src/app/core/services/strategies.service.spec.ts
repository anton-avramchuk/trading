import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { StrategiesService } from './strategies.service';
import { ApiService } from './api.service';
import { StrategyInfo, StrategyDetails, StrategyListResponse } from '../models/strategy.model';

describe('StrategiesService', () => {
  let service: StrategiesService;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockStrategy: StrategyInfo = {
    name: 'MACDStrategy',
    description: 'MACD strategy description',
    version: '1.0.0',
    category: 'trend',
    parameters: []
  };

  const mockStrategyDetails: StrategyDetails = {
    name: 'MACDStrategy',
    description: 'MACD strategy description',
    version: '1.0.0',
    required_timeframes: ['1d'],
    indicators_config: [
      { name: 'MACD', timeframe: '1d', parameters: {}, alias: 'macd_1d' }
    ]
  };

  const mockStrategiesResponse: StrategyListResponse = {
    strategies: [mockStrategy],
    count: 1
  };

  beforeEach(() => {
    const spy = jasmine.createSpyObj('ApiService', ['get']);

    TestBed.configureTestingModule({
      providers: [
        StrategiesService,
        { provide: ApiService, useValue: spy }
      ]
    });

    service = TestBed.inject(StrategiesService);
    apiServiceSpy = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get strategies list', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockStrategiesResponse));

    service.getStrategies().subscribe(response => {
      expect(response).toEqual(mockStrategiesResponse);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/strategies', undefined);
      done();
    });
  });

  it('should get strategies by category', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockStrategiesResponse));

    service.getStrategies('trend').subscribe(response => {
      expect(response).toEqual(mockStrategiesResponse);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/strategies', { category: 'trend' });
      done();
    });
  });

  it('should get strategy info', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockStrategy));

    service.getStrategyInfo('MACDStrategy').subscribe(strategy => {
      expect(strategy).toEqual(mockStrategy);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/strategies/MACDStrategy');
      done();
    });
  });

  it('should get strategy details', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockStrategyDetails));

    service.getStrategyDetails('MACDStrategy').subscribe(details => {
      expect(details).toEqual(mockStrategyDetails);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/strategies/MACDStrategy/details');
      done();
    });
  });
});
