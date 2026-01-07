import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { storage } from '@/lib/utils';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token if available
    const user = storage.get('user', null) as { token?: string } | null;
    if (user && config.headers) {
      config.headers.Authorization = `Bearer ${user.token || 'mock-token'}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      storage.remove('user');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    // Handle other errors
    const errorMessage = 
      (error.response?.data as any)?.message || 
      error.message || 
      'An unexpected error occurred';
    
    return Promise.reject(new Error(errorMessage));
  }
);

export default apiClient;
