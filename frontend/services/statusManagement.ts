/**
 * Status Management Service
 * Full CRUD operations for eligibility statuses, application statuses, and status colors
 */
import apiClient from './api';
import {
  ApiResponse,
} from '@/types';

// Helper to convert snake_case to camelCase
const toCamelCase = (obj: any): any => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(toCamelCase);
  
  return Object.keys(obj).reduce((acc, key) => {
    const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    acc[camelKey] = toCamelCase(obj[key]);
    return acc;
  }, {} as any);
};

// Helper to convert camelCase to snake_case
const toSnakeCase = (obj: any): any => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(toSnakeCase);
  
  return Object.keys(obj).reduce((acc, key) => {
    const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
    acc[snakeKey] = toSnakeCase(obj[key]);
    return acc;
  }, {} as any);
};

// Types
export interface EligibilityStatus {
  id: number;
  code: string;
  name: string;
  description?: string;
  isActive: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
}

export interface ApplicationStatus {
  id: number;
  code: string;
  name: string;
  description?: string;
  colorCode?: string;
  colorName?: string;
  isActive: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
}

export interface ApplicationStatusWithColor extends ApplicationStatus {
  // colorCode and colorName are now part of ApplicationStatus
}

export interface StatusColor {
  id: number;
  statusId: number;
  colorCode: string;
  colorName?: string;
  isPrimary: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface EligibilityStatusCreate {
  code: string;
  name: string;
  description?: string;
  isActive?: boolean;
  displayOrder?: number;
}

export interface EligibilityStatusUpdate {
  code?: string;
  name?: string;
  description?: string;
  isActive?: boolean;
  displayOrder?: number;
}

export interface ApplicationStatusCreate {
  code: string;
  name: string;
  description?: string;
  colorCode?: string;
  colorName?: string;
  isActive?: boolean;
  displayOrder?: number;
}

export interface ApplicationStatusUpdate {
  code?: string;
  name?: string;
  description?: string;
  colorCode?: string;
  colorName?: string;
  isActive?: boolean;
  displayOrder?: number;
}

export interface StatusColorCreate {
  statusId: number;
  colorCode: string;
  colorName?: string;
  isPrimary?: boolean;
}

export interface StatusColorUpdate {
  colorCode?: string;
  colorName?: string;
  isPrimary?: boolean;
}

export const statusManagementService = {
  // ==================== Eligibility Status Operations ====================
  
  /**
   * Get all eligibility statuses
   */
  getEligibilityStatuses: async (
    isActive?: boolean
  ): Promise<ApiResponse<EligibilityStatus[]>> => {
    try {
      const params = new URLSearchParams();
      if (isActive !== undefined) params.append('is_active', isActive.toString());
      
      const response = await apiClient.get(
        `/api/status-management/eligibility-statuses${params.toString() ? `?${params.toString()}` : ''}`
      );
      
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch eligibility statuses',
      };
    }
  },
  
