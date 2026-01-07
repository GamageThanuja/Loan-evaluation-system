'use client';

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import predictionService from '@/services/prediction';
import {
  DashboardStats,
  ModelHealth,
  ModelPerformance,
  BatchPrediction,
} from '@/types';
import { QUERY_KEYS } from './usePrediction';

export function useModelStats(): UseQueryResult<DashboardStats, Error> {
  return useQuery({
    queryKey: [QUERY_KEYS.modelStats],
    queryFn: async () => {
      const response = await predictionService.getModelStats();
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch model stats');
      }
      return response.data;
    },
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 60 * 1000, // Auto-refetch every minute
  });
}

export function useModelHealth(): UseQueryResult<ModelHealth, Error> {
  return useQuery({
    queryKey: [QUERY_KEYS.modelHealth],
    queryFn: async () => {
      const response = await predictionService.getModelHealth();
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch model health');
      }
      return response.data;
    },
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Auto-refetch every 30 seconds
  });
}

export function useModelPerformance(): UseQueryResult<ModelPerformance[], Error> {
  return useQuery({
    queryKey: [QUERY_KEYS.modelPerformance],
    queryFn: async () => {
      const response = await predictionService.getModelPerformance();
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch model performance');
      }
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useBatchPredictions(): UseQueryResult<BatchPrediction[], Error> {
  return useQuery({
    queryKey: [QUERY_KEYS.batchPredictions],
    queryFn: async () => {
      const response = await predictionService.getBatchPredictions();
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch batch predictions');
      }
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}
