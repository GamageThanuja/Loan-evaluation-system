'use client';

import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { applicantKeys } from '@/hooks/useApplicants';
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
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Skeleton,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Person,
  ArrowForward,
  Warning,
  Lightbulb,
  TrendingUp,
  TrendingDown,
  Psychology,
  Settings,
} from '@mui/icons-material';
import predictionService from '@/services/prediction';
import { applicantService } from '@/services/applicants';
import { ApplicantOption, EligibilityResult } from '@/types';

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

// Processing messages to cycle through
const processingMessages = [
  'Analyzing with Bayesian Network...',
  'Processing through TabNet model...',
  'Evaluating risk factors...',
  'Computing inference paths...',
  'Generating reasoning...',
];

export default function EligibilityPage() {
  // React Query client for cache invalidation
  const queryClient = useQueryClient();

  // Applicants state
  const [applicants, setApplicants] = useState<ApplicantOption[]>([]);
  const [loadingApplicants, setLoadingApplicants] = useState(true);

  // Form state
  const [selectedApplicant, setSelectedApplicant] = useState<ApplicantOption | null>(null);
  const [loanAmount, setLoanAmount] = useState<string>('');
  const [monthlyIncome, setMonthlyIncome] = useState<string>('');
  const [loanDuration, setLoanDuration] = useState<number | ''>('');
  const [evaluationStatus, setEvaluationStatus] = useState<EligibilityStatus>('idle');
  const [processingMessage, setProcessingMessage] = useState(processingMessages[0]);
  const [evaluationResult, setEvaluationResult] = useState<EligibilityResult | null>(null);
  const [sentForReview, setSentForReview] = useState(false);
  const [errors, setErrors] = useState<{ applicant?: string; amount?: string; duration?: string; income?: string }>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [isEditingParameters, setIsEditingParameters] = useState(false);
  const [addingToQueue, setAddingToQueue] = useState(false);

  const prefillLoanParameters = (applicant: {
    monthlyIncome?: number;
    loanAmount?: number;
    loanTerm?: number;
    loanTermMonths?: number;
  }) => {
    const nextIncome = applicant.monthlyIncome;
    const nextAmount = applicant.loanAmount;
    const nextDuration = applicant.loanTermMonths ?? applicant.loanTerm;

    setMonthlyIncome(typeof nextIncome === 'number' && nextIncome > 0 ? nextIncome.toString() : '');
    setLoanAmount(typeof nextAmount === 'number' && nextAmount > 0 ? nextAmount.toString() : '');
    setLoanDuration(typeof nextDuration === 'number' && nextDuration > 0 ? nextDuration : '');
  };
  
  // Determine if loan parameters should be locked (when applicant selected, unless editing)
  const areParametersLocked = Boolean(selectedApplicant && !isEditingParameters);

  // Load applicants from API
  useEffect(() => {
    const fetchApplicants = async () => {
      setLoadingApplicants(true);
      try {
        const response = await predictionService.getApplicants(1, 100);
        if (response.success && response.data) {
          const applicantOptions: ApplicantOption[] = response.data.items.map((app) => ({
            id: app.id,
            name: app.name || `${app.firstName || ''} ${app.lastName || ''}`.trim() || 'Unknown',
            nic: app.nic || '',
            email: app.email || '',
            monthlyIncome: app.monthlyIncome,
            loanAmount: app.loanAmount,
            loanTerm: app.loanTerm,
            loanTermMonths: app.loanTermMonths,
          }));
          setApplicants(applicantOptions);
        }
      } catch (error) {
        console.error('Failed to fetch applicants:', error);
      } finally {
        setLoadingApplicants(false);
      }
    };


    fetchApplicants();
  }, []);

  // Auto-fill loan amount and duration when applicant is selected
  useEffect(() => {
    const fetchApplicantDetails = async () => {
      if (!selectedApplicant) {
        prefillLoanParameters({});
        return;
      }

      // Immediate prefill from selected option data.
      prefillLoanParameters(selectedApplicant);

      try {
        const response = await predictionService.getApplicant(selectedApplicant.id);
        if (response.success && response.data) {
          prefillLoanParameters(response.data);
        }
      } catch (error) {
        console.error('Failed to fetch applicant details:', error);
      }
    };

    fetchApplicantDetails();
  }, [selectedApplicant]);

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
    if (!monthlyIncome || parseFloat(monthlyIncome) <= 0) {
      newErrors.income = 'Please enter a valid monthly income';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleEvaluate = async () => {
    if (!validateForm() || !selectedApplicant) return;

    setEvaluationStatus('processing');
    setEvaluationResult(null);
    setSentForReview(false);
    setApiError(null);

    try {
      const response = await predictionService.checkEligibility(
        selectedApplicant.id,
        parseFloat(loanAmount),
        loanDuration as number,
        parseFloat(monthlyIncome)
      );

      if (response.success && response.data) {
        const result = response.data;
        setEvaluationResult(result);

        if (result.eligible) {
          setEvaluationStatus('eligible');
        } else {
          setEvaluationStatus('not-eligible');
        }

        // Invalidate applicants cache to refresh the list with updated eligibility status
        queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
      } else {
        setApiError(response.error || 'Failed to check eligibility');
        setEvaluationStatus('idle');
      }
    } catch (error) {
      console.error('Eligibility check error:', error);
      setApiError('An error occurred while checking eligibility');
      setEvaluationStatus('idle');
    }
  };

  const handleSendForReview = async () => {
    if (!selectedApplicant || !evaluationResult) return;

    try {
      const response = await predictionService.sendForReview(
        selectedApplicant.id,
        evaluationResult,
        'Application eligible - submitted for manager review'
      );

      if (response.success) {
        setSentForReview(true);

        // Invalidate applicants cache to refresh the list with updated review status
        queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
      } else {
        setApiError(response.error || 'Failed to send for review');
      }
    } catch (error) {
      console.error('Send for review error:', error);
      setApiError('An error occurred while sending for review');
    }
  };

  const handleReset = () => {
    setSelectedApplicant(null);
    setLoanAmount('');
    setMonthlyIncome('');
    setLoanDuration('');
    setEvaluationStatus('idle');
    setEvaluationResult(null);
    setSentForReview(false);
    setErrors({});
    setApiError(null);
    setIsEditingParameters(false);
  };

  // Handle adding not-eligible applicant to review queue
  const handleAddToQueue = async () => {
    if (!selectedApplicant) return;
    
    setAddingToQueue(true);
    try {
      const response = await applicantService.addToQueue(selectedApplicant.id.toString());
      if (response.success) {
        // Invalidate queries to refresh data
        queryClient.invalidateQueries({ queryKey: applicantKeys.all });
        // Show success state
        setSentForReview(true);
        setEvaluationStatus('idle');
      } else {
        setApiError(response.error || 'Failed to add to queue');
      }
    } catch (error) {
      setApiError('An unexpected error occurred');
    } finally {
      setAddingToQueue(false);
    }
  };

  // Smart retry: Suggest better parameters based on rejection reasons
  const handleTryDifferentParameters = () => {
    if (!evaluationResult || !selectedApplicant) {
      handleReset();
      return;
    }

    // Get financial profile data
    const financialProfile = evaluationResult.financial_profile;
    const currentAmount = parseFloat(loanAmount);
    const currentDuration = loanDuration as number;

    // Calculate suggested values based on recommendations
    let suggestedAmount = currentAmount;
    let suggestedDuration = currentDuration;

    // Parse recommendations to extract suggestions
    const recommendations = evaluationResult.recommendations || [];

    recommendations.forEach((rec: string) => {
      // Look for loan amount suggestions (e.g., "up to LKR 6.44 Million")
      const amountMatch = rec.match(/up to LKR\s*([\d.]+)\s*(Million|K)?/i);
      if (amountMatch) {
        let amount = parseFloat(amountMatch[1]);
        if (amountMatch[2]?.toLowerCase() === 'million') {
          amount *= 1000000;
        } else if (amountMatch[2]?.toLowerCase() === 'k') {
          amount *= 1000;
        }
        suggestedAmount = Math.min(suggestedAmount, amount);
      }

      // Look for duration suggestions (e.g., "60-month", "at least 36 months")
      const durationMatch = rec.match(/(\d+)-month|at least (\d+) months|With a (\d+)-month/);
      if (durationMatch) {
        const months = parseInt(durationMatch[1] || durationMatch[2] || durationMatch[3]);
        if (months > suggestedDuration) {
          suggestedDuration = months;
        }
      }
    });

    // If payment-to-income ratio is too high, calculate an affordable amount
    if (financialProfile && financialProfile.payment_to_income_ratio > 40) {
      // Target 35% of monthly income for payment
      const targetPaymentRatio = 0.35;
      const affordableMonthlyPayment = financialProfile.monthly_income * targetPaymentRatio;

      // If duration wasn't suggested, try extending to 60 months
      if (suggestedDuration === currentDuration) {
        suggestedDuration = Math.min(60, Math.max(currentDuration, 36));
      }

      // Calculate affordable amount based on new duration
      const affordableAmount = affordableMonthlyPayment * suggestedDuration;
      suggestedAmount = Math.min(suggestedAmount, affordableAmount);
    }

    // Round suggested amount to a reasonable figure
    suggestedAmount = Math.floor(suggestedAmount / 10000) * 10000;

    // Find closest valid duration
    const validDurations = [6, 12, 24, 36, 48, 60, 84, 120];
    suggestedDuration = validDurations.reduce((prev, curr) =>
      Math.abs(curr - suggestedDuration) < Math.abs(prev - suggestedDuration) ? curr : prev
    );

    // Update form with suggested values (keep same applicant)
    setLoanAmount(suggestedAmount.toString());
    setMonthlyIncome(financialProfile?.monthly_income?.toString() || monthlyIncome);
    setLoanDuration(suggestedDuration);
    setEvaluationStatus('idle');
    setEvaluationResult(null);
    setSentForReview(false);
    setErrors({});
    setApiError(null);
    setIsEditingParameters(true); // Enable editing of parameters
  };

  const formatCurrency = (value: string | number) => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
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
       
      </Box>

      {apiError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setApiError(null)}>
          {apiError}
        </Alert>
      )}

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
                {loadingApplicants ? (
                  <Skeleton variant="rounded" height={56} />
                ) : (
                  <Autocomplete
                    options={applicants}
                    getOptionLabel={(option) => `${option.name} (${option.nic})`}
                    value={selectedApplicant}
                    onChange={(_, newValue) => {
                      setSelectedApplicant(newValue);
                      setIsEditingParameters(false); // Reset editing state when applicant changes
                      prefillLoanParameters(newValue || {});
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
                      <Box component="li" {...props} key={option.id}>
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
                    noOptionsText={
                      applicants.length === 0
                        ? "No applicants found. Please add applicants first."
                        : "No matching applicants"
                    }
                  />
                )}
              </Grid>

              {/* Monthly Income - Always editable */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Monthly Income"
                  type="number"
                  value={monthlyIncome}
                  onChange={(e) => {
                    setMonthlyIncome(e.target.value);
                    if (errors.income) setErrors({ ...errors, income: undefined });
                  }}
                  error={Boolean(errors.income)}
                  helperText={errors.income || (monthlyIncome ? formatCurrency(monthlyIncome) : 'Enter the monthly income')}
                  disabled={evaluationStatus === 'processing'}
                  InputProps={{
                    startAdornment: <Typography sx={{ mr: 1, color: 'text.secondary' }}>LKR</Typography>,
                  }}
                />
              </Grid>

              {/* Loan Amount - Locked when applicant selected, unless editing parameters */}
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
                  helperText={
                    areParametersLocked 
                      ? 'Amount locked - use "Try Different Parameters" to edit'
                      : errors.amount || (loanAmount ? formatCurrency(loanAmount) : 'Enter the requested loan amount')
                  }
                  disabled={evaluationStatus === 'processing' || areParametersLocked}
                  InputProps={{
                    startAdornment: <Typography sx={{ mr: 1, color: 'text.secondary' }}>LKR</Typography>,
                  }}
                  sx={areParametersLocked ? { '& .MuiInputBase-input': { color: 'text.secondary' } } : {}}
                />
              </Grid>

              {/* Loan Duration - Locked when applicant selected, unless editing parameters */}
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
                  helperText={
                    areParametersLocked 
                      ? 'Duration locked - use "Try Different Parameters" to edit'
                      : errors.duration || 'Select the repayment period'
                  }
                  disabled={evaluationStatus === 'processing' || areParametersLocked}
                  sx={areParametersLocked ? { '& .MuiInputBase-input': { color: 'text.secondary' } } : {}}
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
                <Box sx={{ display: 'flex', gap: 2, flexDirection: 'column' }}>
                  {/* Show "Try Different Parameters" button when parameters are locked */}
                  {areParametersLocked && !isEditingParameters && (
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={handleTryDifferentParameters}
                      fullWidth
                    >
                      Try Different Parameters
                    </Button>
                  )}
                  
                  {/* Main action buttons */}
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handleEvaluate}
                      disabled={evaluationStatus === 'processing' || !selectedApplicant}
                      startIcon={evaluationStatus === 'processing' ? <CircularProgress size={20} color="inherit" /> : <Psychology />}
                      fullWidth
                    >
                      {evaluationStatus === 'processing' ? 'Analyzing...' : 'Evaluate Eligibility'}
                    </Button>
                    {(evaluationStatus !== 'idle' && evaluationStatus !== 'processing') || isEditingParameters ? (
                      <Button
                        variant="outlined"
                        size="large"
                        onClick={handleReset}
                      >
                        Reset
                      </Button>
                    ) : null}
                  </Box>
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
                border: '1px solid',
                borderColor: 'primary.main',
                bgcolor: 'background.paper',
              }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
                    <CircularProgress
                      size={100}
                      thickness={2}
                      sx={{ color: 'primary.light' }}
                    />
                    <CircularProgress
                      size={100}
                      thickness={2}
                      sx={{
                        color: 'primary.main',
                        position: 'absolute',
                        left: 0,
                        animationDuration: '2s',
                      }}
                    />
                  </Box>
                  <Typography variant="h5" fontWeight={600} color="primary.main" gutterBottom>
                    {processingMessage}
                  </Typography>
                </CardContent>
              </Card>
            </Fade>
          )}

          {/* Eligible Result */}
          {evaluationStatus === 'eligible' && evaluationResult && !sentForReview && (
            <Fade in>
              <Card sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'success.main',
                bgcolor: 'background.paper',
              }}>
                <CardContent sx={{ py: 4 }}>
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Box sx={{ 
                      width: 64, 
                      height: 64, 
                      borderRadius: '50%', 
                      bgcolor: 'success.light', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2
                    }}>
                      <CheckCircle sx={{ fontSize: 36, color: 'success.main' }} />
                    </Box>
                    <Typography variant="h5" fontWeight={700} color="success.main" gutterBottom>
                      ELIGIBLE
                    </Typography>
                    <Chip
                      label={evaluationResult.risk_level}
                      color="success"
                      variant="outlined"
                      size="small"
                    />
                  </Box>

                  {/* AI Reasoning */}
                  <Box sx={{ bgcolor: 'action.hover', borderRadius: 2, p: 2, mb: 3 }}>
                    <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary' }}>
                      <Psychology sx={{ mr: 1, fontSize: 18 }} />
                      AI Reasoning
                    </Typography>
                    <Typography variant="body2" color="text.primary">
                      {evaluationResult.summary_explanation}
                    </Typography>
                  </Box>

                  {/* Protective Factors */}
                  {evaluationResult.protective_factors && evaluationResult.protective_factors.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary' }}>
                        <TrendingDown sx={{ mr: 1, fontSize: 18, color: 'success.main' }} />
                        Positive Factors
                      </Typography>
                      <List dense sx={{ py: 0 }}>
                        {evaluationResult.protective_factors.slice(0, 3).map((factor, idx) => (
                          <ListItem key={idx} sx={{ py: 0.5, px: 0 }}>
                            <ListItemIcon sx={{ minWidth: 28 }}>
                              <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                            </ListItemIcon>
                            <ListItemText
                              primary={factor.explanation}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Recommendations */}
                  {evaluationResult.recommendations && evaluationResult.recommendations.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary' }}>
                        <Lightbulb sx={{ mr: 1, fontSize: 18, color: 'warning.main' }} />
                        Recommendations
                      </Typography>
                      <List dense sx={{ py: 0 }}>
                        {evaluationResult.recommendations.slice(0, 2).map((rec, idx) => (
                          <ListItem key={idx} sx={{ py: 0.5, px: 0 }}>
                            <ListItemText
                              primary={`• ${rec}`}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  <Divider sx={{ my: 2 }} />

                  {/* Summary */}
                  <Grid container spacing={1} sx={{ mb: 3 }}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Risk Score</Typography>
                      <Typography variant="h6" fontWeight={600}>
                        {(evaluationResult.risk_score * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Confidence</Typography>
                      <Typography variant="h6" fontWeight={600}>
                        {(evaluationResult.confidence_score * 100).toFixed(0)}%
                      </Typography>
                    </Grid>
                  </Grid>

                  <Button
                    variant="contained"
                    color="success"
                    size="large"
                    fullWidth
                    onClick={handleSendForReview}
                    endIcon={<ArrowForward />}
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
                border: '1px solid',
                borderColor: 'primary.main',
                bgcolor: 'background.paper',
              }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ 
                    width: 80, 
                    height: 80, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.light', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3
                  }}>
                    <CheckCircle sx={{ fontSize: 48, color: 'primary.main' }} />
                  </Box>
                  <Typography variant="h5" fontWeight={700} color="primary.main" gutterBottom>
                    Sent for Manager Review
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                    The application has been successfully submitted for review.
                    The manager will be notified.
                  </Typography>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={handleReset}
                  >
                    Evaluate Another Application
                  </Button>
                </CardContent>
              </Card>
            </Fade>
          )}

          {/* Not Eligible Result */}
          {evaluationStatus === 'not-eligible' && evaluationResult && (
            <Fade in>
              <Card sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'error.main',
                bgcolor: 'background.paper',
              }}>
                <CardContent sx={{ py: 4 }}>
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Box sx={{ 
                      width: 64, 
                      height: 64, 
                      borderRadius: '50%', 
                      bgcolor: 'error.light', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2
                    }}>
                      <Cancel sx={{ fontSize: 36, color: 'error.main' }} />
                    </Box>
                    <Typography variant="h5" fontWeight={700} color="error.main" gutterBottom>
                      NOT ELIGIBLE
                    </Typography>
                    <Chip
                      label={evaluationResult.risk_level}
                      color="error"
                      variant="outlined"
                      size="small"
                    />
                  </Box>

                  {/* AI Reasoning */}
                  <Box sx={{ bgcolor: 'action.hover', borderRadius: 2, p: 2, mb: 3 }}>
                    <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary' }}>
                      <Psychology sx={{ mr: 1, fontSize: 18 }} />
                      AI Reasoning
                    </Typography>
                    <Typography variant="body2" color="text.primary">
                      {evaluationResult.summary_explanation}
                    </Typography>
                  </Box>

                  {/* Risk Factors */}
                  {evaluationResult.risk_factors && evaluationResult.risk_factors.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary' }}>
                        <TrendingUp sx={{ mr: 1, fontSize: 18, color: 'error.main' }} />
                        Risk Factors
                      </Typography>
                      <List dense sx={{ py: 0 }}>
                        {evaluationResult.risk_factors.slice(0, 4).map((factor, idx) => (
                          <ListItem key={idx} sx={{ py: 0.5, px: 0 }}>
                            <ListItemIcon sx={{ minWidth: 28 }}>
                              <Warning sx={{ fontSize: 16, color: 'warning.main' }} />
                            </ListItemIcon>
                            <ListItemText
                              primary={factor.explanation}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Recommendations */}
                  {evaluationResult.recommendations && evaluationResult.recommendations.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary' }}>
                        <Lightbulb sx={{ mr: 1, fontSize: 18, color: 'warning.main' }} />
                        Recommendations
                      </Typography>
                      <List dense sx={{ py: 0 }}>
                        {evaluationResult.recommendations.map((rec, idx) => (
                          <ListItem key={idx} sx={{ py: 0.5, px: 0 }}>
                            <ListItemText
                              primary={`• ${rec}`}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  <Divider sx={{ my: 2 }} />

                  {/* Summary */}
                  <Grid container spacing={1} sx={{ mb: 3 }}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Risk Score</Typography>
                      <Typography variant="h6" fontWeight={600}>
                        {(evaluationResult.risk_score * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Confidence</Typography>
                      <Typography variant="h6" fontWeight={600}>
                        {(evaluationResult.confidence_score * 100).toFixed(0)}%
                      </Typography>
                    </Grid>
                  </Grid>

                  <Button
                    variant="contained"
                    color="warning"
                    size="large"
                    fullWidth
                    onClick={handleAddToQueue}
                    disabled={addingToQueue}
                    startIcon={addingToQueue ? <CircularProgress size={20} color="inherit" /> : <ArrowForward />}
                  >
                    {addingToQueue ? 'Adding to Queue...' : 'Add to Queue'}
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
                  <Psychology sx={{ fontSize: 50, color: 'text.secondary' }} />
                </Box>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  AI-Powered Eligibility Check
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
