'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  MenuItem,
  Card,
  CardContent,
  Autocomplete,
  CircularProgress,
  Alert,
  Fade,
  Divider,
} from '@mui/material';
import {
  Send,
  CheckCircle,
  Cancel,
  Person,
  AttachMoney,
  ArrowForward,
} from '@mui/icons-material';

// Mock applicants data - replace with actual API call
const mockApplicants = [
  { id: '1', name: 'John Doe', nic: '951234567V', email: 'john@example.com' },
  { id: '2', name: 'Jane Smith', nic: '901234568V', email: 'jane@example.com' },
  { id: '3', name: 'Mike Johnson', nic: '881234569V', email: 'mike@example.com' },
  { id: '4', name: 'Sarah Williams', nic: '871234570V', email: 'sarah@example.com' },
  { id: '5', name: 'David Brown', nic: '861234571V', email: 'david@example.com' },
];

const loanDurations = [
  { value: 6, label: '6 Months' },
  { value: 12, label: '12 Months (1 Year)' },
  { value: 24, label: '24 Months (2 Years)' },
  { value: 36, label: '36 Months (3 Years)' },
  { value: 48, label: '48 Months (4 Years)' },
  { value: 60, label: '60 Months (5 Years)' },
  { value: 84, label: '84 Months (7 Years)' },
  { value: 120, label: '120 Months (10 Years)' },
];

type EligibilityStatus = 'idle' | 'processing' | 'eligible' | 'not-eligible';

interface EvaluationResult {
  status: EligibilityStatus;
  rejectionReason?: string;
}

// Processing messages to cycle through
const processingMessages = [
  'Reviewing eligibility...',
  'Analyzing financial data...',
  'Processing loan evaluation...',
  'Checking credit history...',
  'Finalizing assessment...',
];

