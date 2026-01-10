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
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import { Save, ArrowBack, ArrowForward, Check, Person, ContactPhone, AttachMoney } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { z } from 'zod';

// Simple validation schema for new applicant
const newApplicantSchema = z.object({
  // Personal Information
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  nic: z.string().min(9, 'NIC must be valid').max(12, 'NIC must be valid'),
  dateOfBirth: z.string().refine(
    (date) => {
      if (!date) return false;
      const age = new Date().getFullYear() - new Date(date).getFullYear();
      return age >= 18 && age <= 100;
    },
    { message: 'Applicant must be between 18 and 100 years old' }
  ),
  gender: z.enum(['M', 'F', 'Other']),
  maritalStatus: z.enum(['Single', 'Married', 'Divorced', 'Widowed']),
  dependents: z.number().min(0).max(20),

  // Contact Details
  email: z.string().email('Invalid email address'),
  phone: z.string().regex(/^\+?[\d\s-()]+$/, 'Invalid phone number'),
  address: z.string().min(5, 'Address is required'),
  city: z.string().min(2, 'City is required'),
  district: z.string().min(2, 'District is required'),
  postalCode: z.string().min(4, 'Postal code is required'),

  // Basic Financial Details
  employmentType: z.enum(['Employed', 'Self-Employed', 'Unemployed', 'Student', 'Retired']),
  employerName: z.string().optional(),
  jobTitle: z.string().optional(),
  employmentLength: z.number().min(0).max(50),
  monthlyIncome: z.number().min(0, 'Monthly income must be positive'),
  otherIncome: z.number().min(0).optional(),
  bankName: z.string().min(2, 'Bank name is required'),
  accountNumber: z.string().min(5, 'Account number is required'),
});

type NewApplicantFormData = z.infer<typeof newApplicantSchema>;

const steps = ['Personal Information', 'Contact Details', 'Financial Details'];

