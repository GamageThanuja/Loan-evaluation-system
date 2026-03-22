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
      
      // Transform items from snake_case to camelCase
      const transformedItems = (data.items || data || []).map((item: any) => toCamelCase(item));
      
      return {
        success: true,
        data: {
          items: transformedItems,
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
      // Transform snake_case from API to camelCase for frontend
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
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
  checkEligibility: async (applicantId: number, loanAmount: number, loanTermMonths: number, monthlyIncome?: number): Promise<ApiResponse<EligibilityResult>> => {
    try {
      const response = await apiClient.post('/api/predictions/eligibility', {
        applicant_id: applicantId,
        loan_amount: loanAmount,
        loan_term_months: loanTermMonths,
        monthly_income: monthlyIncome
      });
      
      // Get the nested data from API response
      const apiData = response.data?.data || response.data;
      
      // Transform nested API response to flat EligibilityResult structure
      const transformedData: EligibilityResult = {
        applicant_id: apiData.applicant_id,
        eligible: apiData.decision?.eligible ?? false,
        risk_score: (apiData.decision?.probability_percentage ?? 0) / 100, // Convert percentage to decimal
        probability: (apiData.decision?.probability_percentage ?? 0) / 100,
        decision: apiData.decision?.status || 'REJECT',
        risk_level: apiData.decision?.risk_level || 'Unknown',
        
        // Fix: Map correct fields from API 'reasoning' object
        summary_explanation: apiData.reasoning?.summary || '',
        
        feature_importance: apiData.feature_importance || [],
        risk_analysis: apiData.reasoning, // Store full reasoning object
        
        // Map risk factors
        risk_factors: (apiData.reasoning?.risk_factors || []).map((c: any) => ({
          feature: c.factor_name || '',
          description: c.impact_description || '',
          explanation: c.impact_description || '',
          impact: c.severity || 'major',
          is_positive: false,
          value: c.current_value,
          expected: c.expected_value
        })),
        
        // Map protective factors
        protective_factors: (apiData.reasoning?.protective_factors || []).map((p: any) => ({
          feature: p.factor_name || '',
          description: p.impact_description || '',
          explanation: p.impact_description || '',
          impact: p.severity || 'positive',
          is_positive: true,
          value: p.current_value
        })),
        
        // Map suggestions to recommendations
        recommendations: (apiData.reasoning?.suggestions || []).map((s: any) => s.action || s),
        
        confidence_score: 0.95, // Hardcode high confidence as model is deterministic/hybrid
        model_type: 'Hybrid ANN + BN',
        
        // Include raw loan/financial data for "Try Different Parameters" feature
        loan_details: apiData.financials ? {
            amount: apiData.financials.loan_amount,
            term_months: apiData.financials.term_months,
            interest_rate: 12.0 // Default
        } : undefined,
        
        financial_profile: apiData.financials ? {
            monthly_income: apiData.financials.monthly_income,
            expenses: 0,
            assets: 0
        } : undefined,
        
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
