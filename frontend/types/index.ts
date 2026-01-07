// User & Authentication
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'loan_officer' | 'bank_manager';
  avatar?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  role: 'loan_officer' | 'bank_manager';
}

// Applicant & Application
export interface Applicant {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  age: number;
  gender: 'M' | 'F' | 'Other';
  maritalStatus: 'Single' | 'Married' | 'Divorced' | 'Widowed';
  dependents: number;
  
  // Financial
  annualIncome: number;
  employmentType: 'Employed' | 'Self-Employed' | 'Unemployed' | 'Student' | 'Retired';
  employmentLength: number; // years
  creditScore: number;
  
  // Loan Details
  loanAmount: number;
  loanPurpose: 'Home' | 'Auto' | 'Personal' | 'Education' | 'Business' | 'Other';
  loanTerm: number; // months
  
  // Address
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  
  // Metadata
  createdAt: string;
  updatedAt: string;
  status: 'pending' | 'approved' | 'rejected' | 'under_review';
  assignedTo?: string;
}

// Prediction & Risk Assessment
export interface PredictionRequest {
  applicantId: string;
  features: ModelFeatures;
}

export interface ModelFeatures {
  EXT_SOURCE_MEAN: number;
  CREDIT_INCOME_RATIO: number;
  AGE_YEARS: number;
  DAYS_EMPLOYED: number;
  ANNUITY_INCOME_RATIO: number;
  CREDIT_GOODS_RATIO: number;
  DAYS_ID_PUBLISH: number;
  REGION_RATING: number;
  [key: string]: number;
}

export interface PredictionResult {
  id: string;
  applicantId: string;
  riskScore: number;
  decision: 'APPROVE' | 'REJECT' | 'MANUAL_REVIEW';
  confidence: number;
  timestamp: string;
  
  // Explanations
  shapExplanation: ShapExplanation;
  bayesianNetwork: BayesianNetwork;
  businessRules: BusinessRule[];
  
  // Model Info
  modelVersion: string;
  threshold: {
    low: number;
    medium: number;
    high: number;
  };
}

export interface ShapExplanation {
  topFeatures: ShapFeature[];
  baseValue: number;
  predictionValue: number;
}

export interface ShapFeature {
  feature: string;
  value: number;
  shapValue: number;
  impact: 'positive' | 'negative';
  displayName: string;
}

export interface BayesianNetwork {
  nodes: BayesianNode[];
  edges: BayesianEdge[];
  causalPaths: CausalPath[];
}

export interface BayesianNode {
  id: string;
  name: string;
  displayName: string;
  probability: number;
  state: string;
}

export interface BayesianEdge {
  from: string;
  to: string;
  strength: number;
  type: 'causal' | 'correlational';
}

export interface CausalPath {
  path: string[];
  probability: number;
  impact: number;
  description: string;
}

export interface BusinessRule {
  id: string;
  rule: string;
  triggered: boolean;
  severity: 'info' | 'warning' | 'critical';
  recommendation: string;
  actionRequired: boolean;
}

// Dashboard & Reports
export interface DashboardStats {
  totalPredictions: number;
  approvalRate: number;
  rejectionRate: number;
  avgRiskScore: number;
  pendingReviews: number;
  modelAccuracy: number;
  modelAUC: number;
}

export interface ModelHealth {
  status: 'healthy' | 'degraded' | 'offline';
  lastUpdated: string;
  version: string;
  avgResponseTime: number;
  successRate: number;
  errorRate: number;
}

export interface RecentPrediction {
  id: string;
  applicantName: string;
  riskScore: number;
  decision: string;
  timestamp: string;
  status: string;
}

export interface ReportFilters {
  startDate: string;
  endDate: string;
  decision?: 'APPROVE' | 'REJECT' | 'MANUAL_REVIEW';
  riskLevel?: 'LOW' | 'MEDIUM' | 'HIGH';
  minRiskScore?: number;
  maxRiskScore?: number;
}

export interface ModelPerformance {
  date: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  auc: number;
}

export interface BatchPrediction {
  id: string;
  fileName: string;
  totalRecords: number;
  processed: number;
  approved: number;
  rejected: number;
  status: 'processing' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
}

// API Response
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Form Data
export interface ApplicantFormData {
  // Personal
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  gender: 'M' | 'F' | 'Other';
  maritalStatus: 'Single' | 'Married' | 'Divorced' | 'Widowed';
  dependents: number;
  
  // Financial
  annualIncome: number;
  employmentType: 'Employed' | 'Self-Employed' | 'Unemployed' | 'Student' | 'Retired';
  employmentLength: number;
  creditScore: number;
  
  // Loan
  loanAmount: number;
  loanPurpose: 'Home' | 'Auto' | 'Personal' | 'Education' | 'Business' | 'Other';
  loanTerm: number;
  
  // Address (optional)
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
}

// Enums
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type DecisionType = 'APPROVE' | 'REJECT' | 'MANUAL_REVIEW';
export type ApplicantStatus = 'pending' | 'approved' | 'rejected' | 'under_review';
export type UserRole = 'loan_officer' | 'bank_manager';

// Utility Types
export interface SelectOption {
  value: string;
  label: string;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: string | number;
}

export interface TableColumn<T> {
  id: keyof T;
  label: string;
  minWidth?: number;
  align?: 'left' | 'right' | 'center';
  format?: (value: any) => string;
}
