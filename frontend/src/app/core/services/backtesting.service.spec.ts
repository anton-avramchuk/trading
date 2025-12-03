import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { BacktestingService } from './backtesting.service';
import { ApiService } from './api.service';
import {
  BacktestConfig,
  BacktestResult,
  BacktestRunResponse,
  BacktestListItem
} from '../models/backtest.model';

describe('BacktestingService', () => {
  let service: BacktestingService;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockConfig: BacktestConfig = {
    strategy_name: 'MACDStrategy',
    ticker: 'GAZP',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    initial_capital: 100000,
    commission: 0.001,
    slippage: 0.0005
  };

  const mockRunResponse: BacktestRunResponse = {
    backtest_id: 'bt-123',
    status: 'running'
  };

  const mockBacktestResult: BacktestResult = {
    config: mockConfig,
    metrics: {
      total_return: 15000,
      total_return_percent: 0.15,
      sharpe_ratio: 1.5,
      sortino_ratio: 1.8,
      max_drawdown: -8000,
      max_drawdown_percent: -0.08,
      win_rate: 0.6,
      profit_factor: 1.8,
      avg_win: 800,
      avg_loss: -400,
      avg_win_percent: 0.05,
      avg_loss_percent: -0.025,
      largest_win: 2000,
      largest_loss: -1000,
      total_trades: 50,
      winning_trades: 30,
      losing_trades: 20,
      avg_trade_duration: 5,
      expectancy: 300,
      kelly_criterion: 0.05
    },
    trades: [],
    equity_curve: [],
    completed_at: '2024-01-01T01:00:00Z'
  };

  const mockBacktestListItem: BacktestListItem = {
    backtest_id: 'bt-123',
    strategy_name: 'MACDStrategy',
    ticker: 'GAZP',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    initial_capital: 100000,
    status: 'completed',
    total_return: 0.15,
    created_at: '2024-01-01T00:00:00Z'
  };

  beforeEach(() => {
    const spy = jasmine.createSpyObj('ApiService', ['get', 'post', 'delete']);

    TestBed.configureTestingModule({
      providers: [
        BacktestingService,
        { provide: ApiService, useValue: spy }
      ]
    });

    service = TestBed.inject(BacktestingService);
    apiServiceSpy = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should run backtest', (done) => {
    apiServiceSpy.post.and.returnValue(of(mockRunResponse));

    service.runBacktest(mockConfig).subscribe(response => {
      expect(response).toEqual(mockRunResponse);
      expect(apiServiceSpy.post).toHaveBeenCalledWith('/backtest/run', mockConfig);
      done();
    });
  });

  it('should get backtest result', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockBacktestResult));

    service.getBacktestResult('bt-123').subscribe(result => {
      expect(result).toEqual(mockBacktestResult);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/backtest/bt-123');
      done();
    });
  });

  it('should get backtests list with default params', (done) => {
    const mockList = [mockBacktestListItem];
    apiServiceSpy.get.and.returnValue(of(mockList));

    service.getBacktests().subscribe(list => {
      expect(list).toEqual(mockList);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/backtest', {
        skip: '0',
        limit: '100'
      });
      done();
    });
  });

  it('should get backtests list with all filters', (done) => {
    const mockList = [mockBacktestListItem];
    apiServiceSpy.get.and.returnValue(of(mockList));

    service.getBacktests('GAZP', 'MACDStrategy', 'completed', 10, 50).subscribe(list => {
      expect(list).toEqual(mockList);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/backtest', {
        ticker: 'GAZP',
        strategy_name: 'MACDStrategy',
        status: 'completed',
        skip: '10',
        limit: '50'
      });
      done();
    });
  });

  it('should get backtests list with partial filters', (done) => {
    const mockList = [mockBacktestListItem];
    apiServiceSpy.get.and.returnValue(of(mockList));

    service.getBacktests('GAZP', undefined, 'running').subscribe(list => {
      expect(list).toEqual(mockList);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/backtest', {
        ticker: 'GAZP',
        status: 'running',
        skip: '0',
        limit: '100'
      });
      done();
    });
  });

  it('should delete backtest', (done) => {
    const response = { message: 'Backtest deleted successfully' };
    apiServiceSpy.delete.and.returnValue(of(response));

    service.deleteBacktest('bt-123').subscribe(result => {
      expect(result).toEqual(response);
      expect(apiServiceSpy.delete).toHaveBeenCalledWith('/backtest/bt-123');
      done();
    });
  });

  it('should compare backtests', (done) => {
    const mockComparison = {
      backtests: [mockBacktestResult],
      comparison_metrics: {
        best_return: 'bt-123',
        best_sharpe: 'bt-123'
      }
    };
    apiServiceSpy.post.and.returnValue(of(mockComparison));

    service.compareBacktests(['bt-123', 'bt-456']).subscribe(result => {
      expect(result).toEqual(mockComparison);
      expect(apiServiceSpy.post).toHaveBeenCalledWith('/backtest/compare', {
        backtest_ids: ['bt-123', 'bt-456']
      });
      done();
    });
  });

  it('should export backtest', (done) => {
    const mockBlob = new Blob(['test'], { type: 'text/csv' });
    apiServiceSpy.get.and.returnValue(of(mockBlob));

    service.exportBacktest('bt-123').subscribe(blob => {
      expect(blob).toEqual(mockBlob);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/backtest/bt-123/export');
      done();
    });
  });
});
