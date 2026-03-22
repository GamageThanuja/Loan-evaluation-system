import { type ClassValue, clsx } from 'clsx';
import { RiskLevel, DecisionType } from '@/types';

// Tailwind merge utility (simple version)
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// Format currency
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

// Format percentage
export function formatPercent(value: number, decimals: number = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

// Format date
export function formatDate(date: string | Date | null | undefined, includeTime: boolean = false): string {
  if (!date) return 'N/A';
  
  try {
    const d = new Date(date);
    
    // Check if date is valid
    if (isNaN(d.getTime())) {
      return 'Invalid Date';
    }

    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    };
    
    if (includeTime) {
      options.hour = '2-digit';
      options.minute = '2-digit';
    }
    
    return new Intl.DateTimeFormat('en-US', options).format(d);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid Date';
  }
}

// Format relative time
export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return '';
  
  try {
    const now = new Date();
    const past = new Date(date);
    
    // Check if date is valid
    if (isNaN(past.getTime())) {
      return '';
    }

    const diffInSeconds = Math.floor((now.getTime() - past.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    
    return formatDate(date);
  } catch (error) {
    return '';
  }
}

// Get risk level from score
export function getRiskLevel(score: number): RiskLevel {
  const lowThreshold = parseFloat(process.env.NEXT_PUBLIC_RISK_THRESHOLD_LOW || '0.15');
  const mediumThreshold = parseFloat(process.env.NEXT_PUBLIC_RISK_THRESHOLD_MEDIUM || '0.30');
  
  if (score <= lowThreshold) return 'LOW';
  if (score <= mediumThreshold) return 'MEDIUM';
  return 'HIGH';
}

// Get risk color
export function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case 'LOW':
      return '#2e7d32'; // success.main
    case 'MEDIUM':
      return '#ed6c02'; // warning.main
    case 'HIGH':
      return '#d32f2f'; // error.main
    default:
      return '#0288d1'; // info.main
  }
}

// Get decision color
export function getDecisionColor(decision: DecisionType): string {
  switch (decision) {
    case 'APPROVE':
      return '#2e7d32'; // success.main
    case 'REJECT':
      return '#d32f2f'; // error.main
    case 'MANUAL_REVIEW':
      return '#ed6c02'; // warning.main
    default:
      return '#0288d1'; // info.main
  }
}

// Calculate age from date of birth
export function calculateAge(dateOfBirth: string | Date | null | undefined): number {
  if (!dateOfBirth) return 0;
  
  try {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    
    // Check if date is valid
    if (isNaN(birthDate.getTime())) {
      return 0;
    }

    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  } catch (error) {
    return 0;
  }
}

// Generate applicant features from form data
export function generateFeaturesFromApplicant(applicant: any): any {
  const age = calculateAge(applicant.dateOfBirth);
  const creditIncomeRatio = applicant.loanAmount / applicant.annualIncome;
  const annuityIncomeRatio = (applicant.loanAmount / applicant.loanTerm) / (applicant.annualIncome / 12);
  
  return {
    AGE_YEARS: age,
    CREDIT_INCOME_RATIO: creditIncomeRatio,
    ANNUITY_INCOME_RATIO: annuityIncomeRatio,
    EXT_SOURCE_MEAN: applicant.creditScore / 850, // Normalize credit score
    DAYS_EMPLOYED: applicant.employmentLength * 365,
    CREDIT_GOODS_RATIO: 1.0, // Default value
    DAYS_ID_PUBLISH: -4000, // Default value
    REGION_RATING: 2, // Default value
  };
}

// Truncate text
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + '...';
}

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Local storage helpers
export const storage = {
  get: <T>(key: string, defaultValue: T): T => {
    if (typeof window === 'undefined') return defaultValue;
    
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error(`Error reading from localStorage:`, error);
      return defaultValue;
    }
  },
  
  set: <T>(key: string, value: T): void => {
    if (typeof window === 'undefined') return;
    
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error writing to localStorage:`, error);
    }
  },
  
  remove: (key: string): void => {
    if (typeof window === 'undefined') return;
    
    try {
      window.localStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing from localStorage:`, error);
    }
  },
};

// Error handling
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  return 'An unexpected error occurred';
}

// Generate random ID
export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

// Sleep utility for testing
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
