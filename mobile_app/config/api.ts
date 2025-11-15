/**
 * API Configuration
 * 
 * Change the base URL here to update it across the entire app
 * 
 * Platform-specific URLs:
 * - iOS Simulator: 'http://localhost:8000' ✅ Works
 * - iOS Physical Device: Use your computer's IP address (e.g., 'http://192.168.1.100:8000')
 * - Android Emulator: 'http://10.0.2.2:8000' (special IP to access host machine)
 * - Android Physical Device: Use your computer's IP address (e.g., 'http://192.168.1.100:8000')
 * - Web: 'http://localhost:8000' ✅ Works
 * 
 * To find your computer's IP address:
 * - Mac/Linux: Run `ifconfig` or `ipconfig getifaddr en0` in terminal
 * - Windows: Run `ipconfig` in CMD and look for IPv4 Address
 * 
 * For physical device testing, replace 'localhost' below with your IP address
 */
import { Platform } from 'react-native';

// Set this to your computer's IP address when testing on physical devices
// Leave as 'localhost' for simulator/emulator testing
const DEV_HOST = 'localhost'; // Change to '192.168.1.100' (your IP) for physical devices

const getBaseUrl = (): string => {
  if (!__DEV__) {
    return 'https://your-production-api.com'; // Production URL
  }
  
  // Development URLs based on platform
  if (Platform.OS === 'android') {
    // Android emulator uses 10.0.2.2 to access host machine's localhost
    return `http://192.168.1.167:8000`;
  }else if (Platform.OS === 'ios') {
    return `http://192.168.1.167:8000`;
  }
  
  // iOS simulator and web can use localhost
  // For physical iOS device, change DEV_HOST to your computer's IP
  return `http://${DEV_HOST}:8000`;
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

