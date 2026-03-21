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
  Transaction,
  TransactionSummary,
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
    status?: string,
    eligibilityStatus?: string | number
  ): Promise<ApiResponse<PaginatedResponse<Applicant>>> => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });
      
      if (search) params.append('search', search);
      if (status) params.append('status', status);
      if (eligibilityStatus !== undefined) params.append('eligibility_status', eligibilityStatus.toString());
      
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
      // Backend returns { success: true, data: {...} }, so we need to extract response.data.data
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
  
  /**
   * Create a new applicant
   */
  createApplicant: async (data: ApplicantFormData): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.post('/api/applicants', toSnakeCase(data));
      // Backend returns { success: true, data: {...} }, so we need to extract response.data.data
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: response.data?.message || 'Applicant created successfully',
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
      // Backend returns { success: true, data: {...} }, so we need to extract response.data.data
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: response.data?.message || 'Applicant updated successfully',
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

  /**
   * Add applicant to review queue with not_eligible status
   */
  addToQueue: async (id: string): Promise<ApiResponse<Applicant>> => {
    try {
      const response = await apiClient.put(`/api/applicants/${id}`, {
        eligibility_status: 'not_eligible',
        status: 'under_review',
      });
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
        message: 'Added to review queue successfully',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to add to queue',
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
      // Backend returns { success: true, data: {...} }, so we need to extract response.data.data
      const rawData = response.data?.data || response.data;
      return {
        success: true,
        data: toCamelCase(rawData),
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
      const rawData = toCamelCase(response.data?.data || response.data);
      
      // Transform API response to match frontend CreditProfile interface
      // Backend returns: { creditScore, creditUtilization, paymentHistoryScore, creditAgeYears, accounts, factors }
      // Frontend expects: { currentScore, scoreHistory, creditUtilization, totalCreditLines, ... }
      
      const transformedProfile: CreditProfile = {
        currentScore: rawData?.creditScore ?? 0,
        scoreHistory: rawData?.scoreHistory || [],
        creditUtilization: (rawData?.creditUtilization ?? 0) / 100, // Convert percentage to decimal
        totalCreditLines: rawData?.accounts?.length ?? 0,
        oldestAccount: rawData?.creditAgeYears ? `${rawData.creditAgeYears} years` : '',
        recentInquiries: rawData?.recentInquiries ?? 0,
        delinquencies: rawData?.derogatoryMarks ?? 0,
        publicRecords: 0, // Not provided by API
        averageAccountAge: rawData?.creditAgeYears ?? 0,
      };
      
      return {
        success: true,
        data: transformedProfile,
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
      const rawData = toCamelCase(response.data?.data || response.data);
      
      // Transform API response to match frontend expected structure
      // Backend returns: { summary: { totalLoans, activeLoans, ... }, loans: [...], recentPayments: [...] }
      // Frontend expects: { schedule: [...], summary: { totalLoanAmount, paymentsCompleted, ... } }
      
      const loans = rawData?.loans || [];
      const apiSummary = rawData?.summary || {};
      const recentPayments = rawData?.recentPayments || [];
      
      // Calculate derived values from loans data
      const totalLoanAmount = loans.reduce((sum: number, loan: any) => sum + (loan.originalAmount || 0), 0);
      const totalPaid = apiSummary.totalRepaid || 0;
      const totalRemaining = loans.reduce((sum: number, loan: any) => sum + (loan.remainingBalance || 0), 0);
      
      // Calculate payments completed and total from all loans
      const totalPaymentsCompleted = loans.reduce((sum: number, loan: any) => 
        sum + (loan.onTimePayments || 0) + (loan.latePayments || 0), 0);
      
      // Estimate total number of payments based on loan terms
      const activeLoan = loans.find((l: any) => l.status === 'active');
      const estimatedTotalPayments = totalPaymentsCompleted + (activeLoan ? 
        Math.ceil(activeLoan.remainingBalance / (activeLoan.monthlyPayment || 1)) : 0);
      
      // Build the summary in the format the frontend component expects
      const transformedSummary: RepaymentSummary = {
        totalLoanAmount: totalLoanAmount,
        totalPaid: totalPaid,
        totalRemaining: totalRemaining,
        totalInterest: 0, // Not available from API, default to 0
        nextPaymentDue: activeLoan?.nextDueDate || '',
        nextPaymentAmount: activeLoan?.monthlyPayment || 0,
        overdueAmount: 0, // Calculate if needed
        numberOfPayments: Math.max(estimatedTotalPayments, totalPaymentsCompleted) || 1,
        paymentsCompleted: totalPaymentsCompleted,
        paymentStatus: activeLoan ? 'current' : (loans.length > 0 ? 'completed' : 'pending'),
      };
      
      // Transform loans and recent payments into a schedule format
      let schedule: RepaymentSchedule[] = [];
      
      // If we have recent payments, transform them into schedule entries
      if (recentPayments && recentPayments.length > 0) {
        schedule = recentPayments.map((payment: any, index: number) => ({
          id: payment.id || `payment-${index}`,
          installmentNumber: index + 1,
          dueDate: payment.date || payment.dueDate || '',
          paidDate: payment.paidDate || payment.date || null,
          principalAmount: payment.principalAmount || payment.amount || 0,
          interestAmount: payment.interestAmount || 0,
          totalAmount: payment.amount || payment.totalAmount || 0,
          paidAmount: payment.status === 'paid' ? (payment.amount || 0) : 0,
          lateFee: payment.lateFee || 0,
          status: payment.status || 'pending',
          remainingBalance: payment.remainingBalance || 0,
        }));
      } else if (loans && loans.length > 0) {
        // If no recent payments, create schedule from loans
        schedule = loans.map((loan: any, index: number) => ({
          id: loan.id || `loan-${index}`,
          installmentNumber: index + 1,
          dueDate: loan.nextDueDate || loan.startDate || '',
          paidDate: loan.status === 'closed' || loan.status === 'paid off' ? loan.endDate : null,
          principalAmount: loan.originalAmount || 0,
          interestAmount: 0,
          totalAmount: loan.originalAmount || 0,
          paidAmount: (loan.originalAmount || 0) - (loan.remainingBalance || 0),
          lateFee: 0,
          status: loan.status === 'active' ? 'pending' : 'paid',
          remainingBalance: loan.remainingBalance || 0,
        }));
      }
      
      return {
        success: true,
        data: {
          schedule,
          summary: transformedSummary,
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch repayment history',
      };
    }
  },
  
  /**
   * Get transaction history for an applicant
   */
  getTransactionHistory: async (
    applicantId: string
  ): Promise<ApiResponse<{ transactions: Transaction[]; summary: TransactionSummary }>> => {
    try {
      const response = await apiClient.get(`/api/applicants/${applicantId}/transactions`);
      const rawData = toCamelCase(response.data?.data || response.data);
      
      return {
        success: true,
        data: {
          transactions: rawData?.transactions || [],
          summary: rawData?.summary || {
            totalTransactions: 0,
            totalDebits: 0,
            totalCredits: 0,
            monthlyTransactions: [],
          },
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch transaction history',
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
      const rawData = toCamelCase(response.data?.data || response.data);
      
      // Ensure we return an array
      const auditEntries = Array.isArray(rawData) ? rawData : [];
      
      return {
        success: true,
        data: auditEntries,
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
