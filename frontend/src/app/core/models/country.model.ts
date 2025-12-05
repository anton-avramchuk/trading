/**
 * Модели стран
 */

export interface Country {
  id: number;
  code: string;
  code3?: string;
  name: string;
  name_en?: string;
  region?: string;
  is_active: number;
  created_at?: string;
}

export interface CountryCreate {
  code: string;
  code3?: string;
  name: string;
  name_en?: string;
  region?: string;
  is_active?: number;
}

export interface CountryUpdate {
  code?: string;
  code3?: string;
  name?: string;
  name_en?: string;
  region?: string;
  is_active?: number;
}
