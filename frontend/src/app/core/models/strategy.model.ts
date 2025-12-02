/**
 * Модели торговых стратегий
 */

export interface StrategyParameter {
  name: string;
  type: string;
  default: any;
  min_value?: number;
  max_value?: number;
  description?: string;
}

export interface IndicatorConfig {
  name: string;
  timeframe: string;
  parameters: Record<string, any>;
  alias?: string;
}

export interface StrategyInfo {
  name: string;
  description: string;
  version: string;
  category: string;
  parameters: StrategyParameter[];
}

export interface StrategyDetails {
  name: string;
  description: string;
  version: string;
  required_timeframes: string[];
  indicators_config: IndicatorConfig[];
}

export interface StrategyListResponse {
  strategies: StrategyInfo[];
  count: number;
}

export interface StrategySummary {
  total_strategies: number;
  categories: Record<string, number>;
}
