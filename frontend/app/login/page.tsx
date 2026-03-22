'use client';

import { useState, useEffect } from 'react';
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
  Checkbox,
  FormControlLabel,
  IconButton,
  InputAdornment,
} from '@mui/material';
import { LoginOutlined, Visibility, VisibilityOff } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import AuthLayout from '@/layouts/AuthLayout';
import { loginSchema, type LoginFormData } from '@/lib/validation';

export default function LoginPage() {
  const router = useRouter();
  const { login, error: authError, clearError } = useAuth();
  
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    role: 'loan_officer',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof LoginFormData, string>>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  // Load saved email on mount
  useEffect(() => {
    const savedEmail = localStorage.getItem('rememberedEmail');
    const savedRole = localStorage.getItem('rememberedRole');
    if (savedEmail) {
      setFormData(prev => ({ 
        ...prev, 
        email: savedEmail,
        role: (savedRole as 'loan_officer' | 'manager') || 'loan_officer'
      }));
      setRememberMe(true);
    }
  }, []);

  const handleChange = (field: keyof LoginFormData) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const value = event.target.value as string;
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
    if (error || authError) {
      setError(null);
      clearError();
    }
  };

  const handleTogglePassword = () => {
    setShowPassword((prev) => !prev);
  };

  const handleRememberMeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRememberMe(event.target.checked);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setErrors({});
    clearError();

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

    // Handle remember me
    if (rememberMe) {
      localStorage.setItem('rememberedEmail', formData.email);
      if (formData.role) {
        localStorage.setItem('rememberedRole', formData.role);
      }
    } else {
      localStorage.removeItem('rememberedEmail');
      localStorage.removeItem('rememberedRole');
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
          Enter your credentials to access LoanWise
        </Typography>

        {(error || authError) && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error || authError}
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
          type={showPassword ? 'text' : 'password'}
          value={formData.password}
          onChange={handleChange('password')}
          error={Boolean(errors.password)}
          helperText={errors.password}
          disabled={isLoading}
          sx={{ mb: 2 }}
          autoComplete="current-password"
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={handleTogglePassword}
                  edge="end"
                  disabled={isLoading}
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <FormControl fullWidth sx={{ mb: 2 }} error={Boolean(errors.role)}>
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

        <FormControlLabel
          control={
            <Checkbox
              checked={rememberMe}
              onChange={handleRememberMeChange}
              disabled={isLoading}
              color="primary"
            />
          }
          label="Remember me"
          sx={{ mb: 2 }}
        />

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

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Don't have an account?{' '}
            <Link href="/register" passHref legacyBehavior>
              <Box component="span" sx={{ color: 'primary.main', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}>
                Sign Up
              </Box>
            </Link>
          </Typography>
        </Box>
      </Box>
    </AuthLayout>
  );
}
