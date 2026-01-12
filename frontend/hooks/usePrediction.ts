'use client';

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import predictionService from '@/services/prediction';
import {
  PredictionRequest,
  PredictionResult,
  Applicant,
  ApplicantFormData,
  RecentPrediction,
  PaginatedResponse,
} from '@/types';

// Query keys
export const QUERY_KEYS = {
  predictions: 'predictions',
  recentPredictions: 'recentPredictions',
  applicants: 'applicants',
  applicant: 'applicant',
  modelStats: 'modelStats',
  modelHealth: 'modelHealth',
  modelPerformance: 'modelPerformance',
  batchPredictions: 'batchPredictions',
};

// Hooks for predictions
export function usePrediction(id: string | number): UseQueryResult<PredictionResult, Error> {
  return useQuery({
    queryKey: [QUERY_KEYS.predictions, id],
    queryFn: async () => {
      const response = await predictionService.getPrediction(id);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch prediction');
      }
      return response.data;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreatePrediction(): UseMutationResult<
  PredictionResult,
  Error,
  PredictionRequest,
  unknown
> {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (request: PredictionRequest) => {
      const response = await predictionService.createPrediction(request);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to create prediction');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.recentPredictions] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.modelStats] });
    },
  });
}

export function useRecentPredictions(limit: number = 5): UseQueryResult<RecentPrediction[], Error> {
  return useQuery({
    queryKey: [QUERY_KEYS.recentPredictions, limit],
    queryFn: async () => {
      const response = await predictionService.getRecentPredictions(limit);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch recent predictions');
      }
      return response.data;
    },
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Auto-refetch every 30 seconds
  });
}

// Hooks for applicants
export function useApplicants(
  page: number = 1,
  pageSize: number = 10,
  search?: string
): UseQueryResult<PaginatedResponse<Applicant>, Error> {
  return useQuery({
    queryKey: [QUERY_KEYS.applicants, page, pageSize, search],
    queryFn: async () => {
      const response = await predictionService.getApplicants(page, pageSize, search);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch applicants');
      }
      return response.data;
    },
    staleTime: 60 * 1000, // 1 minute
  });
}

export function useApplicant(id: string | number): UseQueryResult<Applicant, Error> {
  return useQuery({
    queryKey: [QUERY_KEYS.applicant, id],
    queryFn: async () => {
      const response = await predictionService.getApplicant(id);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch applicant');
      }
      return response.data;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateApplicant(): UseMutationResult<
  Applicant,
  Error,
  ApplicantFormData,
  unknown
> {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: ApplicantFormData) => {
      const response = await predictionService.createApplicant(data);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to create applicant');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.applicants] });
    },
  });
}

// Hooks for loan actions
export function useApproveLoan(): UseMutationResult<
  void,
  Error,
  { applicantId: string | number; notes?: string },
  unknown
> {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ applicantId, notes }) => {
      const response = await predictionService.approveLoan(applicantId, notes);
      if (!response.success) {
        throw new Error(response.error || 'Failed to approve loan');
      }
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.applicant, variables.applicantId] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.applicants] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.modelStats] });
    },
  });
}

export function useRejectLoan(): UseMutationResult<
  void,
  Error,
  { applicantId: string | number; reason: string },
  unknown
> {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ applicantId, reason }) => {
      const response = await predictionService.rejectLoan(applicantId, reason);
      if (!response.success) {
        throw new Error(response.error || 'Failed to reject loan');
      }
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.applicant, variables.applicantId] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.applicants] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.modelStats] });
    },
  });
}
