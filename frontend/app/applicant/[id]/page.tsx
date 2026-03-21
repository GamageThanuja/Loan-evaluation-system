'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Tabs,
  Tab,
  Paper,
  CircularProgress,
  Avatar,
  Divider,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Person,
  History,
  Assessment,
  Psychology,
  Lightbulb,
  AccountBalance,
  Receipt,
  CreditScore as CreditScoreIcon,
  Warning,
  Pending,
} from '@mui/icons-material';
import { useRouter, useParams } from 'next/navigation';
import { useApplicant, useApproveLoan, useRejectLoan } from '@/hooks/usePrediction';
import {
  useLoanDetails,
  useCreditHistory,
  useRepaymentHistory,
  useTransactionHistory,
  useAuditTrail,
} from '@/hooks/useApplicants';
import { useStatusUtils } from '@/hooks/useStatusUtils';
import { useAuth } from '@/hooks/useAuth';
import { DetailSkeleton } from '@/components/ui/LoadingSkeleton';
import RiskAssessment from '@/components/loan/RiskAssessment';
import BayesianReasoning from '@/components/loan/BayesianReasoning';
import MitigationSuggestions from '@/components/loan/MitigationSuggestions';
import AuditTrail from '@/components/loan/AuditTrail';
import RepaymentHistory from '@/components/loan/RepaymentHistory';
import CreditHistory from '@/components/loan/CreditHistory';
import TransactionList from '@/components/loan/TransactionList';
import { formatCurrency, getRiskLevel } from '@/lib/utils';
import predictionService from '@/services/prediction';
import { Applicant } from '@/types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function ApplicantDetailPage() {
  const router = useRouter();
  const params = useParams();
  const applicantId = params.id as string;
  const { isManager } = useAuth();

  const { data: applicant, isLoading: applicantLoading, refetch: refetchApplicant } = useApplicant(applicantId);
  const { data: loanDetails } = useLoanDetails(applicantId);
  const { data: creditHistory, isLoading: isLoadingCredit } = useCreditHistory(applicantId);
  const { data: repaymentHistory, isLoading: isLoadingRepayment } = useRepaymentHistory(applicantId);
  const { data: transactionHistory, isLoading: isLoadingTransactions } = useTransactionHistory(applicantId);
  const { data: auditLog, isLoading: isLoadingAudit } = useAuditTrail(applicantId);
  const approveLoan = useApproveLoan();
  const rejectLoan = useRejectLoan();
  const statusUtils = useStatusUtils();
  
  // Wait for status data to load before rendering chips with colors
  const isStatusDataReady = !statusUtils.isLoading;

  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [checkingEligibility, setCheckingEligibility] = useState(false);
  const [eligibilityError, setEligibilityError] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    return statusUtils.getStatusColorName(status);
  };

  const getStatusIcon = (status: string) => {
    const statusInfo = statusUtils.getApplicationStatus(status);
    const statusCode = statusInfo?.code || status?.toLowerCase() || 'pending';
    
    switch (statusCode) {
      case 'approved':
        return <CheckCircle fontSize="small" />;
      case 'rejected':
        return <Cancel fontSize="small" />;
      case 'under_review':
        return <Pending fontSize="small" />;
      default:
        return <Warning fontSize="small" />;
    }
  };

  if (applicantLoading) {
    return <DetailSkeleton />;
  }

  if (!applicant) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">Applicant not found</Alert>
      </Box>
    );
  }

  // Check if we have prediction data (from applicant response or previous check)
  const applicantData = applicant as Applicant & { 
    prediction_confidence?: number;
    loan_term_months?: number;
  };
  const hasPrediction = applicant.riskScore !== undefined && applicant.riskScore !== null;
  const riskScore = applicant.riskScore ?? 0;
  const riskLevel = getRiskLevel(riskScore);
  const decision: 'APPROVE' | 'REJECT' | 'MANUAL_REVIEW' = 
    applicant.eligibilityStatus === 'eligible' ? 'APPROVE' : 
    applicant.eligibilityStatus === 'not_eligible' ? 'REJECT' : 'MANUAL_REVIEW';
  const confidence = applicantData.prediction_confidence ?? 0.5;

  // Build a prediction-like object for components
  const prediction = {
    riskScore,
    decision,
    confidence,
    bayesianNetwork: {
      nodes: [],
      edges: [],
      causalPaths: []
    },
    businessRules: applicant.eligibilityReasons?.map((reason: string) => ({
      id: reason,
      rule: reason,
      description: reason,
      triggered: true,
      passed: false,
      severity: 'warning' as const,
      recommendation: reason,
      actionRequired: true
    })) || []
  };

  const handleRunEligibilityCheck = async () => {
    setCheckingEligibility(true);
    setEligibilityError(null);
    
    try {
      const response = await predictionService.checkEligibility(
        parseInt(applicantId),
        applicant.loanAmount,
        applicant.loanTermMonths ?? applicantData.loan_term_months ?? 12
      );
      
      if (response.success) {
        await refetchApplicant();
      } else {
        setEligibilityError(response.error || 'Failed to check eligibility');
      }
    } catch (error) {
      setEligibilityError('An error occurred while checking eligibility');
      console.error('Eligibility check error:', error);
    } finally {
      setCheckingEligibility(false);
    }
  };

  const handleApprove = async () => {
    try {
      await approveLoan.mutateAsync({ applicantId });
      setApproveDialogOpen(false);
      router.push('/applicant');
    } catch (error) {
      console.error('Failed to approve loan:', error);
    }
  };

  const handleReject = async () => {
    if (!rejectReason.trim()) return;

    try {
      await rejectLoan.mutateAsync({ applicantId, reason: rejectReason });
      setRejectDialogOpen(false);
      router.push('/applicant');
    } catch (error) {
      console.error('Failed to reject loan:', error);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>

      <Paper sx={{ p: 3 }}>
        <Grid container spacing={3} alignItems="center">
        <Grid item>
          <Avatar
          sx={{
            width: 80,
            height: 80,
            bgcolor: 'primary.main',
            fontSize: '2rem',
          }}
          >
          {applicant.firstName?.[0] || (applicant as any).name?.[0] || 'U'}{applicant.lastName?.[0] || ''}
          </Avatar>
        </Grid>

        <Grid item xs>
          <Typography variant="h4" fontWeight={700} gutterBottom>
          {applicant.firstName && applicant.lastName 
            ? `${applicant.firstName} ${applicant.lastName}` 
            : (applicant as any).name || 'Unknown'}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
          {(() => {
            const status = applicant.status || 'pending';
            const statusInfo = statusUtils.getApplicationStatus(status);
            const statusName = statusUtils.getStatusName(status);
            const colorCode = statusInfo?.colorCode;

            // If we have a color code from API and data is ready, use it directly
            if (isStatusDataReady && colorCode) {
            return (
              <Chip
              label={statusName}
              size="small"
              icon={getStatusIcon(status)}
              sx={{
                bgcolor: `${colorCode}20`,
                color: colorCode,
                border: `1px solid ${colorCode}40`,
                fontWeight: 600,
                '& .MuiChip-icon': {
                color: colorCode,
                },
              }}
              />
            );
            }

            // Fallback to Material-UI theme colors (while loading or if no color code)
            return (
            <Chip
              label={statusName}
              color={getStatusColor(status)}
              size="small"
              icon={getStatusIcon(status)}
            />
            );
          })()}
          <Chip
            label={`Loan ID: ${applicant.id}`}
            variant="outlined"
            size="small"
          />
          </Box>
        </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        {/* Key Metrics */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ flex: '1 1 calc(14.28% - 16px)', minWidth: '120px' }}>
          <Typography variant="caption" color="text.secondary">
          Loan Amount
          </Typography>
          <Typography variant="h6" fontWeight={600}>
          {formatCurrency(applicant.loanAmount || 0)}
          </Typography>
        </Box>
        <Box sx={{ flex: '1 1 calc(14.28% - 16px)', minWidth: '120px' }}>
          <Typography variant="caption" color="text.secondary">
          Interest Rate
          </Typography>
          <Typography variant="h6" fontWeight={600}>
          {loanDetails?.interestRate ?? (applicant as any).interestRate ?? 'N/A'}%
          </Typography>
        </Box>
        <Box sx={{ flex: '1 1 calc(14.28% - 16px)', minWidth: '120px' }}>
          <Typography variant="caption" color="text.secondary">
          Monthly Payment
          </Typography>
          <Typography variant="h6" fontWeight={600}>
          {formatCurrency(loanDetails?.monthlyPayment ?? (applicant as any).monthlyPayment ?? 0)}
          </Typography>
        </Box>
        <Box sx={{ flex: '1 1 calc(14.28% - 16px)', minWidth: '120px' }}>
          <Typography variant="caption" color="text.secondary">
          Credit Score
          </Typography>
          <Typography variant="h6" fontWeight={600} color="success.main">
          {applicant.creditScore ?? 'N/A'}
          </Typography>
        </Box>
        <Box sx={{ flex: '1 1 calc(14.28% - 16px)', minWidth: '120px' }}>
          <Typography variant="caption" color="text.secondary">
          Loan Purpose
          </Typography>
          <Typography variant="h6" fontWeight={600}>
          {applicant.loanPurpose ?? 'N/A'}
          </Typography>
        </Box>
        <Box sx={{ flex: '1 1 calc(14.28% - 16px)', minWidth: '120px' }}>
          <Typography variant="caption" color="text.secondary">
          Loan Term
          </Typography>
          <Typography variant="h6" fontWeight={600}>
          {(applicant as any).loanTermMonths ?? applicant.loanTerm ?? 0} months
          </Typography>
        </Box>
        <Box sx={{ flex: '1 1 calc(14.28% - 16px)', minWidth: '120px' }}>
          <Typography variant="caption" color="text.secondary">
          Total Payable
        </Typography>
          <Typography variant="h6" fontWeight={600}>
          {formatCurrency(loanDetails?.totalPayable ?? 0)}
        </Typography>
        </Box>
        </Box>
      </Paper>
      </Box>

      {/* Eligibility Error */}
      {eligibilityError && (
      <Alert severity="error" sx={{ mb: 3 }} onClose={() => setEligibilityError(null)}>
        {eligibilityError}
      </Alert>
      )}
      {/* Decision Banner - Show if eligibility was checked */}
      {hasPrediction && (
      <Alert
        severity={
        prediction.decision === 'APPROVE'
          ? 'success'
          : prediction.decision === 'REJECT'
          ? 'error'
          : 'warning'
        }
        sx={{ mb: 3 }}
      >
        <Typography variant="h6" fontWeight={600}>
        Recommendation: {prediction.decision}
        </Typography>
        <Typography variant="body2">
        {prediction.decision === 'APPROVE'
          ? 'The model recommends approving this loan application.'
          : prediction.decision === 'REJECT'
          ? 'The model recommends rejecting this loan application.'
          : 'This application requires manual review by a loan officer.'}
        </Typography>
      </Alert>
      )}

      {/* Rejection Reason (if rejected) */}
      {applicant.status === 'rejected' && (applicant as any)?.rejectionReason && (
      <Alert severity="error" sx={{ mb: 3 }}>
        <Typography variant="subtitle2" fontWeight={600}>Rejection Reason:</Typography>
        <Typography variant="body2">{(applicant as any).rejectionReason}</Typography>
      </Alert>
      )}

      {/* Main Tabs */}
      <Paper>
      <Tabs
        value={activeTab}
        onChange={(_e, newValue) => setActiveTab(newValue)}
        variant="scrollable"
        scrollButtons="auto"
          sx={{
        borderBottom: 1,
        borderColor: 'divider',
        px: 2,
        }}
      >
        <Tab icon={<Person />} iconPosition="start" label="Overview" />
        <Tab icon={<Assessment />} iconPosition="start" label="Risk Assessment" />
        <Tab icon={<Psychology />} iconPosition="start" label="Reasoning" />
        <Tab icon={<Lightbulb />} iconPosition="start" label="Suggestions" />
        <Tab icon={<AccountBalance />} iconPosition="start" label="Repayment History" />
        <Tab icon={<CreditScoreIcon />} iconPosition="start" label="Credit History" />
        <Tab icon={<Receipt />} iconPosition="start" label="Transactions" />
        <Tab icon={<History />} iconPosition="start" label="Audit Trail" />
      </Tabs>

      <Box sx={{ px: 3 }}>
        {/* Tab 0: Overview */}
        <TabPanel value={activeTab} index={0}>
      <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
            Personal Information
          </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Email</Typography>
            <Typography variant="body2">{applicant.email}</Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Phone</Typography>
            <Typography variant="body2">{applicant.phone}</Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Date of Birth</Typography>
              <Typography variant="body2">
                {applicant.dateOfBirth ? new Date(applicant.dateOfBirth).toLocaleDateString() : 'N/A'}
            </Typography>
              </Grid>
              <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Age</Typography>
              <Typography variant="body2">{applicant.age ?? 'N/A'} years</Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Gender</Typography>
            <Typography variant="body2">
                {applicant.gender === 'M' ? 'Male' : applicant.gender === 'F' ? 'Female' : applicant.gender || 'N/A'}
            </Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Marital Status</Typography>
              <Typography variant="body2">{applicant.maritalStatus ?? 'N/A'}</Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Education Level</Typography>
              <Typography variant="body2">{applicant.educationLevel ?? 'N/A'}</Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Total Assets</Typography>
              <Typography variant="body2" fontWeight={600}>
                {formatCurrency(applicant.assetsValue ?? 0)}
              </Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Dependents</Typography>
              <Typography variant="body2">{applicant.dependents ?? 'N/A'}</Typography>
          </Grid>
          </Grid>
        </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Employment & Income
          </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Employment Type</Typography>
              <Typography variant="body2">{applicant.employmentType ?? 'N/A'}</Typography>
              </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Employment Length</Typography>
              <Typography variant="body2">{applicant.employmentLength ?? 'N/A'} years</Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Monthly Income</Typography>
            <Typography variant="body2" fontWeight={600}>
                {formatCurrency(
                (applicant as any).monthlyIncome ?? 
                (applicant.annualIncome ? applicant.annualIncome / 12 : 0)
                )}
            </Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Annual Income</Typography>
              <Typography variant="body2" fontWeight={600}>
                {formatCurrency(
                applicant.annualIncome ?? 
                ((applicant as any).monthlyIncome ? (applicant as any).monthlyIncome * 12 : 0)
                )}
            </Typography>
          </Grid>
          <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Credit Score</Typography>
              <Typography variant="body2" fontWeight={600}>
                {applicant.creditScore ?? 'N/A'}
            </Typography>
          </Grid>
          </Grid>
        </CardContent>
        </Card>
      </Grid>


        </Grid>
        </TabPanel>

          {/* Tab 1: Risk Assessment */}
        <TabPanel value={activeTab} index={1}>
          <RiskAssessment
            riskScore={prediction.riskScore}
            riskLevel={riskLevel as 'LOW' | 'MEDIUM' | 'HIGH'}
            confidence={prediction.confidence}
            decision={prediction.decision}
          />
        </TabPanel>

          {/* Tab 2: Reasoning */}
        <TabPanel value={activeTab} index={2}>
          <BayesianReasoning
            bayesianNetwork={prediction.bayesianNetwork}
            decision={prediction.decision}
            riskScore={prediction.riskScore}
          />
        </TabPanel>

          {/* Tab 3: Suggestions */}
        <TabPanel value={activeTab} index={3}>
          <MitigationSuggestions
            riskScore={prediction.riskScore}
            decision={prediction.decision}
            creditScore={applicant.creditScore}
            debtToIncomeRatio={0.28}
            employmentLength={applicant.employmentLength}
            businessRules={prediction.businessRules}
          />
        </TabPanel>

        {/* Tab 4: Repayment History */}
        <TabPanel value={activeTab} index={4}>
        {isLoadingRepayment ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
          </Box>
        ) : repaymentHistory ? (
          <RepaymentHistory
          schedule={repaymentHistory.schedule}
          summary={repaymentHistory.summary}
          />
        ) : (
          <Alert severity="info">No repayment history available for this applicant.</Alert>
        )}
        </TabPanel>

        {/* Tab 5: Credit History */}
        <TabPanel value={activeTab} index={5}>
        {isLoadingCredit ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
          </Box>
        ) : creditHistory ? (
          <CreditHistory creditProfile={creditHistory} />
        ) : (
          <Alert severity="info">No credit history available for this applicant.</Alert>
        )}
        </TabPanel>

        {/* Tab 6: Transactions */}
        <TabPanel value={activeTab} index={6}>
        {isLoadingTransactions ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
          </Box>
        ) : transactionHistory?.transactions && transactionHistory.transactions.length > 0 ? (
          <TransactionList transactions={transactionHistory.transactions} />
        ) : (
          <Alert severity="info">No transaction history available for this applicant.</Alert>
        )}
        </TabPanel>

        {/* Tab 7: Audit Trail */}
        <TabPanel value={activeTab} index={7}>
        {isLoadingAudit ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
          </Box>
        ) : auditLog && auditLog.length > 0 ? (
          <AuditTrail auditLog={auditLog} />
        ) : (
          <Alert severity="info">No audit trail available for this applicant.</Alert>
        )}
        </TabPanel>
        </Box>
        </Paper>
    </Box>
  );
}
