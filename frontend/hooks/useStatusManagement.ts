/**
 * useStatusManagement Hook
 * React Query hooks for status management CRUD operations
 */
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { statusManagementService } from '@/services/statusManagement';
import type {
  EligibilityStatusCreate,
  EligibilityStatusUpdate,
  ApplicationStatusCreate,
  ApplicationStatusUpdate,
  StatusColorCreate,
  StatusColorUpdate,
} from '@/services/statusManagement';

// Query keys
export const statusKeys = {
  all: ['status-management'] as const,
  eligibilityStatuses: (isActive?: boolean) => 
    [...statusKeys.all, 'eligibility-statuses', isActive] as const,
  eligibilityStatus: (id: number) => 
    [...statusKeys.all, 'eligibility-status', id] as const,
  applicationStatuses: (isActive?: boolean) => 
    [...statusKeys.all, 'application-statuses', isActive] as const,
  applicationStatusesWithColors: (isActive?: boolean) => 
    [...statusKeys.all, 'application-statuses-with-colors', isActive] as const,
  applicationStatus: (id: number) => 
    [...statusKeys.all, 'application-status', id] as const,
  statusColors: (statusId?: number) => 
    [...statusKeys.all, 'status-colors', statusId] as const,
  statusColor: (id: number) => 
    [...statusKeys.all, 'status-color', id] as const,
};

// ==================== Eligibility Status Hooks ====================

/**
 * Get all eligibility statuses
 */
export function useEligibilityStatuses(isActive?: boolean) {
  return useQuery({
    queryKey: statusKeys.eligibilityStatuses(isActive),
    queryFn: async () => {
      const response = await statusManagementService.getEligibilityStatuses(isActive);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
  });
}

/**
 * Get eligibility status by ID
 */
export function useEligibilityStatus(id: number) {
  return useQuery({
    queryKey: statusKeys.eligibilityStatus(id),
    queryFn: async () => {
      const response = await statusManagementService.getEligibilityStatus(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

/**
 * Create eligibility status mutation
 */
export function useCreateEligibilityStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: EligibilityStatusCreate) => {
      const response = await statusManagementService.createEligibilityStatus(data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: statusKeys.eligibilityStatuses() });
    },
  });
}

/**
 * Update eligibility status mutation
 */
export function useUpdateEligibilityStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: EligibilityStatusUpdate }) => {
      const response = await statusManagementService.updateEligibilityStatus(id, data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: statusKeys.eligibilityStatuses() });
      queryClient.invalidateQueries({ queryKey: statusKeys.eligibilityStatus(variables.id) });
    },
  });
}

/**
 * Delete eligibility status mutation
 */
export function useDeleteEligibilityStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await statusManagementService.deleteEligibilityStatus(id);
      if (!response.success) throw new Error(response.error);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: statusKeys.eligibilityStatuses() });
    },
  });
}

// ==================== Application Status Hooks ====================

/**
 * Get all application statuses
 */
export function useApplicationStatuses(isActive?: boolean) {
  return useQuery({
    queryKey: statusKeys.applicationStatuses(isActive),
    queryFn: async () => {
      const response = await statusManagementService.getApplicationStatuses(isActive);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
  });
}

/**
 * Get all application statuses with colors
 */
export function useApplicationStatusesWithColors(isActive?: boolean) {
  return useQuery({
    queryKey: statusKeys.applicationStatusesWithColors(isActive),
    queryFn: async () => {
      const response = await statusManagementService.getApplicationStatusesWithColors(isActive);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
}

/**
 * Get application status by ID
 */
export function useApplicationStatus(id: number) {
  return useQuery({
    queryKey: statusKeys.applicationStatus(id),
    queryFn: async () => {
      const response = await statusManagementService.getApplicationStatus(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

/**
 * Create application status mutation
 */
export function useCreateApplicationStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: ApplicationStatusCreate) => {
      const response = await statusManagementService.createApplicationStatus(data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatuses() });
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatusesWithColors() });
    },
  });
}

/**
 * Update application status mutation
 */
export function useUpdateApplicationStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: ApplicationStatusUpdate }) => {
      const response = await statusManagementService.updateApplicationStatus(id, data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatuses() });
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatusesWithColors() });
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatus(variables.id) });
    },
  });
}

/**
 * Delete application status mutation
 */
export function useDeleteApplicationStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await statusManagementService.deleteApplicationStatus(id);
      if (!response.success) throw new Error(response.error);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatuses() });
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatusesWithColors() });
    },
  });
}

// ==================== Status Color Hooks ====================

/**
 * Get all status colors
 */
export function useStatusColors(statusId?: number) {
  return useQuery({
    queryKey: statusKeys.statusColors(statusId),
    queryFn: async () => {
      const response = await statusManagementService.getStatusColors(statusId);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
  });
}

/**
 * Get status color by ID
 */
export function useStatusColor(id: number) {
  return useQuery({
    queryKey: statusKeys.statusColor(id),
    queryFn: async () => {
      const response = await statusManagementService.getStatusColor(id);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    enabled: !!id,
  });
}

/**
 * Create status color mutation
 */
export function useCreateStatusColor() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: StatusColorCreate) => {
      const response = await statusManagementService.createStatusColor(data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: statusKeys.statusColors() });
      queryClient.invalidateQueries({ queryKey: statusKeys.statusColors(variables.statusId) });
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatusesWithColors() });
    },
  });
}

/**
 * Update status color mutation
 */
export function useUpdateStatusColor() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: StatusColorUpdate }) => {
      const response = await statusManagementService.updateStatusColor(id, data);
      if (!response.success) throw new Error(response.error);
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: statusKeys.statusColors() });
      queryClient.invalidateQueries({ queryKey: statusKeys.statusColor(variables.id) });
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatusesWithColors() });
    },
  });
}

/**
 * Delete status color mutation
 */
export function useDeleteStatusColor() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await statusManagementService.deleteStatusColor(id);
      if (!response.success) throw new Error(response.error);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: statusKeys.statusColors() });
      queryClient.invalidateQueries({ queryKey: statusKeys.applicationStatusesWithColors() });
    },
  });
}

