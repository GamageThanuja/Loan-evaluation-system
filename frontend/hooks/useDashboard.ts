'use client';

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { FinancialStats } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Dashboard API functions
const dashboardApi = {
  async getFinancialStats() {
    const response = await fetch(`${API_URL}/api/dashboard/financial-stats`);
    if (!response.ok) {
      throw new Error('Failed to fetch financial stats');
    }
    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch financial stats');
    }
    return data.data;
  },

  async getMonthlyStats() {
    const response = await fetch(`${API_URL}/api/dashboard/monthly-summary`);
    if (!response.ok) {
      throw new Error('Failed to fetch monthly stats');
    }
    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch monthly stats');
    }
    return data.data;
  },

  async getRecentApplications(limit = 10) {
    const response = await fetch(`${API_URL}/api/dashboard/recent-applications?limit=${limit}`);
    if (!response.ok) {
      throw new Error('Failed to fetch recent applications');
    }
    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch recent applications');
    }
    return data.data;
  }
};

// Custom hooks
export function useFinancialStats(): UseQueryResult<FinancialStats, Error> {
  return useQuery({
    queryKey: ['dashboard', 'financial-stats'],
    queryFn: dashboardApi.getFinancialStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
  });
}

export function useMonthlyStats(): UseQueryResult<any, Error> {
  return useQuery({
    queryKey: ['dashboard', 'monthly-stats'],
    queryFn: dashboardApi.getMonthlyStats,
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 10 * 60 * 1000, // Auto-refetch every 10 minutes
  });
}

export function useRecentApplications(limit = 10): UseQueryResult<any[], Error> {
  return useQuery({
    queryKey: ['dashboard', 'recent-applications', limit],
    queryFn: () => dashboardApi.getRecentApplications(limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 2 * 60 * 1000, // Auto-refetch every 2 minutes
  });
}

// Export the API functions for direct use if needed
export { dashboardApi };