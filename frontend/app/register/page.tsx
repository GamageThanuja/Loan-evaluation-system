'use client';

import { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Link as MuiLink,
} from '@mui/material';
import { PersonAddOutlined } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AuthLayout from '@/layouts/AuthLayout';
import { authService } from '@/lib/auth/authService';
import { z } from 'zod';

const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  password: z.string().min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string(),
  role: z.enum(['manager', 'loan_officer'], {
    required_error: 'Please select a role',
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  
  const [formData, setFormData] = useState<RegisterFormData>({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    role: 'loan_officer',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof RegisterFormData, string>>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (field: keyof RegisterFormData) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const value = event.target.value as string;
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
    if (error) {
      setError(null);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setErrors({});
    setSuccess(false);

    // Validate form
    const result = registerSchema.safeParse(formData);
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof RegisterFormData, string>> = {};
      result.error.errors.forEach((err) => {
        const field = err.path[0] as keyof RegisterFormData;
        fieldErrors[field] = err.message;
      });
      setErrors(fieldErrors);
      return;
    }

    setIsLoading(true);
    try {
      const response = await authService.register({
        name: formData.name,
        email: formData.email,
        phone: formData.phone || undefined,
        password: formData.password,
        role: formData.role,
      });

      if (response.success) {
        setSuccess(true);
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      } else {
        setError(response.message || 'Registration failed');
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <Typography variant="h5" gutterBottom fontWeight={600} textAlign="center">
          Create Account
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
          Register to access the LoanWise system
        </Typography>

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Registration successful! Redirecting to login...
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          label="Full Name"
          value={formData.name}
          onChange={handleChange('name')}
          error={Boolean(errors.name)}
          helperText={errors.name}
          disabled={isLoading}
          sx={{ mb: 2 }}
          autoComplete="name"
        />

        <TextField
          fullWidth
          label="Email"
          type="email"
          value={formData.email}
          onChange={handleChange('email')}
          error={Boolean(errors.email)}
          helperText={errors.email}
          disabled={isLoading}
          sx={{ mb: 2 }}
          autoComplete="email"
        />

        <TextField
          fullWidth
          label="Phone (Optional)"
          value={formData.phone}
          onChange={handleChange('phone')}
          error={Boolean(errors.phone)}
          helperText={errors.phone}
          disabled={isLoading}
          sx={{ mb: 2 }}
          autoComplete="tel"
        />

        <TextField
          fullWidth
          label="Password"
          type="password"
          value={formData.password}
          onChange={handleChange('password')}
          error={Boolean(errors.password)}
          helperText={errors.password}
          disabled={isLoading}
          sx={{ mb: 2 }}
          autoComplete="new-password"
        />

        <TextField
          fullWidth
          label="Confirm Password"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange('confirmPassword')}
          error={Boolean(errors.confirmPassword)}
          helperText={errors.confirmPassword}
          disabled={isLoading}
          sx={{ mb: 2 }}
          autoComplete="new-password"
        />

        <FormControl fullWidth sx={{ mb: 3 }} error={Boolean(errors.role)}>
          <InputLabel>Role</InputLabel>
          <Select
            value={formData.role}
            label="Role"
            onChange={handleChange('role') as any}
            disabled={isLoading}
          >
            <MenuItem value="loan_officer">Loan Officer</MenuItem>
            <MenuItem value="manager">Manager</MenuItem>
          </Select>
          {errors.role && (
            <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
              {errors.role}
            </Typography>
          )}
        </FormControl>

        <Button
          fullWidth
          type="submit"
          variant="contained"
          size="large"
          disabled={isLoading || success}
          startIcon={isLoading ? <CircularProgress size={20} /> : <PersonAddOutlined />}
          sx={{ mb: 2 }}
        >
          {isLoading ? 'Creating account...' : 'Create Account'}
        </Button>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Already have an account?{' '}
            <Link href="/login" passHref legacyBehavior>
              <MuiLink sx={{ fontWeight: 600, cursor: 'pointer' }}>
                Sign In
              </MuiLink>
            </Link>
          </Typography>
        </Box>

        <Box
          sx={{
            mt: 3,
            p: 2,
            bgcolor: 'info.light',
            borderRadius: 2,
            color: 'info.contrastText',
          }}
        >
          <Typography variant="caption" fontWeight={600} display="block" gutterBottom>
            Password Requirements
          </Typography>
          <Typography variant="caption" display="block">
            • At least 8 characters long
          </Typography>
          <Typography variant="caption" display="block">
            • Contains uppercase and lowercase letters
          </Typography>
          <Typography variant="caption" display="block">
            • Contains at least one number
          </Typography>
        </Box>
      </Box>
    </AuthLayout>
  );
}
