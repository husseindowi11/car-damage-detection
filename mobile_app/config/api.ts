/**
 * API Configuration
 * 
 * Change the base URL here to update it across the entire app
 * 
 * Platform-specific URLs:
 * - iOS Simulator: 'http://localhost:8000'
 * - Android Emulator: 'http://10.0.2.2:8000' (special IP to access host machine)
 * - Physical Device: Use your computer's IP address
 *   Example: 'http://192.168.1.100:8000'
 */
import { Platform } from 'react-native';

const getBaseUrl = (): string => {
  if (!__DEV__) {
    return 'https://your-production-api.com'; // Production URL
  }
  
  // Development URLs based on platform
  if (Platform.OS === 'android') {
    // Android emulator uses 10.0.2.2 to access host machine's localhost
    return 'http://10.0.2.2:8000';
  }
  
  // iOS simulator and web can use localhost
  return 'http://localhost:8000';
};

export const API_CONFIG = {
  BASE_URL: getBaseUrl(),
  
  ENDPOINTS: {
    INSPECT: '/api/inspect',
    INSPECTIONS: '/api/inspections',
    INSPECTION_DETAIL: (id: string) => `/api/inspections/${id}`,
    HEALTH: '/api/health',
  },
};

// Helper to get full URL
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Helper to get image URL (for displaying images from backend)
export const getImageUrl = (imagePath: string): string => {
  // Image paths from backend are relative to uploads directory (e.g., "2025-11-15/inspection_id/before_1.jpg")
  // We need to construct: http://base_url/uploads/path
  const cleanPath = imagePath.startsWith('/') ? imagePath.slice(1) : imagePath;
  // Ensure path doesn't already include 'uploads/'
  const finalPath = cleanPath.startsWith('uploads/') ? cleanPath : `uploads/${cleanPath}`;
  return `${API_CONFIG.BASE_URL}/${finalPath}`;
};

