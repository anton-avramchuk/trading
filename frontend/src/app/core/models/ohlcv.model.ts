/**
 * Модели OHLCV данных
 */

export interface OHLCV {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OHLCVResponse {
  ticker: string;
  timeframe: string;
  data: OHLCV[];
  count: number;
}

export interface ImportCSVRequest {
  ticker: string;
  csv_path: string;
  timeframe: string;
  create_instrument?: boolean;
  instrument_name?: string;
  market?: string;
  instrument_type?: string;
}

export interface ImportCSVResponse {
  ticker: string;
  timeframe: string;
  records_imported: number;
  instrument_created: boolean;
  message: string;
}

export interface BatchImportRequest {
  directory: string;
  timeframe: string;
  pattern?: string;
  create_instruments?: boolean;
}

export interface BatchImportResponse {
  total_files: number;
  successful: number;
  failed: number;
  results: ImportCSVResponse[];
}
