/**
 * Applicant Service
 * Full CRUD operations for applicant management
 */
import apiClient from './api';
import {
  Applicant,
  ApplicantFormData,
  ApiResponse,
  PaginatedResponse,
  EligibilityCheckResult,
  ReviewSubmission,
  ApprovalData,
  RejectionData,
  LoanApplicationDetails,
  CreditProfile,
  RepaymentSchedule,
  RepaymentSummary,
  AuditLogEntry,
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

export const applicantService = {
  // ==================== CRUD Operations ====================
  
  /**
   * Get paginated list of applicants
   */
  getApplicants: async (
    page: number = 1,
    pageSize: number = 10,
    search?: string,
    status?: string
  ): Promise<ApiResponse<PaginatedResponse<Applicant>>> => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });
      
      if (search) params.append('search', search);
      if (status) params.append('status', status);
      
      const response = await apiClient.get(`/api/applicants?${params.toString()}`);
      
      // Handle both response formats: { data: { items: [...] } } or { items: [...] }
      const responseData = response.data?.data || response.data;
      const items = responseData?.items || responseData || [];
      const total = responseData?.total || items.length;
      
      return {
        success: true,
        data: {
          items: toCamelCase(items),
          total,
          page,
          pageSize,
          totalPages: Math.ceil(total / pageSize),
        },
      };
    } catch (error) {
      console.error('Error fetching applicants:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch applicants',
      };
    }
  },
  
  /**
   * Get applicant by ID with full details
   */
  getApplicant: async (id: string): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.get(`/api/applicants/${id}`);
      return {
        success: true,
        data: toCamelCase(response.data),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch applicant',
      };
    }
  },
  
  /**
   * Create a new applicant
   */
  createApplicant: async (data: ApplicantFormData): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.post('/api/applicants', toSnakeCase(data));
      return {
        success: true,
        data: toCamelCase(response.data),
        message: 'Applicant created successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create applicant',
      };
    }
  },
  
  /**
   * Update an existing applicant
   */
  updateApplicant: async (
    id: string,
    data: Partial<ApplicantFormData>
  ): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.put(`/api/applicants/${id}`, toSnakeCase(data));
      return {
        success: true,
        data: toCamelCase(response.data),
        message: 'Applicant updated successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update applicant',
      };
    }
  },
  
  /**
   * Delete an applicant (soft delete - manager only)
   */
  deleteApplicant: async (id: string): Promise<ApiResponse<void>> => {
    try {
      await apiClient.delete(`/api/applicants/${id}`);
      return {
        success: true,
        message: 'Applicant deleted successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete applicant',
      };
    }
  },
  
  // ==================== Eligibility Operations ====================
  
  /**
   * Check eligibility for an applicant
   */
  checkEligibility: async (applicantId: string): Promise<ApiResponse<EligibilityCheckResult>> => {
    try {
      const response = await apiClient.post(`/api/applicants/${applicantId}/check-eligibility`);
      return {
        success: true,
        data: toCamelCase(response.data),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to check eligibility',
      };
    }
  },
  
  // ==================== Review Workflow ====================
  
  /**
   * Send applicant for manager review (loan officer)
   */
  sendForReview: async (
    applicantId: string,
    data: ReviewSubmission
  ): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.post(
        `/api/applicants/${applicantId}/send-for-review`,
        toSnakeCase(data)
      );
      return {
        success: true,
        data: toCamelCase(response.data),
        message: 'Sent for review successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to send for review',
      };
    }
  },
  
  /**
   * Get applications pending review (manager)
   */
  getPendingReviews: async (): Promise<ApiResponse<Applicant[]>> => {
    try {
      const response = await apiClient.get('/api/applicants/review/pending');
      return {
        success: true,
        data: toCamelCase(response.data),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch pending reviews',
      };
    }
  },
  
  /**
   * Approve an application (manager)
   */
  approveApplication: async (
    applicantId: string,
    data: ApprovalData
  ): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.post(
        `/api/applicants/${applicantId}/approve`,
        toSnakeCase(data)
      );
      return {
        success: true,
        data: toCamelCase(response.data),
        message: 'Application approved successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to approve application',
      };
    }
  },
  
  /**
   * Reject an application (manager)
   */
  rejectApplication: async (
    applicantId: string,
    data: RejectionData
  ): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.post(
        `/api/applicants/${applicantId}/reject`,
        toSnakeCase(data)
      );
      return {
        success: true,
        data: toCamelCase(response.data),
        message: 'Application rejected',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to reject application',
      };
    }
  },
  
  // ==================== History & Details ====================
  
  /**
   * Get full loan application details
   */
  getLoanDetails: async (applicantId: string): Promise<ApiResponse<LoanApplicationDetails>> => {
    try {
      const response = await apiClient.get(`/api/loan-details/${applicantId}`);
      return {
        success: true,
        data: toCamelCase(response.data),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch loan details',
      };
    }
  },
  
  /**
   * Get credit history for an applicant
   */
  getCreditHistory: async (applicantId: string): Promise<ApiResponse<CreditProfile>> => {
    try {
      const response = await apiClient.get(`/api/applicants/${applicantId}/credit-history`);
      return {
        success: true,
        data: toCamelCase(response.data),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch credit history',
      };
    }
  },
  
  /**
   * Get repayment history for an applicant
   */
  getRepaymentHistory: async (
    applicantId: string
  ): Promise<ApiResponse<{ schedule: RepaymentSchedule[]; summary: RepaymentSummary }>> => {
    try {
      const response = await apiClient.get(`/api/applicants/${applicantId}/repayment-history`);
      return {
        success: true,
        data: toCamelCase(response.data),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch repayment history',
      };
    }
  },
  
  /**
   * Get loan history for an applicant
   */
  getLoanHistory: async (applicantId: string): Promise<ApiResponse<any[]>> => {
    try {
      const response = await apiClient.get(`/api/applicants/${applicantId}/loan-history`);
      return {
        success: true,
        data: toCamelCase(response.data),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch loan history',
      };
    }
  },
  
  /**
   * Get audit trail for an applicant
   */
  getAuditTrail: async (applicantId: string): Promise<ApiResponse<AuditLogEntry[]>> => {
    try {
      const response = await apiClient.get(`/api/applicants/${applicantId}/audit-trail`);
      return {
        success: true,
        data: toCamelCase(response.data),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch audit trail',
      };
    }
  },
};

export default applicantService;
