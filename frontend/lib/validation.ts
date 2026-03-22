import { z } from 'zod';

// Login Validation
export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  role: z.enum(['loan_officer', 'manager'], {
    required_error: 'Please select a role',
  }).optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;

// Applicant Validation
export const applicantSchema = z.object({
  // Personal Information
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().regex(/^\+?[\d\s-()]+$/, 'Invalid phone number'),
  dateOfBirth: z.string().refine(
    (date) => {
      const age = new Date().getFullYear() - new Date(date).getFullYear();
      return age >= 18 && age <= 100;
    },
    { message: 'Applicant must be between 18 and 100 years old' }
  ),
  gender: z.enum(['M', 'F', 'Other']),
  maritalStatus: z.enum(['Single', 'Married', 'Divorced', 'Widowed']),
  dependents: z.number().min(0).max(20),
  
  // Financial Information
  annualIncome: z.number()
    .min(1000, 'Annual income must be at least $1,000')
    .max(10000000, 'Annual income cannot exceed $10,000,000'),
  employmentType: z.enum(['Employed', 'Self-Employed', 'Unemployed', 'Student', 'Retired']),
  employmentLength: z.number()
    .min(0, 'Employment length cannot be negative')
    .max(50, 'Employment length cannot exceed 50 years'),
  creditScore: z.number()
    .min(300, 'Credit score must be at least 300')
    .max(850, 'Credit score cannot exceed 850'),
  
  // Loan Information
  loanAmount: z.number()
    .min(1000, 'Loan amount must be at least $1,000')
    .max(1000000, 'Loan amount cannot exceed $1,000,000'),
  loanPurpose: z.enum(['Home', 'Auto', 'Personal', 'Education', 'Business', 'Other']),
  loanTerm: z.number()
    .min(6, 'Loan term must be at least 6 months')
    .max(360, 'Loan term cannot exceed 360 months'),
  
  // Address (Optional)
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, 'Invalid ZIP code').optional().or(z.literal('')),
});

export type ApplicantFormData = z.infer<typeof applicantSchema>;

// Prediction Request Validation
export const predictionRequestSchema = z.object({
  applicantId: z.string().uuid('Invalid applicant ID'),
  features: z.record(z.string(), z.number()),
});

// Report Filters Validation
export const reportFiltersSchema = z.object({
  startDate: z.string().refine((date) => !isNaN(Date.parse(date)), {
    message: 'Invalid start date',
  }),
  endDate: z.string().refine((date) => !isNaN(Date.parse(date)), {
    message: 'Invalid end date',
  }),
  decision: z.enum(['APPROVE', 'REJECT', 'MANUAL_REVIEW']).optional(),
  riskLevel: z.enum(['LOW', 'MEDIUM', 'HIGH']).optional(),
  minRiskScore: z.number().min(0).max(1).optional(),
  maxRiskScore: z.number().min(0).max(1).optional(),
}).refine(
  (data) => new Date(data.startDate) <= new Date(data.endDate),
  { message: 'Start date must be before end date', path: ['endDate'] }
);

export type ReportFiltersData = z.infer<typeof reportFiltersSchema>;

// Export Data Validation
export const exportSchema = z.object({
  format: z.enum(['csv', 'pdf']),
  filters: reportFiltersSchema.optional(),
  includeDetails: z.boolean().default(false),
});

export type ExportData = z.infer<typeof exportSchema>;

// Loan Action Validation
export const loanActionSchema = z.object({
  applicantId: z.string().uuid(),
  action: z.enum(['approve', 'reject']),
  reason: z.string().min(10, 'Reason must be at least 10 characters').optional(),
  notes: z.string().optional(),
});

export type LoanActionData = z.infer<typeof loanActionSchema>;

// Helper function to format validation errors
export const formatZodError = (error: z.ZodError): Record<string, string> => {
  const formattedErrors: Record<string, string> = {};
  error.errors.forEach((err) => {
    const path = err.path.join('.');
    formattedErrors[path] = err.message;
  });
  return formattedErrors;
};
