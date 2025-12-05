/**
 * Модели инструментов и индексов
 */

export interface Index {
  id: number;
  name: string;
  ticker: string;
  description?: string;
  currency_id?: number;
  country_id?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Instrument {
  id: number;
  ticker: string;
  name: string;
  market: string;
  instrument_type: string;
  index_id?: number;
  currency_id?: number;
  isin?: string;
  board?: string;
  lot_size?: number;
  tick_size?: string;
  extra_data?: any;
  index?: Index;
  created_at: string;
  updated_at?: string;
}

export interface InstrumentCreate {
  ticker: string;
  name: string;
  market: string;
  instrument_type: string;
  index_id?: number;
  currency_id?: number;
  isin?: string;
  board?: string;
  lot_size?: number;
  tick_size?: string;
  extra_data?: any;
}

export interface InstrumentUpdate {
  name?: string;
  market?: string;
  instrument_type?: string;
  index_id?: number;
  currency_id?: number;
  isin?: string;
  board?: string;
  lot_size?: number;
  tick_size?: string;
  extra_data?: any;
}

export interface IndexCreate {
  name: string;
  ticker: string;
  description?: string;
  currency_id?: number;
  country_id?: number;
}

export interface IndexUpdate {
  name?: string;
  description?: string;
  currency_id?: number;
  country_id?: number;
}

export interface InstrumentWithDetails extends Instrument {
  index_name?: string;
  index_ticker?: string;
  currency_code?: string;
  currency_symbol?: string;
}

export interface IndexWithDetails extends Index {
  instruments_count?: number;
  currency_code?: string;
  currency_symbol?: string;
  country_code?: string;
  country_name?: string;
}