  /**
   * Get eligibility status by ID
   */
  getEligibilityStatus: async (id: number): Promise<ApiResponse<EligibilityStatus>> => {
    try {
      const response = await apiClient.get(`/api/status-management/eligibility-statuses/${id}`);
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch eligibility status',
      };
    }
  },
  
  /**
   * Create eligibility status
   */
  createEligibilityStatus: async (
    data: EligibilityStatusCreate
  ): Promise<ApiResponse<EligibilityStatus>> => {
    try {
      const response = await apiClient.post(
        '/api/status-management/eligibility-statuses',
        toSnakeCase(data)
      );
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: 'Eligibility status created successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create eligibility status',
      };
    }
  },
  
  /**
   * Update eligibility status
   */
  updateEligibilityStatus: async (
    id: number,
    data: EligibilityStatusUpdate
  ): Promise<ApiResponse<EligibilityStatus>> => {
    try {
      const response = await apiClient.put(
        `/api/status-management/eligibility-statuses/${id}`,
        toSnakeCase(data)
      );
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: 'Eligibility status updated successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update eligibility status',
      };
    }
  },
  
  /**
   * Delete eligibility status
   */
  deleteEligibilityStatus: async (id: number): Promise<ApiResponse<void>> => {
    try {
      await apiClient.delete(`/api/status-management/eligibility-statuses/${id}`);
      return {
        success: true,
        message: 'Eligibility status deleted successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete eligibility status',
      };
    }
  },
  
  // ==================== Application Status Operations ====================
  
  /**
   * Get all application statuses
   */
  getApplicationStatuses: async (
    isActive?: boolean
  ): Promise<ApiResponse<ApplicationStatus[]>> => {
    try {
      const params = new URLSearchParams();
      if (isActive !== undefined) params.append('is_active', isActive.toString());
      
      const response = await apiClient.get(
        `/api/status-management/application-statuses${params.toString() ? `?${params.toString()}` : ''}`
      );
      
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch application statuses',
      };
    }
  },
  
  /**
   * Get application statuses with colors
   */
  getApplicationStatusesWithColors: async (
    isActive?: boolean
  ): Promise<ApiResponse<ApplicationStatusWithColor[]>> => {
    try {
      const params = new URLSearchParams();
      if (isActive !== undefined) params.append('is_active', isActive.toString());
      
      const response = await apiClient.get(
        `/api/status-management/application-statuses-with-colors${params.toString() ? `?${params.toString()}` : ''}`
      );
      
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch application statuses with colors',
      };
    }
  },
  
  /**
   * Get application status by ID
   */
  getApplicationStatus: async (id: number): Promise<ApiResponse<ApplicationStatus>> => {
    try {
      const response = await apiClient.get(`/api/status-management/application-statuses/${id}`);
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch application status',
      };
    }
  },
  
  /**
   * Create application status
   */
  createApplicationStatus: async (
    data: ApplicationStatusCreate
  ): Promise<ApiResponse<ApplicationStatus>> => {
    try {
      const response = await apiClient.post(
        '/api/status-management/application-statuses',
        toSnakeCase(data)
      );
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: 'Application status created successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create application status',
      };
    }
  },
  
  /**
   * Update application status
   */
  updateApplicationStatus: async (
    id: number,
    data: ApplicationStatusUpdate
  ): Promise<ApiResponse<ApplicationStatus>> => {
    try {
      const response = await apiClient.put(
        `/api/status-management/application-statuses/${id}`,
        toSnakeCase(data)
      );
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: 'Application status updated successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update application status',
      };
    }
  },
  
  /**
   * Delete application status
   */
  deleteApplicationStatus: async (id: number): Promise<ApiResponse<void>> => {
    try {
      await apiClient.delete(`/api/status-management/application-statuses/${id}`);
      return {
        success: true,
        message: 'Application status deleted successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete application status',
      };
    }
  },
  
  // ==================== Status Color Operations ====================
  
  /**
   * Get all status colors
   */
  getStatusColors: async (
    statusId?: number
  ): Promise<ApiResponse<StatusColor[]>> => {
    try {
      const params = new URLSearchParams();
      if (statusId !== undefined) params.append('status_id', statusId.toString());
      
      const response = await apiClient.get(
        `/api/status-management/status-colors${params.toString() ? `?${params.toString()}` : ''}`
      );
      
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch status colors',
      };
    }
  },
  
  /**
   * Get status color by ID
   */
  getStatusColor: async (id: number): Promise<ApiResponse<StatusColor>> => {
    try {
      const response = await apiClient.get(`/api/status-management/status-colors/${id}`);
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch status color',
      };
    }
  },
  
  /**
   * Create status color
   */
  createStatusColor: async (
    data: StatusColorCreate
  ): Promise<ApiResponse<StatusColor>> => {
    try {
      const response = await apiClient.post(
        '/api/status-management/status-colors',
        toSnakeCase(data)
      );
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: 'Status color created successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create status color',
      };
    }
  },
  
  /**
   * Update status color
   */
  updateStatusColor: async (
    id: number,
    data: StatusColorUpdate
  ): Promise<ApiResponse<StatusColor>> => {
    try {
      const response = await apiClient.put(
        `/api/status-management/status-colors/${id}`,
        toSnakeCase(data)
      );
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: 'Status color updated successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update status color',
      };
    }
  },
  
  /**
   * Delete status color
   */
  deleteStatusColor: async (id: number): Promise<ApiResponse<void>> => {
    try {
      await apiClient.delete(`/api/status-management/status-colors/${id}`);
      return {
        success: true,
        message: 'Status color deleted successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete status color',
      };
    }
  },
};

export default statusManagementService;

