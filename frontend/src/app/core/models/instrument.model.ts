/**
 * Модели инструментов и индексов
 */

export interface Index {
  id: number;
  name: string;
  ticker: string;
}

export interface Instrument {
  id: number;
  ticker: string;
  name: string;
  market: string;
  instrument_type: string;
  index_id?: number;
  index?: Index;
  created_at: string;
}

export interface InstrumentCreate {
  ticker: string;
  name: string;
  market: string;
  instrument_type: string;
  index_id?: number;
}

export interface InstrumentUpdate {
  name?: string;
  market?: string;
  instrument_type?: string;
  index_id?: number;
}

export interface IndexCreate {
  name: string;
  ticker: string;
}
