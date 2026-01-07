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
} from '@mui/material';
import {
  ArrowBack,
  CheckCircle,
  Cancel,
  Person,
  AttachMoney,
} from '@mui/icons-material';
import { useRouter, useParams } from 'next/navigation';
import { useApplicant, usePrediction, useApproveLoan, useRejectLoan } from '@/hooks/usePrediction';
import { useAuth } from '@/hooks/useAuth';
import { DetailSkeleton } from '@/components/ui/LoadingSkeleton';
import RiskGauge from '@/components/prediction/RiskGauge';
import ShapExplanation from '@/components/prediction/ShapExplanation';
import BayesianNetworkDisplay from '@/components/prediction/BayesianNetworkDisplay';
import BusinessRules from '@/components/prediction/BusinessRules';
import { formatCurrency, getRiskLevel } from '@/lib/utils';

export default function ApplicantDetailPage() {
  const router = useRouter();
  const params = useParams();
  const applicantId = params.id as string;
  const { isManager } = useAuth();
  
  const { data: applicant, isLoading: applicantLoading } = useApplicant(applicantId);
  const { data: prediction, isLoading: predictionLoading } = usePrediction(applicantId);
  const approveLoan = useApproveLoan();
  const rejectLoan = useRejectLoan();
  
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  if (applicantLoading || predictionLoading) {
    return <DetailSkeleton />;
  }

  if (!applicant || !prediction) {
    return (
      <Alert severity="error">
        Applicant or prediction not found
      </Alert>
    );
  }

  const riskLevel = getRiskLevel(prediction.riskScore);

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
      <Box sx={{ mb: 3 }}>
        <Button startIcon={<ArrowBack />} onClick={() => router.back()} sx={{ mb: 2 }}>
          Back
        </Button>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h4" gutterBottom fontWeight={700}>
              {applicant.firstName} {applicant.lastName}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Application ID: {applicant.id}
            </Typography>
          </Box>
          <Chip
            label={applicant.status.toUpperCase()}
            color={
              applicant.status === 'approved'
                ? 'success'
                : applicant.status === 'rejected'
                ? 'error'
                : 'warning'
            }
          />
        </Box>
      </Box>

      {/* Decision Banner */}
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

      <Grid container spacing={3}>
        {/* Applicant Info */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Person color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Personal Information
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Email
                  </Typography>
                  <Typography variant="body2">{applicant.email}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Phone
                  </Typography>
                  <Typography variant="body2">{applicant.phone}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Age
                  </Typography>
                  <Typography variant="body2">{applicant.age} years</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Gender
                  </Typography>
                  <Typography variant="body2">
                    {applicant.gender === 'M' ? 'Male' : applicant.gender === 'F' ? 'Female' : 'Other'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Marital Status
                  </Typography>
                  <Typography variant="body2">{applicant.maritalStatus}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Dependents
                  </Typography>
                  <Typography variant="body2">{applicant.dependents}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Financial Info */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AttachMoney color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Financial Information
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Annual Income
                  </Typography>
                  <Typography variant="body2">{formatCurrency(applicant.annualIncome)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Credit Score
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {applicant.creditScore}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Employment Type
                  </Typography>
                  <Typography variant="body2">{applicant.employmentType}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Employment Length
                  </Typography>
                  <Typography variant="body2">{applicant.employmentLength} years</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Loan Amount
                  </Typography>
                  <Typography variant="body2">{formatCurrency(applicant.loanAmount)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Loan Purpose
                  </Typography>
                  <Typography variant="body2">{applicant.loanPurpose}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Gauge */}
        <Grid item xs={12} md={4}>
          <RiskGauge
            riskScore={prediction.riskScore}
            riskLevel={riskLevel}
            confidence={prediction.confidence}
          />
        </Grid>

        {/* SHAP Explanation */}
        <Grid item xs={12} md={8}>
          <ShapExplanation explanation={prediction.shapExplanation} />
        </Grid>

        {/* Bayesian Network */}
        <Grid item xs={12}>
          <BayesianNetworkDisplay network={prediction.bayesianNetwork} />
        </Grid>

        {/* Business Rules */}
        <Grid item xs={12}>
          <BusinessRules rules={prediction.businessRules} />
        </Grid>

        {/* Manager Actions */}
        {isManager() && applicant.status === 'pending' && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  Loan Decision
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  As a Bank Manager, you can approve or reject this loan application.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<CheckCircle />}
                    onClick={() => setApproveDialogOpen(true)}
                    disabled={approveLoan.isPending}
                  >
                    Approve Loan
                  </Button>
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<Cancel />}
                    onClick={() => setRejectDialogOpen(true)}
                    disabled={rejectLoan.isPending}
                  >
                    Reject Loan
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Approve Dialog */}
      <Dialog open={approveDialogOpen} onClose={() => setApproveDialogOpen(false)}>
        <DialogTitle>Approve Loan Application</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to approve this loan application for{' '}
            <strong>
              {applicant.firstName} {applicant.lastName}
            </strong>
            ?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApproveDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleApprove}
            variant="contained"
            color="success"
            disabled={approveLoan.isPending}
          >
            {approveLoan.isPending ? 'Approving...' : 'Approve'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)}>
        <DialogTitle>Reject Loan Application</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Please provide a reason for rejecting this application:
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Enter rejection reason..."
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleReject}
            variant="contained"
            color="error"
            disabled={rejectLoan.isPending || !rejectReason.trim()}
          >
            {rejectLoan.isPending ? 'Rejecting...' : 'Reject'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
