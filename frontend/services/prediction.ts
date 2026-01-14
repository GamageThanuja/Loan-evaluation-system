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
  EligibilityResult,
  PredictionWithReasoning,
  BayesianNetworkStructure,
  ScenarioComparison,
  ModelInfo,
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

  // ============================================
  // ELIGIBILITY & PREDICTION ENDPOINTS
  // ============================================

  // Check eligibility with ML model reasoning
  checkEligibility: async (applicantId: number, loanAmount: number, loanTermMonths: number): Promise<ApiResponse<EligibilityResult>> => {
    try {
      const response = await apiClient.post('/api/predictions/eligibility', {
        applicant_id: applicantId,
        loan_amount: loanAmount,
        loan_term_months: loanTermMonths
      });
      
      // Get the nested data from API response
      const apiData = response.data?.data || response.data;
      
      // Transform nested API response to flat EligibilityResult structure
      const transformedData: EligibilityResult = {
        applicant_id: apiData.applicant_id,
        eligible: apiData.decision?.eligible ?? false,
        risk_score: (apiData.decision?.risk_score_percentage ?? 0) / 100, // Convert percentage to decimal
        probability: (apiData.decision?.risk_score_percentage ?? 0) / 100,
        decision: apiData.decision?.status || 'REJECT',
        risk_level: apiData.decision?.risk_level || 'Unknown',
        summary_explanation: apiData.explanation?.summary || '',
        risk_factors: (apiData.risk_analysis?.concerns || []).map((c: { factor?: string; explanation?: string; severity?: string }) => ({
          feature: c.factor || '',
          description: c.explanation || '',
          explanation: c.explanation || '',
          impact: c.severity || 'Medium',
          is_positive: false
        })),
        protective_factors: (apiData.risk_analysis?.positive_factors || []).map((p: { factor?: string; explanation?: string; severity?: string }) => ({
          feature: p.factor || '',
          description: p.explanation || '',
          explanation: p.explanation || '',
          impact: p.severity || 'Medium',
          is_positive: true
        })),
        recommendations: apiData.recommendations || [],
        confidence_score: (apiData.model_info?.confidence_score ?? 0) / 100, // Convert percentage to decimal
        model_type: apiData.model_info?.model_type,
        // Include raw loan/financial data for "Try Different Parameters" feature
        loan_details: apiData.loan_details,
        financial_profile: apiData.financial_profile,
        raw_decision: apiData.decision,
        raw_model_info: apiData.model_info
      };
      
      return {
        success: true,
        data: transformedData,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to check eligibility',
      };
    }
  },

  // Get prediction with full Bayesian reasoning
  getPredictionWithReasoning: async (features: Record<string, number>): Promise<ApiResponse<PredictionWithReasoning>> => {
    try {
      const response = await apiClient.post('/api/predictions/predict/explain', { features });
      return {
        success: true,
        data: response.data?.reasoning || response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get prediction with reasoning',
      };
    }
  },

  // Send application for manager review
  sendForReview: async (applicantId: number, eligibilityResult: EligibilityResult, notes?: string): Promise<ApiResponse<void>> => {
    try {
      await apiClient.post(`/api/applicants/${applicantId}/send-for-review`, {
        applicant_id: applicantId,
        eligibility_result: eligibilityResult,
        notes
      });
      return {
        success: true,
        message: 'Application sent for review successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to send for review',
      };
    }
  },

  // Get Bayesian Network structure for visualization
  getBayesianNetworkStructure: async (): Promise<ApiResponse<BayesianNetworkStructure>> => {
    try {
      const response = await apiClient.get('/api/predictions/explain/network');
      return {
        success: true,
        data: response.data?.network || response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get network structure',
      };
    }
  },

  // Compare two loan scenarios
  compareScenarios: async (scenarioA: Record<string, number>, scenarioB: Record<string, number>): Promise<ApiResponse<ScenarioComparison>> => {
    try {
      const response = await apiClient.post('/api/predictions/compare', {
        scenario_a: scenarioA,
        scenario_b: scenarioB
      });
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to compare scenarios',
      };
    }
  },

  // Get model information
  getModelInfo: async (): Promise<ApiResponse<ModelInfo>> => {
    try {
      const response = await apiClient.get('/api/predictions/model/info');
      return {
        success: true,
        data: response.data?.data || response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get model info',
      };
    }
  },
};

export default predictionService;
