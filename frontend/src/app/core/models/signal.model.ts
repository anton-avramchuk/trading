/**
 * Модели торговых сигналов
 */

export interface Signal {
  id: number;
  instrument_id: number;
  ticker: string;
  strategy_name: string;
  signal_type: 'BUY' | 'SELL' | 'HOLD';
  timestamp: string;
  price: number;
  confidence?: number;
  position_size?: number;
  stop_loss?: number;
  take_profit?: number;
  created_at: string;
}

export interface SignalGenerateRequest {
  strategy_name: string;
  ticker: string;
  start_date?: string;
  end_date?: string;
  use_risk_manager?: boolean;
  max_position_size?: number;
  atr_multiplier_sl?: number;
  atr_multiplier_tp?: number;
  min_confidence?: number;
  remove_duplicates?: boolean;
  save_to_db?: boolean;
}

export interface SignalGenerateResponse {
  strategy_name: string;
  ticker: string;
  total_points: number;
  signals_generated: number;
  buy_signals: number;
  sell_signals: number;
  signals_saved: number;
  start_date?: string;
  end_date?: string;
  signals: Signal[];
}

export interface SignalStatsResponse {
  total_signals: number;
  buy_signals: number;
  sell_signals: number;
  unique_strategies: number;
  unique_instruments: number;
  avg_confidence?: number;
  date_range?: {
    min: string;
    max: string;
  };
}
