import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { SignalsService } from './signals.service';
import { ApiService } from './api.service';
import { Signal, SignalGenerateRequest, SignalGenerateResponse } from '../models/signal.model';

describe('SignalsService', () => {
  let service: SignalsService;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockSignal: Signal = {
    id: 1,
    instrument_id: 1,
    ticker: 'GAZP',
    strategy_name: 'MACDStrategy',
    signal_type: 'BUY',
    timestamp: new Date().toISOString(),
    price: 150.5,
    confidence: 0.85,
    position_size: 0.05,
    stop_loss: 145.0,
    take_profit: 160.0,
    created_at: new Date().toISOString()
  };

  const mockGenerateRequest: SignalGenerateRequest = {
    strategy_name: 'MACDStrategy',
    ticker: 'GAZP',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    use_risk_manager: true,
    save_to_db: true
  };

  const mockGenerateResponse: SignalGenerateResponse = {
    strategy_name: 'MACDStrategy',
    ticker: 'GAZP',
    total_points: 1000,
    signals_generated: 50,
    buy_signals: 25,
    sell_signals: 25,
    signals_saved: 50,
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    signals: [mockSignal]
  };

  beforeEach(() => {
    const spy = jasmine.createSpyObj('ApiService', ['get', 'post', 'delete']);

    TestBed.configureTestingModule({
      providers: [
        SignalsService,
        { provide: ApiService, useValue: spy }
      ]
    });

    service = TestBed.inject(SignalsService);
    apiServiceSpy = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get signals list', (done) => {
    const mockSignals: Signal[] = [mockSignal];
    apiServiceSpy.get.and.returnValue(of(mockSignals));

    service.getSignals().subscribe(signals => {
      expect(signals).toEqual(mockSignals);
      expect(apiServiceSpy.get).toHaveBeenCalled();
      done();
    });
  });

  it('should get signals with filters', (done) => {
    const mockSignals: Signal[] = [mockSignal];
    apiServiceSpy.get.and.returnValue(of(mockSignals));

    service.getSignals('GAZP', 'MACDStrategy', 'BUY', '2024-01-01', '2024-12-31').subscribe(signals => {
      expect(signals).toEqual(mockSignals);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/signals', jasmine.objectContaining({
        ticker: 'GAZP',
        strategy_name: 'MACDStrategy',
        signal_type: 'BUY',
        start_date: '2024-01-01',
        end_date: '2024-12-31'
      }));
      done();
    });
  });

  it('should get signal by id', (done) => {
    apiServiceSpy.get.and.returnValue(of(mockSignal));

    service.getSignal(1).subscribe(signal => {
      expect(signal).toEqual(mockSignal);
      expect(apiServiceSpy.get).toHaveBeenCalledWith('/signals/1');
      done();
    });
  });

  it('should generate signals', (done) => {
    apiServiceSpy.post.and.returnValue(of(mockGenerateResponse));

    service.generateSignals(mockGenerateRequest).subscribe(response => {
      expect(response).toEqual(mockGenerateResponse);
      expect(apiServiceSpy.post).toHaveBeenCalledWith('/signals/generate', mockGenerateRequest);
      done();
    });
  });

  it('should delete signal', (done) => {
    const response = { message: 'Signal deleted successfully' };
    apiServiceSpy.delete.and.returnValue(of(response));

    service.deleteSignal(1).subscribe(result => {
      expect(result).toEqual(response);
      expect(apiServiceSpy.delete).toHaveBeenCalledWith('/signals/1');
      done();
    });
  });
});
