/**
 * API Service
 * Handles all API calls to the backend
 */
import axios, { AxiosError } from 'axios';
import { API_CONFIG } from '@/config/api';
import type {
  InspectionResponse,
  InspectionListResponse,
  InspectionDetailResponse,
  ApiError,
} from '@/types/api';

const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: 30000, // 30 seconds for image uploads
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Request interceptor (for logging/debugging)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor (for error handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    console.error('[API] Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Submit inspection with images
 */
export const submitInspection = async (
  carName: string,
  carModel: string,
  carYear: number,
  beforeImages: string[],
  afterImages: string[]
): Promise<InspectionResponse> => {
  const formData = new FormData();
  
  formData.append('car_name', carName);
  formData.append('car_model', carModel);
  formData.append('car_year', carYear.toString());
  
  // Append before images
  beforeImages.forEach((uri, index) => {
    const filename = uri.split('/').pop() || `before_${index}.jpg`;
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';
    
    formData.append('before', {
      uri,
      name: filename,
      type,
    } as any);
  });
  
  // Append after images
  afterImages.forEach((uri, index) => {
    const filename = uri.split('/').pop() || `after_${index}.jpg`;
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';
    
    formData.append('after', {
      uri,
      name: filename,
      type,
    } as any);
  });
  
  const response = await apiClient.post<InspectionResponse>(
    API_CONFIG.ENDPOINTS.INSPECT,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  
  return response.data;
};

/**
 * Get list of inspections
 */
export const getInspections = async (
  skip: number = 0,
  limit: number = 100
): Promise<InspectionListResponse> => {
  const response = await apiClient.get<InspectionListResponse>(
    API_CONFIG.ENDPOINTS.INSPECTIONS,
    {
      params: { skip, limit },
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );
  
  return response.data;
};

/**
 * Get inspection details by ID
 */
export const getInspectionDetails = async (
  inspectionId: string
): Promise<InspectionDetailResponse> => {
  const response = await apiClient.get<InspectionDetailResponse>(
    API_CONFIG.ENDPOINTS.INSPECTION_DETAIL(inspectionId),
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );
  
  return response.data;
};

/**
 * Health check
 */
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.HEALTH);
    return response.status === 200;
  } catch {
    return false;
  }
};

