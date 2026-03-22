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
  id: number;
  name?: string; // Full name from database
  firstName?: string; // For backward compatibility
  lastName?: string; // For backward compatibility
  email: string;
  phone: string;
  dateOfBirth: string;
  age?: number;
  gender?: 'M' | 'F' | 'Other';
  maritalStatus?: 'Single' | 'Married' | 'Divorced' | 'Widowed';
  dependents?: number;
  nic?: string;
  // Financial
  monthlyIncome?: number;
  annualIncome?: number;
  employmentType?: 'Employed' | 'Self-Employed' | 'Unemployed' | 'Student' | 'Retired';
  employmentStatus?: string;
  employmentLength?: number; // years
  yearsEmployed?: number;
  occupation?: string;
  employerName?: string;
  creditScore?: number;
  existingLoansCount?: number;
  existingDebtAmount?: number;
  assetsValue?: number;
  
  // Loan Details
  loanAmount: number;
  loanPurpose: string;
  loanTerm?: number; // months
  loanTermMonths?: number;
  
  // Address
  address?: string;
  addressLine1?: string;
  addressLine2?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  postalCode?: string;
  country?: string;
  educationLevel?: string;
  
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
  passed: boolean; // For MitigationSuggestions component
  description: string; // For MitigationSuggestions component
  suggestion?: string; // Optional suggestion for failed rules
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

export interface FinancialStats {
  totalLoansDisbursed: number;
  totalLoanAmount: number;
  totalInterestEarned: number;
  avgInterestRate: number;
  activeLoans: number;
  paidOffLoans: number;
  pendingApplications: number;
  approvedThisMonth: number;
  approvalRate: number;
  pendingReviews: number;
}

export interface ModelHealth {
  status: 'healthy' | 'degraded' | 'offline' | 'unhealthy';
  lastUpdated?: string;
  version?: string;
  avgResponseTime?: number;
  successRate?: number;
  errorRate?: number;
  // Additional fields from backend
  model_loaded?: boolean;
  bayesian_reasoner_loaded?: boolean;
  features_loaded?: boolean;
  total_features?: number;
  optimal_threshold?: number;
  reasoning_capability?: string;
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
  educationLevel: 'High School' | 'Bachelor' | 'Master' | 'PhD' | 'Other';
  assetsValue: number;
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
  paymentStatus: 'on_time' | 'late' | 'defaulted' | 'completed' | 'current' | 'pending';
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
// ============================================
// ML PREDICTION & REASONING TYPES
// ============================================

export interface FeatureInfluence {
  feature_name: string;
  feature_value: number;
  discretized_value: number;
  influence_direction: 'increases_risk' | 'decreases_risk' | 'neutral';
  influence_strength: number;
  conditional_probability: number;
  explanation: string;
}

export interface InferencePath {
  parent_nodes: string[];
  child_nodes: string[];
  path_strength: number;
  description: string;
}

export interface EligibilityResult {
  applicant_id?: number;
  eligible: boolean;
  risk_score: number;
  probability: number;
  decision: 'APPROVE' | 'REJECT';
  risk_level: string;
  summary_explanation: string;
  feature_importance?: {
    feature: string;
    importance: number;
    direction: string;
  }[];
  risk_analysis?: any; // Allow flexible structure
  risk_factors: any[]; // Allow flexible structure for rule-based vs ML factors
  protective_factors: any[]; // Allow flexible structure
  recommendations: string[];
  confidence_score: number;
  model_type?: string;
  // Additional fields for loan details display
  loan_details?: any;
  financial_profile?: any;
  raw_decision?: any;
  raw_model_info?: any;
}

export interface PredictionWithReasoning {
  prediction: number;
  probability: number;
  risk_level: string;
  decision: 'APPROVE' | 'REJECT';
  top_risk_factors: FeatureInfluence[];
  top_protective_factors: FeatureInfluence[];
  inference_paths: InferencePath[];
  summary_explanation: string;
  detailed_explanation: string;
  conditional_probabilities: Record<string, number>;
  confidence_score: number;
  evidence_strength: string;
  model_type: string;
  tabnet_probability?: number;
  bayesian_probability?: number;
}

export interface BayesianNetworkNode {
  id: string;
  description: string;
  is_target: boolean;
}

export interface BayesianNetworkEdge {
  from: string;
  to: string;
  from_desc: string;
  to_desc: string;
}

export interface BayesianNetworkStructure {
  nodes: BayesianNetworkNode[];
  edges: BayesianNetworkEdge[];
  target_parents: string[];
  total_nodes: number;
  total_edges: number;
}

export interface ScenarioComparison {
  scenario_a: PredictionWithReasoning;
  scenario_b: PredictionWithReasoning;
  comparison: {
    probability_difference: number;
    changed_features: {
      feature: string;
      original_value: number;
      new_value: number;
      change: number;
    }[];
    summary: string;
    decision_changed: boolean;
  };
}

export interface ModelInfo {
  tabnet_loaded: boolean;
  bayesian_reasoner_loaded: boolean;
  total_features: number;
  optimal_threshold: number;
  model_type: string;
  capabilities: {
    basic_prediction: boolean;
    bayesian_reasoning: boolean;
    feature_explanation: boolean;
    network_visualization: boolean;
    scenario_comparison: boolean;
  };
}

// Simplified applicant for dropdown selection
export interface ApplicantOption {
  id: number;
  name: string;
  nic: string;
  email: string;
  monthlyIncome?: number;
  loanAmount?: number;
  loanTerm?: number;
  loanTermMonths?: number;
}
