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
} from '@mui/material';
import { LoginOutlined } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import AuthLayout from '@/layouts/AuthLayout';
import { loginSchema, type LoginFormData } from '@/lib/validation';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    role: 'loan_officer',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof LoginFormData, string>>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: keyof LoginFormData) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const value = event.target.value as string;
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setErrors({});

    // Validate form
    const result = loginSchema.safeParse(formData);
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof LoginFormData, string>> = {};
      result.error.errors.forEach((err) => {
        const field = err.path[0] as keyof LoginFormData;
        fieldErrors[field] = err.message;
      });
      setErrors(fieldErrors);
      return;
    }

    setIsLoading(true);
    try {
      await login(formData);
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <Typography variant="h5" gutterBottom fontWeight={600} textAlign="center">
          Sign In
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
          Enter your credentials to access the system
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

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
          label="Password"
          type="password"
          value={formData.password}
          onChange={handleChange('password')}
          error={Boolean(errors.password)}
          helperText={errors.password}
          disabled={isLoading}
          sx={{ mb: 2 }}
          autoComplete="current-password"
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
            <MenuItem value="bank_manager">Bank Manager</MenuItem>
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
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={20} /> : <LoginOutlined />}
          sx={{ mb: 2 }}
        >
          {isLoading ? 'Signing in...' : 'Sign In'}
        </Button>

        <Box
          sx={{
            p: 2,
            bgcolor: 'info.light',
            borderRadius: 2,
            color: 'info.contrastText',
          }}
        >
          <Typography variant="caption" fontWeight={600} display="block" gutterBottom>
            Demo Credentials
          </Typography>
          <Typography variant="caption" display="block">
            Email: any email
          </Typography>
          <Typography variant="caption" display="block">
            Password: any password (min 6 characters)
          </Typography>
          <Typography variant="caption" display="block">
            Role: Select Loan Officer or Bank Manager
          </Typography>
        </Box>
      </Box>
    </AuthLayout>
  );
}
