/**
 * Модели индикаторов
 */

export interface IndicatorParameter {
  name: string;
  type: string;
  default: any;
  min_value?: number;
  max_value?: number;
  description?: string;
}

export interface IndicatorInfo {
  name: string;
  category: string;
  description: string;
  parameters: IndicatorParameter[];
}

export interface IndicatorListResponse {
  indicators: IndicatorInfo[];
  count: number;
  categories: string[];
}

export interface IndicatorCalculateRequest {
  indicator_name: string;
  ticker: string;
  timeframe: string;
  parameters?: Record<string, any>;
  start_date?: string;
  end_date?: string;
}

export interface IndicatorCalculateResponse {
  indicator_name: string;
  ticker: string;
  timeframe: string;
  result_type: 'continuous' | 'discrete' | 'shape';
  data?: Record<string, any>;
  points?: DiscretePoint[];
  shapes?: Shape[];
  metadata?: Record<string, any>;
}

export interface DiscretePoint {
  timestamp: string;
  price: number;
  label: string;
  direction?: 'UP' | 'DOWN';
  metadata?: Record<string, any>;
}

export interface Shape {
  shape_type: 'rectangle' | 'hline' | 'trendline' | 'zone';
  start_time: string;
  end_time: string;
  price_low: number;
  price_high: number;
  label?: string;
  color?: string;
  metadata?: Record<string, any>;
}

export interface IndicatorUsageStats {
  total_calculations: number;
  most_used: string[];
  by_category: Record<string, number>;
}