export default function NewApplicantPage() {
  const router = useRouter();
  const [activeStep, setActiveStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [formData, setFormData] = useState<NewApplicantFormData>({
    firstName: '',
    lastName: '',
    nic: '',
    dateOfBirth: '',
    gender: 'M',
    maritalStatus: 'Single',
    dependents: 0,
    email: '',
    phone: '',
    address: '',
    city: '',
    district: '',
    postalCode: '',
    employmentType: 'Employed',
    employerName: '',
    jobTitle: '',
    employmentLength: 0,
    monthlyIncome: 0,
    otherIncome: 0,
    bankName: '',
    accountNumber: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof NewApplicantFormData, string>>>({});

  const handleChange = (field: keyof NewApplicantFormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.type === 'number' 
      ? (event.target.value === '' ? 0 : parseFloat(event.target.value))
      : event.target.value;
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const validateStep = (step: number): boolean => {
    const stepFields: Record<number, (keyof NewApplicantFormData)[]> = {
      0: ['firstName', 'lastName', 'nic', 'dateOfBirth', 'gender', 'maritalStatus', 'dependents'],
      1: ['email', 'phone', 'address', 'city', 'district', 'postalCode'],
      2: ['employmentType', 'employmentLength', 'monthlyIncome', 'bankName', 'accountNumber'],
    };

    const fieldsToValidate = stepFields[step];
    const partialData: Partial<NewApplicantFormData> = {};
    fieldsToValidate.forEach((field) => {
      (partialData as any)[field] = formData[field];
    });

    // Create partial schema for validation
    const result = newApplicantSchema.partial().safeParse(partialData);
    
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof NewApplicantFormData, string>> = {};
      result.error.errors.forEach((err) => {
        const field = err.path[0] as keyof NewApplicantFormData;
        if (fieldsToValidate.includes(field)) {
          fieldErrors[field] = err.message;
        }
      });
      setErrors(fieldErrors);
      return Object.keys(fieldErrors).length === 0;
    }

    // Additional required field checks
    let hasErrors = false;
    const newErrors: Partial<Record<keyof NewApplicantFormData, string>> = {};

    fieldsToValidate.forEach((field) => {
      const value = formData[field];
      if (field !== 'employerName' && field !== 'jobTitle' && field !== 'otherIncome') {
        if (value === '' || value === undefined || value === null) {
          newErrors[field] = 'This field is required';
          hasErrors = true;
        }
      }
    });

    if (hasErrors) {
      setErrors(newErrors);
      return false;
    }

    setErrors({});
    return true;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitError(null);

    if (!validateStep(activeStep)) {
      return;
    }

    // Full validation
    const result = newApplicantSchema.safeParse(formData);
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof NewApplicantFormData, string>> = {};
      result.error.errors.forEach((err) => {
        const field = err.path[0] as keyof NewApplicantFormData;
        fieldErrors[field] = err.message;
      });
      setErrors(fieldErrors);
      setSubmitError('Please fix the validation errors before submitting.');
      return;
    }

    setIsSubmitting(true);

    try {
      // TODO: Replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 1500));
      
      // Simulate successful submission
      setSubmitSuccess(true);
      
      // Redirect after short delay
      setTimeout(() => {
        router.push('/applicant');
      }, 2000);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to create applicant');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Person color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Personal Information
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Enter the applicant's personal details
              </Typography>
            </Grid>
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
                label="NIC Number"
                value={formData.nic}
                onChange={handleChange('nic')}
                error={Boolean(errors.nic)}
                helperText={errors.nic || 'E.g., 951234567V or 199512345678'}
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
            <Grid item xs={12} sm={4}>
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
            <Grid item xs={12} sm={4}>
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
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                required
                label="Number of Dependents"
                type="number"
                value={formData.dependents}
                onChange={handleChange('dependents')}
                error={Boolean(errors.dependents)}
                helperText={errors.dependents}
                inputProps={{ min: 0, max: 20 }}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <ContactPhone color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Contact Details
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Enter the applicant's contact information
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Email Address"
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
                label="Phone Number"
                value={formData.phone}
                onChange={handleChange('phone')}
                error={Boolean(errors.phone)}
                helperText={errors.phone || 'E.g., +94 77 123 4567'}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Street Address"
                value={formData.address}
                onChange={handleChange('address')}
                error={Boolean(errors.address)}
                helperText={errors.address}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                required
                label="City"
                value={formData.city}
                onChange={handleChange('city')}
                error={Boolean(errors.city)}
                helperText={errors.city}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                required
                label="District"
                value={formData.district}
                onChange={handleChange('district')}
                error={Boolean(errors.district)}
                helperText={errors.district}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                required
                label="Postal Code"
                value={formData.postalCode}
                onChange={handleChange('postalCode')}
                error={Boolean(errors.postalCode)}
                helperText={errors.postalCode}
              />
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AttachMoney color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Basic Financial Details
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Enter the applicant's employment and financial information
              </Typography>
            </Grid>
            
            {/* Employment Section */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight={600} color="text.secondary" gutterBottom>
                Employment Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
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
                inputProps={{ min: 0, max: 50 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Employer Name"
                value={formData.employerName}
                onChange={handleChange('employerName')}
                helperText="Optional"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Job Title"
                value={formData.jobTitle}
                onChange={handleChange('jobTitle')}
                helperText="Optional"
              />
            </Grid>

            {/* Income Section */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight={600} color="text.secondary" gutterBottom sx={{ mt: 2 }}>
                Income & Banking
              </Typography>
              <Divider sx={{ mb: 2 }} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Monthly Income"
                type="number"
                value={formData.monthlyIncome}
                onChange={handleChange('monthlyIncome')}
                error={Boolean(errors.monthlyIncome)}
                helperText={errors.monthlyIncome}
                InputProps={{ startAdornment: <Typography sx={{ mr: 1 }}>LKR</Typography> }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Other Monthly Income"
                type="number"
                value={formData.otherIncome}
                onChange={handleChange('otherIncome')}
                helperText="Optional (rental, investments, etc.)"
                InputProps={{ startAdornment: <Typography sx={{ mr: 1 }}>LKR</Typography> }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Bank Name"
                value={formData.bankName}
                onChange={handleChange('bankName')}
                error={Boolean(errors.bankName)}
                helperText={errors.bankName}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Account Number"
                value={formData.accountNumber}
                onChange={handleChange('accountNumber')}
                error={Boolean(errors.accountNumber)}
                helperText={errors.accountNumber}
              />
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  if (submitSuccess) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Card sx={{ maxWidth: 500, mx: 'auto' }}>
          <CardContent sx={{ py: 6 }}>
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                bgcolor: 'success.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 3,
              }}
            >
              <Check sx={{ fontSize: 40, color: 'success.main' }} />
            </Box>
            <Typography variant="h5" fontWeight={700} gutterBottom>
              Application Submitted!
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              The applicant has been successfully registered. You will be redirected to the applicants list.
            </Typography>
            <CircularProgress size={24} />
          </CardContent>
        </Card>
      </Box>
    );
  }

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
          Register a new loan applicant by entering their information below
        </Typography>
      </Box>

      {submitError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setSubmitError(null)}>
          {submitError}
        </Alert>
      )}

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Form Content */}
      <Paper component="form" onSubmit={handleSubmit} sx={{ p: 4 }}>
        {renderStepContent(activeStep)}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4, pt: 3, borderTop: 1, borderColor: 'divider' }}>
          <Button
            onClick={handleBack}
            disabled={activeStep === 0 || isSubmitting}
            startIcon={<ArrowBack />}
          >
            Back
          </Button>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {activeStep === steps.length - 1 ? (
              <Button
                type="submit"
                variant="contained"
                disabled={isSubmitting}
                startIcon={isSubmitting ? <CircularProgress size={20} /> : <Save />}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Application'}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
                endIcon={<ArrowForward />}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}
