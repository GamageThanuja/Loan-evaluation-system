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
  Autocomplete,
} from '@mui/material';
import { Save, ArrowForward, Check, Person, ContactPhone, AttachMoney, AccountBalance } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { z } from 'zod';

// Sri Lankan Districts
const SRI_LANKA_DISTRICTS = [
  'Colombo', 'Gampaha', 'Kalutara', 'Kandy', 'Matale', 'Nuwara Eliya',
  'Galle', 'Matara', 'Hambantota', 'Jaffna', 'Kilinochchi', 'Mannar',
  'Vavuniya', 'Mullaitivu', 'Batticaloa', 'Ampara', 'Trincomalee',
  'Kurunegala', 'Puttalam', 'Anuradhapura', 'Polonnaruwa', 'Badulla',
  'Monaragala', 'Ratnapura', 'Kegalle'
];

const SRI_LANKA_CITIES: Record<string, string[]> = {
  'Colombo': ['Colombo', 'Dehiwala-Mount Lavinia', 'Moratuwa', 'Kotte', 'Kolonnawa', 'Maharagama', 'Nugegoda', 'Boralesgamuwa', 'Pannipitiya', 'Piliyandala', 'Homagama', 'Kaduwela'],
  'Gampaha': ['Negombo', 'Gampaha', 'Kelaniya', 'Wattala', 'Ja-Ela', 'Kandana', 'Ragama', 'Minuwangoda', 'Divulapitiya', 'Kiribathgoda'],
  'Kalutara': ['Kalutara', 'Panadura', 'Beruwala', 'Horana', 'Matugama', 'Wadduwa', 'Bandaragama', 'Aluthgama'],
  'Kandy': ['Kandy', 'Peradeniya', 'Katugastota', 'Gampola', 'Nawalapitiya', 'Kadugannawa', 'Kundasale', 'Digana'],
  'Matale': ['Matale', 'Dambulla', 'Sigiriya', 'Galewela', 'Ukuwela', 'Rattota'],
  'Nuwara Eliya': ['Nuwara Eliya', 'Hatton', 'Talawakelle', 'Bandarawela', 'Haputale', 'Welimada'],
  'Galle': ['Galle', 'Hikkaduwa', 'Ambalangoda', 'Elpitiya', 'Karapitiya', 'Unawatuna', 'Koggala'],
  'Matara': ['Matara', 'Weligama', 'Dikwella', 'Akuressa', 'Deniyaya', 'Hakmana'],
  'Hambantota': ['Hambantota', 'Tangalle', 'Tissamaharama', 'Ambalantota', 'Beliatta'],
  'Jaffna': ['Jaffna', 'Chavakachcheri', 'Point Pedro', 'Nallur', 'Kodikamam'],
  'Kilinochchi': ['Kilinochchi', 'Pallai', 'Paranthan'],
  'Mannar': ['Mannar', 'Thalaimannar', 'Nanattan'],
  'Vavuniya': ['Vavuniya', 'Nedunkeni', 'Cheddikulam'],
  'Mullaitivu': ['Mullaitivu', 'Oddusuddan', 'Puthukkudiyiruppu'],
  'Batticaloa': ['Batticaloa', 'Kattankudy', 'Eravur', 'Kaluwanchikudy', 'Valachchenai'],
  'Ampara': ['Ampara', 'Kalmunai', 'Sainthamaruthu', 'Akkaraipattu', 'Sammanthurai'],
  'Trincomalee': ['Trincomalee', 'Kinniya', 'Kantale', 'Muttur', 'China Bay'],
  'Kurunegala': ['Kurunegala', 'Kuliyapitiya', 'Narammala', 'Polgahawela', 'Pannala', 'Mawathagama'],
  'Puttalam': ['Puttalam', 'Chilaw', 'Wennappuwa', 'Nattandiya', 'Dankotuwa', 'Marawila'],
  'Anuradhapura': ['Anuradhapura', 'Mihintale', 'Medawachchiya', 'Kekirawa', 'Tambuttegama'],
  'Polonnaruwa': ['Polonnaruwa', 'Kaduruwela', 'Medirigiriya', 'Hingurakgoda'],
  'Badulla': ['Badulla', 'Bandarawela', 'Haputale', 'Ella', 'Mahiyanganaya', 'Passara'],
  'Monaragala': ['Monaragala', 'Wellawaya', 'Bibile', 'Buttala', 'Kataragama'],
  'Ratnapura': ['Ratnapura', 'Embilipitiya', 'Balangoda', 'Pelmadulla', 'Eheliyagoda', 'Kuruwita'],
  'Kegalle': ['Kegalle', 'Mawanella', 'Warakapola', 'Rambukkana', 'Ruwanwella', 'Deraniyagala']
};