export default function EligibilityPage() {
  const [selectedApplicant, setSelectedApplicant] = useState<typeof mockApplicants[0] | null>(null);
  const [loanAmount, setLoanAmount] = useState<string>('');
  const [loanDuration, setLoanDuration] = useState<number | ''>('');
  const [evaluationStatus, setEvaluationStatus] = useState<EligibilityStatus>('idle');
  const [processingMessage, setProcessingMessage] = useState(processingMessages[0]);
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null);
  const [sentForReview, setSentForReview] = useState(false);
  const [errors, setErrors] = useState<{ applicant?: string; amount?: string; duration?: string }>({});

  // Cycle through processing messages
  useEffect(() => {
    if (evaluationStatus === 'processing') {
      let messageIndex = 0;
      const interval = setInterval(() => {
        messageIndex = (messageIndex + 1) % processingMessages.length;
        setProcessingMessage(processingMessages[messageIndex]);
      }, 1500);
      return () => clearInterval(interval);
    }
    return undefined;
  }, [evaluationStatus]);

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    if (!selectedApplicant) {
      newErrors.applicant = 'Please select an applicant';
    }
    if (!loanAmount || parseFloat(loanAmount) <= 0) {
      newErrors.amount = 'Please enter a valid loan amount';
    }
    if (!loanDuration) {
      newErrors.duration = 'Please select a loan duration';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleEvaluate = async () => {
    if (!validateForm()) return;

    setEvaluationStatus('processing');
    setEvaluationResult(null);
    setSentForReview(false);

    // Simulate API call with delay
    await new Promise((resolve) => setTimeout(resolve, 4000));

    // Mock evaluation result (randomly eligible or not)
    const isEligible = Math.random() > 0.3; // 70% chance of being eligible

    if (isEligible) {
      setEvaluationStatus('eligible');
      setEvaluationResult({ status: 'eligible' });
    } else {
      setEvaluationStatus('not-eligible');
      setEvaluationResult({
        status: 'not-eligible',
        rejectionReason: getRandomRejectionReason(),
      });
    }
  };

  const getRandomRejectionReason = (): string => {
    const reasons = [
      'Insufficient income to support the requested loan amount. The debt-to-income ratio exceeds acceptable limits.',
      'Credit history indicates multiple late payments in the past 12 months.',
      'Employment duration is below the minimum requirement of 2 years.',
      'Existing loan obligations exceed the maximum allowable debt threshold.',
      'The requested loan amount exceeds the maximum limit for the applicant\'s income bracket.',
    ];
    return reasons[Math.floor(Math.random() * reasons.length)];
  };

  const handleSendForReview = async () => {
    // Simulate sending for review
    await new Promise((resolve) => setTimeout(resolve, 500));
    setSentForReview(true);
  };

  const handleReset = () => {
    setSelectedApplicant(null);
    setLoanAmount('');
    setLoanDuration('');
    setEvaluationStatus('idle');
    setEvaluationResult(null);
    setSentForReview(false);
    setErrors({});
  };

  const formatCurrency = (value: string) => {
    const num = parseFloat(value);
    if (isNaN(num)) return '';
    return new Intl.NumberFormat('en-LK', {
      style: 'currency',
      currency: 'LKR',
      minimumFractionDigits: 0,
    }).format(num);
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Loan Eligibility Evaluation
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Select a customer and enter loan details to check eligibility
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Input Form */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
              Loan Application Details
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              {/* Customer Selection */}
              <Grid item xs={12}>
                <Autocomplete
                  options={mockApplicants}
                  getOptionLabel={(option) => `${option.name} (${option.nic})`}
                  value={selectedApplicant}
                  onChange={(_, newValue) => {
                    setSelectedApplicant(newValue);
                    if (errors.applicant) setErrors({ ...errors, applicant: undefined });
                  }}
                  disabled={evaluationStatus === 'processing'}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Select Customer"
                      error={Boolean(errors.applicant)}
                      helperText={errors.applicant || 'Search by name or NIC'}
                    />
                  )}
                  renderOption={(props, option) => (
                    <Box component="li" {...props}>
                      <Box>
                        <Typography variant="body1" fontWeight={600}>
                          {option.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          NIC: {option.nic} | {option.email}
                        </Typography>
                      </Box>
                    </Box>
                  )}
                />
              </Grid>

              {/* Loan Amount */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Loan Amount"
                  type="number"
                  value={loanAmount}
                  onChange={(e) => {
                    setLoanAmount(e.target.value);
                    if (errors.amount) setErrors({ ...errors, amount: undefined });
                  }}
                  error={Boolean(errors.amount)}
                  helperText={errors.amount || (loanAmount ? formatCurrency(loanAmount) : 'Enter the requested loan amount')}
                  disabled={evaluationStatus === 'processing'}
                  InputProps={{
                    startAdornment: <Typography sx={{ mr: 1, color: 'text.secondary' }}>LKR</Typography>,
                  }}
                />
              </Grid>

              {/* Loan Duration */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  select
                  label="Loan Duration"
                  value={loanDuration}
                  onChange={(e) => {
                    setLoanDuration(Number(e.target.value));
                    if (errors.duration) setErrors({ ...errors, duration: undefined });
                  }}
                  error={Boolean(errors.duration)}
                  helperText={errors.duration || 'Select the repayment period'}
                  disabled={evaluationStatus === 'processing'}
                >
                  {loanDurations.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              {/* Action Buttons */}
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleEvaluate}
                    disabled={evaluationStatus === 'processing'}
                    startIcon={evaluationStatus === 'processing' ? <CircularProgress size={20} color="inherit" /> : <Send />}
                    fullWidth
                  >
                    {evaluationStatus === 'processing' ? 'Evaluating...' : 'Evaluate Eligibility'}
                  </Button>
                  {evaluationStatus !== 'idle' && evaluationStatus !== 'processing' && (
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={handleReset}
                    >
                      Reset
                    </Button>
                  )}
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Results Panel */}
        <Grid item xs={12} md={6}>
          {/* Processing State */}
          {evaluationStatus === 'processing' && (
            <Fade in>
              <Card sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column', 
                justifyContent: 'center',
                alignItems: 'center',
                py: 8,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
              }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
                    <CircularProgress
                      size={100}
                      thickness={2}
                      sx={{ color: 'rgba(255,255,255,0.3)' }}
                    />
                    <CircularProgress
                      size={100}
                      thickness={2}
                      sx={{ 
                        color: 'white',
                        position: 'absolute',
                        left: 0,
                        animationDuration: '2s',
                      }}
                    />
                  </Box>
                  <Typography variant="h5" fontWeight={600} gutterBottom>
                    {processingMessage}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Please wait while we process the evaluation
                  </Typography>
                </CardContent>
              </Card>
            </Fade>
          )}

          {/* Eligible Result */}
          {evaluationStatus === 'eligible' && !sentForReview && (
            <Fade in>
              <Card sx={{ 
                height: '100%',
                background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                color: 'white',
              }}>
                <CardContent sx={{ py: 4 }}>
                  <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <CheckCircle sx={{ fontSize: 80, mb: 2 }} />
                    <Typography variant="h4" fontWeight={700} gutterBottom>
                      ELIGIBLE
                    </Typography>
                    <Typography variant="body1">
                      The applicant meets the eligibility criteria for this loan
                    </Typography>
                  </Box>

                  <Divider sx={{ bgcolor: 'rgba(255,255,255,0.3)', my: 3 }} />

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" sx={{ opacity: 0.9 }} gutterBottom>
                      Application Summary
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ opacity: 0.9 }}>Applicant:</Typography>
                          <Typography variant="body2" fontWeight={600}>{selectedApplicant?.name}</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ opacity: 0.9 }}>Loan Amount:</Typography>
                          <Typography variant="body2" fontWeight={600}>{formatCurrency(loanAmount)}</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ opacity: 0.9 }}>Duration:</Typography>
                          <Typography variant="body2" fontWeight={600}>
                            {loanDurations.find(d => d.value === loanDuration)?.label}
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </Box>

                  <Button
                    variant="contained"
                    size="large"
                    fullWidth
                    onClick={handleSendForReview}
                    endIcon={<ArrowForward />}
                    sx={{
                      bgcolor: 'white',
                      color: '#11998e',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' },
                    }}
                  >
                    Send for Manager Review
                  </Button>
                </CardContent>
              </Card>
            </Fade>
          )}

          {/* Sent for Review Confirmation */}
          {sentForReview && (
            <Fade in>
              <Card sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                py: 8,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
              }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <CheckCircle sx={{ fontSize: 80, mb: 3 }} />
                  <Typography variant="h5" fontWeight={700} gutterBottom>
                    Sent for Manager Review
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 4, opacity: 0.9 }}>
                    The application has been successfully submitted for review.
                    The manager will be notified.
                  </Typography>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={handleReset}
                    sx={{ 
                      color: 'white', 
                      borderColor: 'white',
                      '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' }
                    }}
                  >
                    Evaluate Another Application
                  </Button>
                </CardContent>
              </Card>
            </Fade>
          )}

          {/* Not Eligible Result */}
          {evaluationStatus === 'not-eligible' && (
            <Fade in>
              <Card sx={{ 
                height: '100%',
                background: 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)',
                color: 'white',
              }}>
                <CardContent sx={{ py: 4 }}>
                  <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <Cancel sx={{ fontSize: 80, mb: 2 }} />
                    <Typography variant="h4" fontWeight={700} gutterBottom>
                      NOT ELIGIBLE
                    </Typography>
                    <Typography variant="body1">
                      The applicant does not meet the eligibility criteria
                    </Typography>
                  </Box>

                  <Divider sx={{ bgcolor: 'rgba(255,255,255,0.3)', my: 3 }} />

                  <Alert 
                    severity="error" 
                    sx={{ 
                      bgcolor: 'rgba(255,255,255,0.15)', 
                      color: 'white',
                      '& .MuiAlert-icon': { color: 'white' },
                    }}
                  >
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      Reason for Rejection
                    </Typography>
                    <Typography variant="body2">
                      {evaluationResult?.rejectionReason}
                    </Typography>
                  </Alert>

                  <Box sx={{ mt: 4 }}>
                    <Typography variant="subtitle2" sx={{ opacity: 0.9 }} gutterBottom>
                      Application Details
                    </Typography>
                    <Grid container spacing={1}>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ opacity: 0.9 }}>Applicant:</Typography>
                          <Typography variant="body2" fontWeight={600}>{selectedApplicant?.name}</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ opacity: 0.9 }}>Requested Amount:</Typography>
                          <Typography variant="body2" fontWeight={600}>{formatCurrency(loanAmount)}</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </Box>

                  <Button
                    variant="outlined"
                    size="large"
                    fullWidth
                    onClick={handleReset}
                    sx={{ 
                      mt: 4,
                      color: 'white', 
                      borderColor: 'white',
                      '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' }
                    }}
                  >
                    Try Different Parameters
                  </Button>
                </CardContent>
              </Card>
            </Fade>
          )}

          {/* Initial State */}
          {evaluationStatus === 'idle' && (
            <Card sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              py: 8,
              bgcolor: 'action.hover',
            }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Box
                  sx={{
                    width: 100,
                    height: 100,
                    borderRadius: '50%',
                    bgcolor: 'action.selected',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                  }}
                >
                  <AttachMoney sx={{ fontSize: 50, color: 'text.secondary' }} />
                </Box>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Eligibility Result
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Fill in the application details and click "Evaluate Eligibility" to check if the applicant qualifies for the loan.
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
