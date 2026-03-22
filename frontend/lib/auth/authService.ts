import apiClient from '@/services/api';
import { LoginCredentials, User } from '@/types';

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  phone?: string;
  role: 'manager' | 'loan_officer';
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: User;
}

export interface ForgotPasswordData {
  email: string;
}

export interface ResetPasswordData {
  token: string;
  new_password: string;
}

class AuthService {
  /**
   * Register a new user
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/register', data);
    return response.data;
  }

  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', {
      email: credentials.email,
      password: credentials.password,
      role: credentials.role,
    });
    return response.data;
  }

  /**
   * Logout user
   */
  async logout(token: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      '/api/auth/logout',
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  }

  /**
   * Request password reset
   */
  async forgotPassword(data: ForgotPasswordData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/forgot-password', data);
    return response.data;
  }

  /**
   * Reset password with token
   */
  async resetPassword(data: ResetPasswordData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/reset-password', data);
    return response.data;
  }

  /**
   * Verify JWT token
   */
  async verifyToken(token: string): Promise<AuthResponse> {
    const response = await apiClient.get<AuthResponse>('/api/auth/verify-token', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  }
}

export const authService = new AuthService();
