/**
 * useApplicants Hook
 * React Query hooks for applicant CRUD operations
 */
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { applicantService } from '@/services/applicants';
import {
  ApplicantFormData,
  ReviewSubmission,
  ApprovalData,
  RejectionData,
} from '@/types';

// Query keys
export const applicantKeys = {
  all: ['applicants'] as const,
  lists: () => [...applicantKeys.all, 'list'] as const,
  list: (filters: { page?: number; search?: string; status?: string; eligibilityStatus?: string | number }) =>
    [...applicantKeys.lists(), filters] as const,
  details: () => [...applicantKeys.all, 'detail'] as const,
  detail: (id: string) => [...applicantKeys.details(), id] as const,
  loanDetails: (id: string) => [...applicantKeys.all, 'loan-details', id] as const,
  creditHistory: (id: string) => [...applicantKeys.all, 'credit-history', id] as const,
  repaymentHistory: (id: string) => [...applicantKeys.all, 'repayment-history', id] as const,
  loanHistory: (id: string) => [...applicantKeys.all, 'loan-history', id] as const,
  auditTrail: (id: string) => [...applicantKeys.all, 'audit-trail', id] as const,
  pendingReviews: () => [...applicantKeys.all, 'pending-reviews'] as const,
};

// ==================== List Hooks ====================

/**
 * Get paginated applicants list
 */
export function useApplicants(
  page: number = 1,
  pageSize: number = 10,
  search?: string,
  status?: string,
  eligibilityStatus?: string | number
) {
  return useQuery({
    queryKey: applicantKeys.list({ page, search, status, eligibilityStatus }),
    queryFn: async () => {
      const response = await applicantService.getApplicants(page, pageSize, search, status, eligibilityStatus);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
  });
}

/**
 * Get pending reviews (manager only)
 */
export function usePendingReviews() {
  return useQuery({
    queryKey: applicantKeys.pendingReviews(),
    queryFn: async () => {
      const response = await applicantService.getPendingReviews();
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
  });
}

// ==================== Detail Hooks ====================

/**
 * Get single applicant by ID
 */
export function useApplicant(id: string) {
  return useQuery({
    queryKey: applicantKeys.detail(id),
    queryFn: async () => {
      const response = await applicantService.getApplicant(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

/**
 * Get full loan application details
 */
export function useLoanDetails(id: string) {
  return useQuery({
    queryKey: applicantKeys.loanDetails(id),
    queryFn: async () => {
      const response = await applicantService.getLoanDetails(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

/**
 * Get credit history for applicant
 */
export function useCreditHistory(id: string) {
  return useQuery({
    queryKey: applicantKeys.creditHistory(id),
    queryFn: async () => {
      const response = await applicantService.getCreditHistory(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

/**
 * Get repayment history for applicant
 */
export function useRepaymentHistory(id: string) {
  return useQuery({
    queryKey: applicantKeys.repaymentHistory(id),
    queryFn: async () => {
      const response = await applicantService.getRepaymentHistory(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

/**
 * Get loan history for applicant
 */
export function useLoanHistory(id: string) {
  return useQuery({
    queryKey: applicantKeys.loanHistory(id),
    queryFn: async () => {
      const response = await applicantService.getLoanHistory(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

/**
 * Get audit trail for applicant
 */
export function useAuditTrail(id: string) {
  return useQuery({
    queryKey: applicantKeys.auditTrail(id),
    queryFn: async () => {
      const response = await applicantService.getAuditTrail(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

// ==================== Mutation Hooks ====================

/**
 * Create a new applicant
 */
export function useCreateApplicant() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: ApplicantFormData) => {
      const response = await applicantService.createApplicant(data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
    },
  });
}

/**
 * Update an applicant
 */
export function useUpdateApplicant() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<ApplicantFormData> }) => {
      const response = await applicantService.updateApplicant(id, data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
      queryClient.invalidateQueries({ queryKey: applicantKeys.detail(variables.id) });
    },
  });
}

/**
 * Delete an applicant
 */
export function useDeleteApplicant() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await applicantService.deleteApplicant(id);
      if (!response.success) throw new Error(response.error);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
    },
  });
}

/**
 * Check eligibility for an applicant
 */
export function useCheckEligibility() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (applicantId: string) => {
      const response = await applicantService.checkEligibility(applicantId);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, applicantId) => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.detail(applicantId) });
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
    },
  });
}

/**
 * Send for manager review
 */
export function useSendForReview() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ applicantId, data }: { applicantId: string; data: ReviewSubmission }) => {
      const response = await applicantService.sendForReview(applicantId, data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.detail(variables.applicantId) });
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
      queryClient.invalidateQueries({ queryKey: applicantKeys.pendingReviews() });
    },
  });
}

/**
 * Approve an application (manager only)
 */
export function useApproveApplication() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ applicantId, data }: { applicantId: string; data: ApprovalData }) => {
      const response = await applicantService.approveApplication(applicantId, data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.detail(variables.applicantId) });
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
      queryClient.invalidateQueries({ queryKey: applicantKeys.pendingReviews() });
    },
  });
}

/**
 * Reject an application (manager only)
 */
export function useRejectApplication() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ applicantId, data }: { applicantId: string; data: RejectionData }) => {
      const response = await applicantService.rejectApplication(applicantId, data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.detail(variables.applicantId) });
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
      queryClient.invalidateQueries({ queryKey: applicantKeys.pendingReviews() });
    },
  });
}

