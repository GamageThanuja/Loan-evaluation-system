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
} from '@/types';
import { generateId, calculateAge } from '@/lib/utils';

// Mock data for development
const mockApplicants: Applicant[] = [
  {
    id: '1',
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@email.com',
    phone: '+1-555-0100',
    dateOfBirth: '1988-05-15',
    age: 35,
    gender: 'M',
    maritalStatus: 'Married',
    dependents: 2,
    annualIncome: 75000,
    employmentType: 'Employed',
    employmentLength: 8,
    creditScore: 720,
    loanAmount: 25000,
    loanPurpose: 'Home',
    loanTerm: 60,
    address: '123 Main St',
    city: 'New York',
    state: 'NY',
    zipCode: '10001',
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-15T10:30:00Z',
    status: 'approved',
  },
  {
    id: '2',
    firstName: 'Jane',
    lastName: 'Smith',
    email: 'jane.smith@email.com',
    phone: '+1-555-0200',
    dateOfBirth: '1992-08-22',
    age: 31,
    gender: 'F',
    maritalStatus: 'Single',
    dependents: 0,
    annualIncome: 55000,
    employmentType: 'Employed',
    employmentLength: 5,
    creditScore: 680,
    loanAmount: 15000,
    loanPurpose: 'Auto',
    loanTerm: 36,
    createdAt: '2024-01-16T14:20:00Z',
    updatedAt: '2024-01-16T14:20:00Z',
    status: 'pending',
  },
];

const mockPredictionResult: PredictionResult = {
  id: generateId(),
  applicantId: '1',
  riskScore: 0.23,
  decision: 'APPROVE',
  confidence: 0.89,
  timestamp: new Date().toISOString(),
  shapExplanation: {
    baseValue: 0.5,
    predictionValue: 0.23,
    topFeatures: [
      {
        feature: 'EXT_SOURCE_MEAN',
        value: 0.65,
        shapValue: -0.15,
        impact: 'negative',
        displayName: 'External Credit Score',
      },
      {
        feature: 'CREDIT_INCOME_RATIO',
        value: 0.33,
        shapValue: -0.08,
        impact: 'negative',
        displayName: 'Credit to Income Ratio',
      },
      {
        feature: 'AGE_YEARS',
        value: 35,
        shapValue: -0.05,
        impact: 'negative',
        displayName: 'Age',
      },
      {
        feature: 'DAYS_EMPLOYED',
        value: 2920,
        shapValue: -0.03,
        impact: 'negative',
        displayName: 'Employment Duration',
      },
      {
        feature: 'ANNUITY_INCOME_RATIO',
        value: 0.07,
        shapValue: 0.04,
        impact: 'positive',
        displayName: 'Annuity to Income Ratio',
      },
    ],
  },
  bayesianNetwork: {
    nodes: [
      { id: 'credit_score', name: 'credit_score', displayName: 'Credit Score', probability: 0.75, state: 'good' },
      { id: 'income', name: 'income', displayName: 'Income Level', probability: 0.68, state: 'adequate' },
      { id: 'employment', name: 'employment', displayName: 'Employment Status', probability: 0.82, state: 'stable' },
      { id: 'default_risk', name: 'default_risk', displayName: 'Default Risk', probability: 0.23, state: 'low' },
    ],
    edges: [
      { from: 'credit_score', to: 'default_risk', strength: 0.65, type: 'causal' },
      { from: 'income', to: 'default_risk', strength: 0.52, type: 'causal' },
      { from: 'employment', to: 'income', strength: 0.48, type: 'causal' },
    ],
    causalPaths: [
      {
        path: ['credit_score', 'default_risk'],
        probability: 0.75,
        impact: 0.65,
        description: 'Strong credit score indicates lower default risk',
      },
      {
        path: ['income', 'default_risk'],
        probability: 0.68,
        impact: 0.52,
        description: 'Adequate income reduces default probability',
      },
      {
        path: ['employment', 'income', 'default_risk'],
        probability: 0.82,
        impact: 0.35,
        description: 'Stable employment supports income stability',
      },
    ],
  },
  businessRules: [
    {
      id: 'rule1',
      rule: 'Credit score above 700',
      triggered: true,
      severity: 'info',
      recommendation: 'Excellent credit history - proceed with approval',
      actionRequired: false,
    },
    {
      id: 'rule2',
      rule: 'Debt-to-income ratio below 40%',
      triggered: true,
      severity: 'info',
      recommendation: 'Healthy debt-to-income ratio',
      actionRequired: false,
    },
    {
      id: 'rule3',
      rule: 'Employment length > 2 years',
      triggered: true,
      severity: 'info',
      recommendation: 'Stable employment history',
      actionRequired: false,
    },
  ],
  modelVersion: '2.1.0',
  threshold: {
    low: 0.15,
    medium: 0.30,
    high: 0.50,
  },
};