// Common job titles in Sri Lanka
const JOB_TITLES = [
  'Software Engineer', 'Senior Software Engineer', 'Software Developer',
  'Accountant', 'Senior Accountant', 'Financial Analyst',
  'Manager', 'Assistant Manager', 'General Manager', 'Project Manager',
  'Executive', 'Senior Executive', 'Chief Executive Officer',
  'Teacher', 'Lecturer', 'Professor',
  'Doctor', 'Nurse', 'Medical Officer',
  'Engineer', 'Civil Engineer', 'Mechanical Engineer', 'Electrical Engineer',
  'Lawyer', 'Legal Officer', 'Attorney',
  'Sales Representative', 'Sales Manager', 'Marketing Manager',
  'Business Analyst', 'Data Analyst', 'System Analyst',
  'Administrative Officer', 'HR Manager', 'HR Executive',
  'Bank Officer', 'Bank Manager', 'Cashier',
  'Clerk', 'Office Assistant', 'Receptionist',
  'Driver', 'Security Officer', 'Technician',
  'Entrepreneur', 'Business Owner', 'Consultant',
  'Farmer', 'Fisherman', 'Laborer',
  'Other'
];

// Loan purposes
const LOAN_PURPOSES = [
  { value: 'purchase', label: 'Home/Property Purchase' },
  { value: 'refinance', label: 'Loan Refinancing' },
  { value: 'home_improvement', label: 'Home Improvement/Renovation' },
  { value: 'debt_consolidation', label: 'Debt Consolidation' },
  { value: 'business', label: 'Business' },
  { value: 'education', label: 'Education' },
  { value: 'medical', label: 'Medical Expenses' },
  { value: 'other', label: 'Other (Personal, Wedding, Vehicle, etc.)' },
];

// Loan durations
const LOAN_DURATIONS = [
  { value: 6, label: '6 Months' },
  { value: 12, label: '12 Months (1 Year)' },
  { value: 24, label: '24 Months (2 Years)' },
  { value: 36, label: '36 Months (3 Years)' },
  { value: 48, label: '48 Months (4 Years)' },
  { value: 60, label: '60 Months (5 Years)' },
  { value: 84, label: '84 Months (7 Years)' },
  { value: 120, label: '120 Months (10 Years)' },
  { value: 180, label: '180 Months (15 Years)' },
  { value: 240, label: '240 Months (20 Years)' },
];

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

  // Financial Details
  employmentType: z.enum(['Employed', 'Self-Employed', 'Unemployed', 'Student', 'Retired']),
  employerName: z.string().optional(),
  jobTitle: z.string().optional(),
  employmentLength: z.number().min(0).max(50),
  monthlyIncome: z.number().min(0, 'Monthly income must be positive'),

  // Loan Details
  loanAmount: z.number().min(10000, 'Loan amount must be at least LKR 10,000'),
  loanPurpose: z.string().min(1, 'Loan purpose is required'),
  loanTermMonths: z.number().min(6, 'Loan term must be at least 6 months'),
});

type NewApplicantFormData = z.infer<typeof newApplicantSchema>;

