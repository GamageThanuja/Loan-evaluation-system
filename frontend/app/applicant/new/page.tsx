'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save, ArrowBack } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useCreateApplicant } from '@/hooks/usePrediction';
import { applicantSchema, type ApplicantFormData } from '@/lib/validation';

export default function NewApplicantPage() {
  const router = useRouter();
  const createApplicant = useCreateApplicant();
  
  const [formData, setFormData] = useState<ApplicantFormData>({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    gender: 'M',
    maritalStatus: 'Single',
    dependents: 0,
    annualIncome: 0,
    employmentType: 'Employed',
    employmentLength: 0,
    creditScore: 650,
    loanAmount: 0,
    loanPurpose: 'Personal',
    loanTerm: 36,
    address: '',
    city: '',
    state: '',
    zipCode: '',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof ApplicantFormData, string>>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleChange = (field: keyof ApplicantFormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.type === 'number' ? parseFloat(event.target.value) : event.target.value;
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitError(null);
    setErrors({});

    const result = applicantSchema.safeParse(formData);
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof ApplicantFormData, string>> = {};
      result.error.errors.forEach((err) => {
        const field = err.path[0] as keyof ApplicantFormData;
        fieldErrors[field] = err.message;
      });
      setErrors(fieldErrors);
      return;
    }

    try {
      const response = await createApplicant.mutateAsync(formData);
      router.push(`/applicant/${response.id}`);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to create applicant');
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Button startIcon={<ArrowBack />} onClick={() => router.back()} sx={{ mb: 2 }}>
          Back
        </Button>
        <Typography variant="h4" gutterBottom fontWeight={700}>
          New Applicant
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter applicant information to create a new loan application
        </Typography>
      </Box>

      {submitError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {submitError}
        </Alert>
      )}

      <Paper component="form" onSubmit={handleSubmit} sx={{ p: 3 }}>
        {/* Personal Information */}
        <Typography variant="h6" gutterBottom fontWeight={600}>
          Personal Information
        </Typography>
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="First Name"
              value={formData.firstName}
              onChange={handleChange('firstName')}
              error={Boolean(errors.firstName)}
              helperText={errors.firstName}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Last Name"
              value={formData.lastName}
              onChange={handleChange('lastName')}
              error={Boolean(errors.lastName)}
              helperText={errors.lastName}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Email"
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              error={Boolean(errors.email)}
              helperText={errors.email}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Phone"
              value={formData.phone}
              onChange={handleChange('phone')}
              error={Boolean(errors.phone)}
              helperText={errors.phone}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Date of Birth"
              type="date"
              value={formData.dateOfBirth}
              onChange={handleChange('dateOfBirth')}
              error={Boolean(errors.dateOfBirth)}
              helperText={errors.dateOfBirth}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              select
              label="Gender"
              value={formData.gender}
              onChange={handleChange('gender')}
              error={Boolean(errors.gender)}
              helperText={errors.gender}
            >
              <MenuItem value="M">Male</MenuItem>
              <MenuItem value="F">Female</MenuItem>
              <MenuItem value="Other">Other</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              select
              label="Marital Status"
              value={formData.maritalStatus}
              onChange={handleChange('maritalStatus')}
              error={Boolean(errors.maritalStatus)}
              helperText={errors.maritalStatus}
            >
              <MenuItem value="Single">Single</MenuItem>
              <MenuItem value="Married">Married</MenuItem>
              <MenuItem value="Divorced">Divorced</MenuItem>
              <MenuItem value="Widowed">Widowed</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Dependents"
              type="number"
              value={formData.dependents}
              onChange={handleChange('dependents')}
              error={Boolean(errors.dependents)}
              helperText={errors.dependents}
            />
          </Grid>
        </Grid>

        {/* Financial Information */}
        <Typography variant="h6" gutterBottom fontWeight={600}>
          Financial Information
        </Typography>
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Annual Income"
              type="number"
              value={formData.annualIncome}
              onChange={handleChange('annualIncome')}
              error={Boolean(errors.annualIncome)}
              helperText={errors.annualIncome}
              InputProps={{ startAdornment: '$' }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              select
              label="Employment Type"
              value={formData.employmentType}
              onChange={handleChange('employmentType')}
              error={Boolean(errors.employmentType)}
              helperText={errors.employmentType}
            >
              <MenuItem value="Employed">Employed</MenuItem>
              <MenuItem value="Self-Employed">Self-Employed</MenuItem>
              <MenuItem value="Unemployed">Unemployed</MenuItem>
              <MenuItem value="Student">Student</MenuItem>
              <MenuItem value="Retired">Retired</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Employment Length (years)"
              type="number"
              value={formData.employmentLength}
              onChange={handleChange('employmentLength')}
              error={Boolean(errors.employmentLength)}
              helperText={errors.employmentLength}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Credit Score"
              type="number"
              value={formData.creditScore}
              onChange={handleChange('creditScore')}
              error={Boolean(errors.creditScore)}
              helperText={errors.creditScore}
            />
          </Grid>
        </Grid>

        {/* Loan Information */}
        <Typography variant="h6" gutterBottom fontWeight={600}>
          Loan Information
        </Typography>
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Loan Amount"
              type="number"
              value={formData.loanAmount}
              onChange={handleChange('loanAmount')}
              error={Boolean(errors.loanAmount)}
              helperText={errors.loanAmount}
              InputProps={{ startAdornment: '$' }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              select
              label="Loan Purpose"
              value={formData.loanPurpose}
              onChange={handleChange('loanPurpose')}
              error={Boolean(errors.loanPurpose)}
              helperText={errors.loanPurpose}
            >
              <MenuItem value="Home">Home</MenuItem>
              <MenuItem value="Auto">Auto</MenuItem>
              <MenuItem value="Personal">Personal</MenuItem>
              <MenuItem value="Education">Education</MenuItem>
              <MenuItem value="Business">Business</MenuItem>
              <MenuItem value="Other">Other</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Loan Term (months)"
              type="number"
              value={formData.loanTerm}
              onChange={handleChange('loanTerm')}
              error={Boolean(errors.loanTerm)}
              helperText={errors.loanTerm}
            />
          </Grid>
        </Grid>

        {/* Address (Optional) */}
        <Typography variant="h6" gutterBottom fontWeight={600}>
          Address (Optional)
        </Typography>
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Street Address"
              value={formData.address}
              onChange={handleChange('address')}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="City"
              value={formData.city}
              onChange={handleChange('city')}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="State"
              value={formData.state}
              onChange={handleChange('state')}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="ZIP Code"
              value={formData.zipCode}
              onChange={handleChange('zipCode')}
              error={Boolean(errors.zipCode)}
              helperText={errors.zipCode}
            />
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={() => router.back()}
            disabled={createApplicant.isPending}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            startIcon={createApplicant.isPending ? <CircularProgress size={20} /> : <Save />}
            disabled={createApplicant.isPending}
          >
            {createApplicant.isPending ? 'Creating...' : 'Create & Predict'}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
