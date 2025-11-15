/**
 * API Response Types
 */

export interface DamageItem {
  car_part: string;
  damage_type: string;
  severity: string;
  recommended_action: string;
  estimated_cost_usd: number;
  description: string;
}

export interface DamageReport {
  new_damage: DamageItem[];
  total_estimated_cost_usd: number;
  summary: string;
}

export interface SavedImages {
  before: string[];
  after: string[];
  bounded: string[];
}

export interface InspectionResponse {
  success: boolean;
  inspection_id: string;
  car_name: string;
  car_model: string;
  car_year: number;
  report: DamageReport;
  saved_images: SavedImages;
}

export interface InspectionListItem {
  id: string;
  car_name: string;
  car_model: string;
  car_year: number;
  total_damage_cost: number;
  created_at: string;
}

export interface InspectionListData {
  total: number;
  inspections: InspectionListItem[];
}

export interface InspectionListResponse {
  status: boolean;
  message: string;
  data: InspectionListData;
}

export interface InspectionDetail {
  id: string;
  car_name: string;
  car_model: string;
  car_year: number;
  damage_report: DamageReport;
  total_damage_cost: number;
  before_images: string[];
  after_images: string[];
  bounded_images: string[];
  created_at: string;
}

export interface InspectionDetailResponse {
  status: boolean;
  message: string;
  data: InspectionDetail;
}

export interface ApiError {
  status: boolean;
  message: string;
  data?: {
    error_type?: string;
    status_code?: number;
    [key: string]: any;
  };
}