const steps = ['Personal Information', 'Contact Details', 'Financial Details', 'Loan Details'];

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
    loanAmount: 0,
    loanPurpose: '',
    loanTermMonths: 12,
  });

  const [errors, setErrors] = useState<Partial<Record<keyof NewApplicantFormData, string>>>({});
  
  // Track which number fields have been touched (to show empty instead of 0)
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());
  
  // Get available cities based on selected district
  const availableCities = formData.district ? SRI_LANKA_CITIES[formData.district] || [] : [];

  const handleChange = (field: keyof NewApplicantFormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    let value: string | number = event.target.value;
    
    if (event.target.type === 'number') {
      // Mark field as touched so it shows actual value instead of empty
      setTouchedFields(prev => new Set(prev).add(field));
      value = event.target.value === '' ? 0 : parseFloat(event.target.value);
    }
    
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  // Handlers for Autocomplete fields
  const handleDistrictChange = (newDistrict: string | null) => {
    setFormData((prev) => ({ 
      ...prev, 
      district: newDistrict || '',
      city: '' // Reset city when district changes
    }));
    if (errors.district) {
      setErrors((prev) => ({ ...prev, district: undefined }));
    }
  };

  const handleCityChange = (newCity: string | null) => {
    setFormData((prev) => ({ ...prev, city: newCity || '' }));
    if (errors.city) {
      setErrors((prev) => ({ ...prev, city: undefined }));
    }
  };

  const handleJobTitleChange = (newJobTitle: string | null) => {
    setFormData((prev) => ({ ...prev, jobTitle: newJobTitle || '' }));
  };

  // Get display value for number fields (empty if 0 and not touched)
  const getNumberFieldValue = (field: keyof NewApplicantFormData) => {
    const value = formData[field] as number;
    if (value === 0 && !touchedFields.has(field)) {
      return '';
    }
    return value;
  };

  const validateStep = (step: number): boolean => {
    const stepFields: Record<number, (keyof NewApplicantFormData)[]> = {
      0: ['firstName', 'lastName', 'nic', 'dateOfBirth', 'gender', 'maritalStatus', 'dependents'],
      1: ['email', 'phone', 'address', 'city', 'district', 'postalCode'],
      2: ['employmentType', 'employmentLength', 'monthlyIncome'],
      3: ['loanAmount', 'loanPurpose', 'loanTermMonths'],
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
      if (field !== 'employerName' && field !== 'jobTitle') {
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
      // Transform form data to API format (snake_case for backend)
      const apiData = {
        first_name: formData.firstName.trim(),
        last_name: formData.lastName.trim(),
        nic: formData.nic.trim(),
        date_of_birth: formData.dateOfBirth,
        gender: formData.gender,
        marital_status: formData.maritalStatus,
        dependents: formData.dependents,
        email: formData.email.trim(),
        phone: formData.phone.trim(),
        address: formData.address.trim(),
        city: formData.city,
        district: formData.district,
        postal_code: formData.postalCode.trim(),
        employment_type: formData.employmentType,
        employer_name: formData.employerName?.trim() || null,
        job_title: formData.jobTitle?.trim() || null,
        employment_length: formData.employmentLength,
        monthly_income: formData.monthlyIncome,
        loan_amount: formData.loanAmount,
        loan_purpose: formData.loanPurpose,
        loan_term_months: formData.loanTermMonths,
      };
      
      // Get token from zustand store (persisted in localStorage)
      const authStorage = localStorage.getItem('auth-storage');
      let token = '';
      if (authStorage) {
        try {
          const parsed = JSON.parse(authStorage);
          token = parsed?.state?.token || '';
        } catch (e) {
          console.error('Failed to parse auth storage');
        }
      }
      
      // Use the backend API URL directly
      const response = await fetch('http://localhost:8000/api/applicants', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(apiData),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Failed to create applicant');
      }
      
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
                value={getNumberFieldValue('dependents')}
                onChange={handleChange('dependents')}
                error={Boolean(errors.dependents)}
                helperText={errors.dependents}
                inputProps={{ min: 0, max: 20 }}
                placeholder="0"
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
              <Autocomplete
                options={SRI_LANKA_DISTRICTS}
                value={formData.district || null}
                onChange={(_, newValue) => handleDistrictChange(newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    required
                    label="District"
                    error={Boolean(errors.district)}
                    helperText={errors.district}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Autocomplete
                options={availableCities}
                value={formData.city || null}
                onChange={(_, newValue) => handleCityChange(newValue)}
                disabled={!formData.district}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    required
                    label="City"
                    error={Boolean(errors.city)}
                    helperText={errors.city || (!formData.district ? 'Select a district first' : '')}
                  />
                )}
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
                value={getNumberFieldValue('employmentLength')}
                onChange={handleChange('employmentLength')}
                error={Boolean(errors.employmentLength)}
                helperText={errors.employmentLength}
                inputProps={{ min: 0, max: 50 }}
                placeholder="0"
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
              <Autocomplete
                options={JOB_TITLES}
                value={formData.jobTitle || null}
                onChange={(_, newValue) => handleJobTitleChange(newValue)}
                freeSolo
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Job Title"
                    helperText="Optional - Select or type your job title"
                  />
                )}
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
                value={getNumberFieldValue('monthlyIncome')}
                onChange={handleChange('monthlyIncome')}
                error={Boolean(errors.monthlyIncome)}
                helperText={errors.monthlyIncome}
                InputProps={{ startAdornment: <Typography sx={{ mr: 1 }}>LKR</Typography> }}
                placeholder="0"
              />
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AccountBalance color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Loan Details
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Enter the loan request information
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Loan Amount"
                type="number"
                value={getNumberFieldValue('loanAmount')}
                onChange={handleChange('loanAmount')}
                error={Boolean(errors.loanAmount)}
                helperText={errors.loanAmount || 'Minimum LKR 10,000'}
                InputProps={{ startAdornment: <Typography sx={{ mr: 1 }}>LKR</Typography> }}
                placeholder="0"
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
                {LOAN_PURPOSES.map((purpose) => (
                  <MenuItem key={purpose.value} value={purpose.value}>
                    {purpose.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                select
                label="Loan Duration"
                value={formData.loanTermMonths}
                onChange={handleChange('loanTermMonths')}
                error={Boolean(errors.loanTermMonths)}
                helperText={errors.loanTermMonths || 'Select repayment period'}
              >
                {LOAN_DURATIONS.map((duration) => (
                  <MenuItem key={duration.value} value={duration.value}>
                    {duration.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                disabled
                label="Monthly Payment (Estimated)"
                value={formData.loanAmount && formData.loanTermMonths 
                  ? `LKR ${Math.round(formData.loanAmount / formData.loanTermMonths).toLocaleString()}`
                  : 'Enter loan details'
                }
                helperText="Principal only, interest will be calculated later"
              />
            </Grid>
            
            {/* Loan Summary */}
            {formData.loanAmount > 0 && formData.loanTermMonths > 0 && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2, bgcolor: 'action.hover', mt: 2 }}>
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                    Loan Summary
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">Loan Amount</Typography>
                      <Typography variant="body1" fontWeight={600}>
                        LKR {formData.loanAmount.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">Duration</Typography>
                      <Typography variant="body1" fontWeight={600}>
                        {formData.loanTermMonths} months
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">Purpose</Typography>
                      <Typography variant="body1" fontWeight={600}>
                        {LOAN_PURPOSES.find(p => p.value === formData.loanPurpose)?.label || formData.loanPurpose}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">Est. Monthly</Typography>
                      <Typography variant="body1" fontWeight={600}>
                        LKR {Math.round(formData.loanAmount / formData.loanTermMonths).toLocaleString()}
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            )}
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

        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4, pt: 3, borderTop: 1, borderColor: 'divider' }}>
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
