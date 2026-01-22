/**
 * Status Utility Hook
 * Provides easy access to status information and colors from APIs
 */
'use client';

import { useMemo } from 'react';
import { useApplicationStatusesWithColors, useEligibilityStatuses } from './useStatusManagement';
import type { ApplicationStatusWithColor, EligibilityStatus } from '@/services/statusManagement';

/**
 * Hook to get status utilities (colors, names, etc.)
 */
export function useStatusUtils() {
  const { data: applicationStatuses, isLoading: isLoadingAppStatuses } = useApplicationStatusesWithColors(true);
  const { data: eligibilityStatuses, isLoading: isLoadingEligibility } = useEligibilityStatuses(true);

  const statusMap = useMemo(() => {
    if (!applicationStatuses) return new Map();
    
    const map = new Map<string, ApplicationStatusWithColor>();
    applicationStatuses.forEach((status) => {
      map.set(status.code.toLowerCase(), status);
      map.set(status.id.toString(), status);
    });
    return map;
  }, [applicationStatuses]);

  const eligibilityMap = useMemo(() => {
    if (!eligibilityStatuses) return new Map();
    
    const map = new Map<string, EligibilityStatus>();
    eligibilityStatuses.forEach((status) => {
      map.set(status.code.toLowerCase(), status);
      map.set(status.id.toString(), status);
    });
    return map;
  }, [eligibilityStatuses]);

  /**
   * Get application status by code or ID
   */
  const getApplicationStatus = (status: string | number | null | undefined): ApplicationStatusWithColor | null => {
    if (!status) return null;
    return statusMap.get(status.toString().toLowerCase()) || null;
  };

  /**
   * Get eligibility status by code or ID
   */
  const getEligibilityStatus = (status: string | number | null | undefined): EligibilityStatus | null => {
    if (!status) return null;
    return eligibilityMap.get(status.toString().toLowerCase()) || null;
  };

  /**
   * Get status color code (HEX) by status code or ID
   */
  const getStatusColorCode = (status: string | number | null | undefined): string | null => {
    const statusInfo = getApplicationStatus(status);
    return statusInfo?.colorCode || null;
  };

  /**
   * Get status color name (Material-UI compatible) by status code or ID
   */
  const getStatusColorName = (status: string | number | null | undefined): 'success' | 'error' | 'warning' | 'info' | 'default' => {
    const statusInfo = getApplicationStatus(status);
    const colorName = statusInfo?.colorName?.toLowerCase();
    
    if (colorName === 'success') return 'success';
    if (colorName === 'error') return 'error';
    if (colorName === 'warning') return 'warning';
    if (colorName === 'info') return 'info';
    return 'default';
  };

  /**
   * Get status display name by code or ID
   */
  const getStatusName = (status: string | number | null | undefined): string => {
    const statusInfo = getApplicationStatus(status);
    return statusInfo?.name || status?.toString() || 'Unknown';
  };

  /**
   * Get eligibility status display name by code or ID
   */
  const getEligibilityName = (status: string | number | null | undefined): string => {
    const statusInfo = getEligibilityStatus(status);
    return statusInfo?.name || 'Not Checked';
  };

  return {
    applicationStatuses,
    eligibilityStatuses,
    isLoading: isLoadingAppStatuses || isLoadingEligibility,
    getApplicationStatus,
    getEligibilityStatus,
    getStatusColorCode,
    getStatusColorName,
    getStatusName,
    getEligibilityName,
  };
}

