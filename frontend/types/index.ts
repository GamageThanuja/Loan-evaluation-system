// User & Authentication
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'loan_officer' | 'manager';
  phone?: string;
  is_active?: boolean;
  created_at?: string;
  last_login?: string;
  avatar?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  role?: 'loan_officer' | 'manager';
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
  nic?: string;
  
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
  
  // Eligibility
  eligibilityStatus?: 'eligible' | 'not_eligible' | 'not_checked';
  eligibilityReasons?: string[];
  riskScore?: number;
  
  // Review
  reviewNotes?: string;
  rejectionReason?: string;
  approvedBy?: string;
  approvedAt?: string;
  rejectedBy?: string;
  rejectedAt?: string;
}

// Eligibility Check Response
export interface EligibilityCheckResult {
  applicantId: string;
  isEligible: boolean;
  riskScore: number;
  reasons: string[];
  checkedAt: string;
  checkedBy: string;
}

// Review Request
export interface ReviewSubmission {
  notes: string;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
}

// Approval/Rejection
export interface ApprovalData {
  notes?: string;
  interestRate?: number;
  approvedAmount?: number;
  conditions?: string[];
}

export interface RejectionData {
  reason: string;
  additionalNotes?: string;
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
export type UserRole = 'loan_officer' | 'manager';

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

// Audit Trail
export interface AuditLogEntry {
  id: string;
  timestamp: string;
  action: 'created' | 'updated' | 'status_changed' | 'reviewed' | 'approved' | 'rejected' | 'payment_made' | 'document_uploaded' | 'note_added';
  performedBy: {
    id: string;
    name: string;
    role: UserRole;
  };
  description: string;
  changes?: {
    field: string;
    oldValue: string;
    newValue: string;
  }[];
  metadata?: Record<string, any>;
}

// Repayment History
export interface RepaymentSchedule {
  id: string;
  loanId: string;
  installmentNumber: number;
  dueDate: string;
  principalAmount: number;
  interestAmount: number;
  totalAmount: number;
  status: 'pending' | 'paid' | 'overdue' | 'partial';
  paidAmount?: number;
  paidDate?: string;
  lateFee?: number;
  remainingBalance: number;
}

export interface RepaymentSummary {
  totalLoanAmount: number;
  totalPaid: number;
  totalRemaining: number;
  totalInterest: number;
  nextPaymentDue: string;
  nextPaymentAmount: number;
  overdueAmount: number;
  numberOfPayments: number;
  paymentsCompleted: number;
  paymentStatus: 'on_time' | 'late' | 'defaulted' | 'completed';
}

// Credit History
export interface CreditHistoryEntry {
  id: string;
  date: string;
  creditScore: number;
  bureau: 'Experian' | 'Equifax' | 'TransUnion';
  reason?: string;
  change?: number;
}

export interface CreditProfile {
  currentScore: number;
  scoreHistory: CreditHistoryEntry[];
  creditUtilization: number;
  totalCreditLines: number;
  oldestAccount: string;
  recentInquiries: number;
  delinquencies: number;
  publicRecords: number;
  averageAccountAge: number;
}

// Transactions
export interface Transaction {
  id: string;
  date: string;
  type: 'payment' | 'disbursement' | 'fee' | 'refund' | 'adjustment' | 'penalty';
  amount: number;
  description: string;
  status: 'completed' | 'pending' | 'failed' | 'reversed';
  paymentMethod?: 'bank_transfer' | 'card' | 'cash' | 'check' | 'online';
  referenceNumber?: string;
  balance: number;
  notes?: string;
}

export interface TransactionSummary {
  totalTransactions: number;
  totalDebits: number;
  totalCredits: number;
  lastTransaction?: Transaction;
  monthlyTransactions: {
    month: string;
    count: number;
    amount: number;
  }[];
}

// Loan Application Details
export interface LoanApplicationDetails extends Applicant {
  // Loan specific details
  interestRate: number;
  monthlyPayment: number;
  totalPayable: number;
  disbursementDate?: string;
  maturityDate?: string;
  
  // Related data
  auditLog: AuditLogEntry[];
  repaymentSchedule: RepaymentSchedule[];
  repaymentSummary: RepaymentSummary;
  creditProfile: CreditProfile;
  transactions: Transaction[];
  transactionSummary: TransactionSummary;
  
  // Documents
  documents?: {
    id: string;
    name: string;
    type: string;
    uploadedAt: string;
    url: string;
  }[];
  
  // Notes
  notes?: {
    id: string;
    content: string;
    createdBy: string;
    createdAt: string;
  }[];
}
