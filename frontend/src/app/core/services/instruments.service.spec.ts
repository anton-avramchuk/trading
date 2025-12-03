import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { InstrumentsService } from './instruments.service';
import { ApiService } from './api.service';
import { Instrument, InstrumentCreate, InstrumentUpdate, Index, IndexCreate } from '../models/instrument.model';

describe('InstrumentsService', () => {
  let service: InstrumentsService;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockInstrument: Instrument = {
    id: 1,
    ticker: 'GAZP',
    name: 'Газпром',
    market: 'MOEX',
    instrument_type: 'stock',
    index_id: 1,
    created_at: new Date().toISOString()
  };

  const mockIndex: Index = {
    id: 1,
    name: 'IMOEX',
    ticker: 'IMOEX'
  };

  beforeEach(() => {
    const spy = jasmine.createSpyObj('ApiService', ['get', 'post', 'put', 'delete']);

    TestBed.configureTestingModule({
      providers: [
        InstrumentsService,
        { provide: ApiService, useValue: spy }
      ]
    });

    service = TestBed.inject(InstrumentsService);
    apiServiceSpy = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('Instruments', () => {
    it('should get instruments list', (done) => {
      const mockInstruments: Instrument[] = [mockInstrument];
      apiServiceSpy.get.and.returnValue(of(mockInstruments));

      service.getInstruments(0, 100).subscribe(instruments => {
        expect(instruments).toEqual(mockInstruments);
        expect(apiServiceSpy.get).toHaveBeenCalledWith('/instruments', {
          skip: '0',
          limit: '100'
        });
        done();
      });
    });

    it('should get instrument by ticker', (done) => {
      apiServiceSpy.get.and.returnValue(of(mockInstrument));

      service.getInstrument('GAZP').subscribe(instrument => {
        expect(instrument).toEqual(mockInstrument);
        expect(apiServiceSpy.get).toHaveBeenCalledWith('/instruments/GAZP');
        done();
      });
    });

    it('should create instrument', (done) => {
      const newInstrument: InstrumentCreate = {
        ticker: 'GAZP',
        name: 'Газпром',
        market: 'MOEX',
        instrument_type: 'stock'
      };
      apiServiceSpy.post.and.returnValue(of(mockInstrument));

      service.createInstrument(newInstrument).subscribe(instrument => {
        expect(instrument).toEqual(mockInstrument);
        expect(apiServiceSpy.post).toHaveBeenCalledWith('/instruments', newInstrument);
        done();
      });
    });

    it('should update instrument', (done) => {
      const updateData: InstrumentUpdate = {
        name: 'Газпром обновленный'
      };
      const updatedInstrument = { ...mockInstrument, ...updateData };
      apiServiceSpy.put.and.returnValue(of(updatedInstrument));

      service.updateInstrument('GAZP', updateData).subscribe(instrument => {
        expect(instrument).toEqual(updatedInstrument);
        expect(apiServiceSpy.put).toHaveBeenCalledWith('/instruments/GAZP', updateData);
        done();
      });
    });

    it('should delete instrument', (done) => {
      const response = { message: 'Instrument deleted successfully' };
      apiServiceSpy.delete.and.returnValue(of(response));

      service.deleteInstrument('GAZP').subscribe(result => {
        expect(result).toEqual(response);
        expect(apiServiceSpy.delete).toHaveBeenCalledWith('/instruments/GAZP');
        done();
      });
    });
  });

  describe('Indexes', () => {
    it('should get indexes list', (done) => {
      const mockIndexes: Index[] = [mockIndex];
      apiServiceSpy.get.and.returnValue(of(mockIndexes));

      service.getIndexes().subscribe(indexes => {
        expect(indexes).toEqual(mockIndexes);
        expect(apiServiceSpy.get).toHaveBeenCalledWith('/indexes');
        done();
      });
    });

    it('should get index by ticker', (done) => {
      apiServiceSpy.get.and.returnValue(of(mockIndex));

      service.getIndex('IMOEX').subscribe(index => {
        expect(index).toEqual(mockIndex);
        expect(apiServiceSpy.get).toHaveBeenCalledWith('/indexes/IMOEX');
        done();
      });
    });

    it('should create index', (done) => {
      const newIndex: IndexCreate = {
        name: 'IMOEX',
        ticker: 'IMOEX'
      };
      apiServiceSpy.post.and.returnValue(of(mockIndex));

      service.createIndex(newIndex).subscribe(index => {
        expect(index).toEqual(mockIndex);
        expect(apiServiceSpy.post).toHaveBeenCalledWith('/indexes', newIndex);
        done();
      });
    });

    it('should delete index', (done) => {
      const response = { message: 'Index deleted successfully' };
      apiServiceSpy.delete.and.returnValue(of(response));

      service.deleteIndex('IMOEX').subscribe(result => {
        expect(result).toEqual(response);
        expect(apiServiceSpy.delete).toHaveBeenCalledWith('/indexes/IMOEX');
        done();
      });
    });

    it('should get instruments by index', (done) => {
      const mockInstruments: Instrument[] = [mockInstrument];
      apiServiceSpy.get.and.returnValue(of(mockInstruments));

      service.getInstrumentsByIndex('IMOEX').subscribe(instruments => {
        expect(instruments).toEqual(mockInstruments);
        expect(apiServiceSpy.get).toHaveBeenCalledWith('/indexes/IMOEX/instruments');
        done();
      });
    });
  });
});
