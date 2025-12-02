/**
 * Модели бэктестинга
 */

export interface BacktestConfig {
  strategy_name: string;
  ticker: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission: number;
  slippage: number;
  use_risk_manager?: boolean;
  max_position_size?: number;
  atr_multiplier_sl?: number;
  atr_multiplier_tp?: number;
}

export interface BacktestTrade {
  entry_date: string;
  entry_price: number;
  exit_date: string;
  exit_price: number;
  side: 'LONG' | 'SHORT';
  size: number;
  pnl: number;
  pnl_percent: number;
  commission: number;
  mae: number;
  mfe: number;
  duration_bars: number;
  exit_reason: string;
}

export interface BacktestMetrics {
  total_return: number;
  total_return_percent: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  max_drawdown_percent: number;
  win_rate: number;
  profit_factor: number;
  avg_win: number;
  avg_loss: number;
  avg_win_percent: number;
  avg_loss_percent: number;
  largest_win: number;
  largest_loss: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  avg_trade_duration: number;
  expectancy: number;
  kelly_criterion: number;
}

export interface BacktestEquityCurve {
  date: string;
  equity: number;
  drawdown: number;
  drawdown_percent: number;
}

export interface BacktestResult {
  config: BacktestConfig;
  metrics: BacktestMetrics;
  trades: BacktestTrade[];
  equity_curve: BacktestEquityCurve[];
  completed_at: string;
}

export interface BacktestRunResponse {
  backtest_id: string;
  status: 'running' | 'completed' | 'failed';
  result?: BacktestResult;
  error?: string;
}

export interface BacktestListItem {
  backtest_id: string;
  strategy_name: string;
  ticker: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  total_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  total_trades?: number;
  status: 'running' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
}
