/* eslint-disable @typescript-eslint/no-unused-vars */
import apiClient from './api';
import {
  PredictionRequest,
  PredictionResult,
  Applicant,
  ApplicantFormData,
  DashboardStats,
  ModelHealth,
  RecentPrediction,
  ModelPerformance,
  BatchPrediction,
  ApiResponse,
  PaginatedResponse,
  LoanApplicationDetails,
} from '@/types';

// API Service Methods
export const predictionService = {
  // Create prediction
  createPrediction: async (request: PredictionRequest): Promise<ApiResponse<PredictionResult>> => {
    try {
      const response = await apiClient.post('/api/predict', request);
      return {
        success: true,
        data: response.data,
        message: 'Prediction created successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create prediction',
      };
    }
  },

  // Get prediction by ID
  getPrediction: async (id: string | number): Promise<ApiResponse<PredictionResult>> => {
    try {
      const response = await apiClient.get(`/api/predictions/${id}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch prediction',
      };
    }
  },

  // Get recent predictions
  getRecentPredictions: async (limit: number = 5): Promise<ApiResponse<RecentPrediction[]>> => {
    try {
      const response = await apiClient.get(`/api/predictions/recent?limit=${limit}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch recent predictions',
      };
    }
  },

  // Get applicants
  getApplicants: async (
    page: number = 1,
    pageSize: number = 10,
    search?: string
  ): Promise<ApiResponse<PaginatedResponse<Applicant>>> => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });
      
      if (search) params.append('search', search);
      
      const response = await apiClient.get(`/api/applicants?${params.toString()}`);
      const data = response.data?.data || response.data;
      
      return {
        success: true,
        data: {
          items: data.items || data || [],
          total: data.total || 0,
          page,
          pageSize,
          totalPages: Math.ceil((data.total || 0) / pageSize),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch applicants',
      };
    }
  },

  // Get applicant by ID
  getApplicant: async (id: string | number): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.get(`/api/applicants/${id}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch applicant',
      };
    }
  },

  // Create applicant
  createApplicant: async (data: ApplicantFormData): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.post('/api/applicants', data);
      return {
        success: true,
        data: response.data,
        message: 'Applicant created successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create applicant',
      };
    }
  },

  // Approve loan
  approveLoan: async (applicantId: string | number, notes?: string): Promise<ApiResponse<void>> => {
    try {
      await apiClient.post(`/api/applicants/${applicantId}/approve`, { notes });
      return {
        success: true,
        message: 'Loan approved successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to approve loan',
      };
    }
  },

  // Reject loan
  rejectLoan: async (applicantId: string | number, reason: string): Promise<ApiResponse<void>> => {
    try {
      await apiClient.post(`/api/applicants/${applicantId}/reject`, { reason });
      return {
        success: true,
        message: 'Loan rejected successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to reject loan',
      };
    }
  },

  // Get model stats
  getModelStats: async (): Promise<ApiResponse<DashboardStats>> => {
    try {
      const response = await apiClient.get('/api/model/stats');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch model stats',
      };
    }
  },

  // Get model health
  getModelHealth: async (): Promise<ApiResponse<ModelHealth>> => {
    try {
      const response = await apiClient.get('/api/model/health');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch model health',
      };
    }
  },

  // Get model performance
  getModelPerformance: async (): Promise<ApiResponse<ModelPerformance[]>> => {
    try {
      const response = await apiClient.get('/api/reports/performance');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch performance data',
      };
    }
  },

  // Get batch predictions
  getBatchPredictions: async (): Promise<ApiResponse<BatchPrediction[]>> => {
    try {
      const response = await apiClient.get('/api/reports/batches');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch batch predictions',
      };
    }
  },

  // Export data
  exportData: async (format: 'csv' | 'pdf'): Promise<ApiResponse<Blob>> => {
    try {
      const response = await apiClient.get(`/api/reports/export/${format}`, { 
        responseType: 'blob' 
      });
      return {
        success: true,
        data: response.data,
        message: `Data exported as ${format.toUpperCase()}`,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to export data',
      };
    }
  },

  // Get loan application details
  getLoanApplicationDetails: async (applicantId: string | number): Promise<ApiResponse<LoanApplicationDetails>> => {
    try {
      const response = await apiClient.get(`/api/loan-details/${applicantId}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch loan application details',
      };
    }
  },
};

export default predictionService;