// ==================== Combined Hook ====================

/**
 * Combined hook for all applicant operations
 */
export function useApplicantOperations(applicantId?: string) {
  const queryClient = useQueryClient();
  
  // Queries
  const applicantQuery = useApplicant(applicantId || '');
  const loanDetailsQuery = useLoanDetails(applicantId || '');
  const creditHistoryQuery = useCreditHistory(applicantId || '');
  const repaymentHistoryQuery = useRepaymentHistory(applicantId || '');
  
  // Mutations
  const createMutation = useCreateApplicant();
  const updateMutation = useUpdateApplicant();
  const deleteMutation = useDeleteApplicant();
  const eligibilityMutation = useCheckEligibility();
  const reviewMutation = useSendForReview();
  const approveMutation = useApproveApplication();
  const rejectMutation = useRejectApplication();
  
  return {
    // Queries
    applicant: applicantQuery.data,
    loanDetails: loanDetailsQuery.data,
    creditHistory: creditHistoryQuery.data,
    repaymentHistory: repaymentHistoryQuery.data,
    
    // Loading states
    isLoading: applicantQuery.isLoading || loanDetailsQuery.isLoading,
    isLoadingCreditHistory: creditHistoryQuery.isLoading,
    isLoadingRepaymentHistory: repaymentHistoryQuery.isLoading,
    
    // Errors
    error: applicantQuery.error || loanDetailsQuery.error,
    
    // Mutations
    createApplicant: createMutation.mutateAsync,
    updateApplicant: updateMutation.mutateAsync,
    deleteApplicant: deleteMutation.mutateAsync,
    checkEligibility: eligibilityMutation.mutateAsync,
    sendForReview: reviewMutation.mutateAsync,
    approveApplication: approveMutation.mutateAsync,
    rejectApplication: rejectMutation.mutateAsync,
    
    // Mutation states
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isCheckingEligibility: eligibilityMutation.isPending,
    isSendingForReview: reviewMutation.isPending,
    isApproving: approveMutation.isPending,
    isRejecting: rejectMutation.isPending,
    
    // Refetch
    refetch: () => {
      if (applicantId) {
        applicantQuery.refetch();
        loanDetailsQuery.refetch();
        creditHistoryQuery.refetch();
        repaymentHistoryQuery.refetch();
      }
    },
    
    // Invalidate cache
    invalidate: () => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.all });
    },
  };
}

export default useApplicantOperations;
