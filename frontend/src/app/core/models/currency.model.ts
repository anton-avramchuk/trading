/**
 * Модели валют
 */

export interface Currency {
  id: number;
  code: string;
  numeric_code?: string;
  name: string;
  name_en?: string;
  symbol?: string;
  decimal_places: number;
  is_active: number;
  created_at?: string;
}

export interface CurrencyCreate {
  code: string;
  numeric_code?: string;
  name: string;
  name_en?: string;
  symbol?: string;
  decimal_places?: number;
  is_active?: number;
}

export interface CurrencyUpdate {
  code?: string;
  numeric_code?: string;
  name?: string;
  name_en?: string;
  symbol?: string;
  decimal_places?: number;
  is_active?: number;
}
