'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
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
  Warning,
  Pending,
} from '@mui/icons-material';
import { useParams } from 'next/navigation';
import { useApplicant } from '@/hooks/usePrediction';
import {
  useLoanDetails,
  useAuditTrail,
} from '@/hooks/useApplicants';
import { useStatusUtils } from '@/hooks/useStatusUtils';
import { DetailSkeleton } from '@/components/ui/LoadingSkeleton';
import AuditTrail from '@/components/loan/AuditTrail';
import { formatCurrency } from '@/lib/utils';

export default function ApplicantDetailPage() {
  const params = useParams();
  const applicantId = params.id as string;

  const { data: applicant, isLoading: applicantLoading } = useApplicant(applicantId);
  const { data: loanDetails } = useLoanDetails(applicantId);
  const { data: auditLog, isLoading: isLoadingAudit } = useAuditTrail(applicantId);
  const statusUtils = useStatusUtils();
  
  // Wait for status data to load before rendering chips with colors
  const isStatusDataReady = !statusUtils.isLoading;

  const [activeTab, setActiveTab] = useState(0);
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
      {/* Rejection Reason (if rejected) */}
      {applicant.status === 'rejected' && (applicant as any)?.rejectionReason && (
      <Alert severity="error" sx={{ mb: 3 }}>
        <Typography variant="subtitle2" fontWeight={600}>Rejection Reason:</Typography>
        <Typography variant="body2">{(applicant as any).rejectionReason}</Typography>
      </Alert>
      )}

      {/* Main Content */}
      <Paper>
      <Tabs
        value={activeTab}
        onChange={(_e, newValue) => setActiveTab(newValue)}
        variant="fullWidth"
        sx={{
          borderBottom: 1,
          borderColor: 'divider',
          px: 2,
        }}
      >
        <Tab icon={<Person />} iconPosition="start" label="Overview" />
        <Tab icon={<History />} iconPosition="start" label="Audit Trail" />
      </Tabs>
      <Box sx={{ px: 3, py: 3 }}>
        {activeTab === 0 && (
          <>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Overview
          </Typography>
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
          </>
        )}

        {activeTab === 1 && (
          <>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Audit Trail
          </Typography>
          {isLoadingAudit ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
            </Box>
          ) : auditLog && auditLog.length > 0 ? (
            <Box
              sx={{
                maxHeight: { xs: '55vh', md: '65vh' },
                overflowY: 'auto',
                pr: 1,
              }}
            >
              <AuditTrail auditLog={auditLog} />
            </Box>
          ) : (
            <Alert severity="info">No audit trail available for this applicant.</Alert>
          )}
          </>
        )}

        </Box>
        </Paper>
    </Box>
  );
}