// API Service Methods
export const predictionService = {
  // Create prediction
  createPrediction: async (request: PredictionRequest): Promise<ApiResponse<PredictionResult>> => {
    try {
      // Mock implementation - replace with actual API call
      // const response = await apiClient.post('/api/predict', request);
      
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
      
      return {
        success: true,
        data: mockPredictionResult,
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
  getPrediction: async (id: string): Promise<ApiResponse<PredictionResult>> => {
    try {
      // const response = await apiClient.get(`/api/predictions/${id}`);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return {
        success: true,
        data: mockPredictionResult,
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
      // const response = await apiClient.get(`/api/predictions/recent?limit=${limit}`);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockRecent: RecentPrediction[] = [
        {
          id: '1',
          applicantName: 'John Doe',
          riskScore: 0.23,
          decision: 'APPROVE',
          timestamp: new Date().toISOString(),
          status: 'approved',
        },
        {
          id: '2',
          applicantName: 'Jane Smith',
          riskScore: 0.42,
          decision: 'MANUAL_REVIEW',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          status: 'pending',
        },
        {
          id: '3',
          applicantName: 'Bob Johnson',
          riskScore: 0.68,
          decision: 'REJECT',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          status: 'rejected',
        },
      ];
      
      return {
        success: true,
        data: mockRecent,
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
      // const response = await apiClient.get(`/api/applicants?page=${page}&pageSize=${pageSize}&search=${search}`);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      let filtered = [...mockApplicants];
      
      if (search) {
        filtered = filtered.filter(
          a => 
            a.firstName.toLowerCase().includes(search.toLowerCase()) ||
            a.lastName.toLowerCase().includes(search.toLowerCase()) ||
            a.email.toLowerCase().includes(search.toLowerCase())
        );
      }
      
      return {
        success: true,
        data: {
          items: filtered,
          total: filtered.length,
          page,
          pageSize,
          totalPages: Math.ceil(filtered.length / pageSize),
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
  getApplicant: async (id: string): Promise<ApiResponse<Applicant>> => {
    try {
      // const response = await apiClient.get(`/api/applicants/${id}`);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const applicant = mockApplicants.find(a => a.id === id) || mockApplicants[0];
      
      return {
        success: true,
        data: applicant,
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
      // const response = await apiClient.post('/api/applicants', data);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newApplicant: Applicant = {
        id: generateId(),
        ...data,
        age: calculateAge(data.dateOfBirth),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        status: 'pending',
      };
      
      mockApplicants.push(newApplicant);
      
      return {
        success: true,
        data: newApplicant,
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
  approveLoan: async (applicantId: string, notes?: string): Promise<ApiResponse<void>> => {
    try {
      // const response = await apiClient.post(`/api/applicants/${applicantId}/approve`, { notes });
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
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
  rejectLoan: async (applicantId: string, reason: string): Promise<ApiResponse<void>> => {
    try {
      // const response = await apiClient.post(`/api/applicants/${applicantId}/reject`, { reason });
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
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
      // const response = await apiClient.get('/api/model/stats');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockStats: DashboardStats = {
        totalPredictions: 1247,
        approvalRate: 0.6832,
        rejectionRate: 0.2145,
        avgRiskScore: 0.3421,
        pendingReviews: 23,
        modelAccuracy: 0.9197,
        modelAUC: 0.7545,
      };
      
      return {
        success: true,
        data: mockStats,
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
      // const response = await apiClient.get('/api/model/health');
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const mockHealth: ModelHealth = {
        status: 'healthy',
        lastUpdated: new Date().toISOString(),
        version: '2.1.0',
        avgResponseTime: 245,
        successRate: 0.9987,
        errorRate: 0.0013,
      };
      
      return {
        success: true,
        data: mockHealth,
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
      // const response = await apiClient.get('/api/reports/performance');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockPerformance: ModelPerformance[] = [
        { date: '2024-01', accuracy: 0.915, precision: 0.882, recall: 0.856, f1Score: 0.869, auc: 0.748 },
        { date: '2024-02', accuracy: 0.918, precision: 0.888, recall: 0.862, f1Score: 0.875, auc: 0.752 },
        { date: '2024-03', accuracy: 0.920, precision: 0.891, recall: 0.865, f1Score: 0.878, auc: 0.755 },
      ];
      
      return {
        success: true,
        data: mockPerformance,
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
      // const response = await apiClient.get('/api/reports/batches');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockBatches: BatchPrediction[] = [
        {
          id: '1',
          fileName: 'january_applications.csv',
          totalRecords: 150,
          processed: 150,
          approved: 102,
          rejected: 32,
          status: 'completed',
          createdAt: '2024-01-15T10:00:00Z',
          completedAt: '2024-01-15T10:05:30Z',
        },
        {
          id: '2',
          fileName: 'february_applications.csv',
          totalRecords: 180,
          processed: 180,
          approved: 125,
          rejected: 38,
          status: 'completed',
          createdAt: '2024-02-10T14:00:00Z',
          completedAt: '2024-02-10T14:06:15Z',
        },
      ];
      
      return {
        success: true,
        data: mockBatches,
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
      // const response = await apiClient.get(`/api/reports/export/${format}`, { responseType: 'blob' });
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockBlob = new Blob(['Mock export data'], { type: format === 'csv' ? 'text/csv' : 'application/pdf' });
      
      return {
        success: true,
        data: mockBlob,
        message: `Data exported as ${format.toUpperCase()}`,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to export data',
      };
    }
  },
};

export default predictionService;
