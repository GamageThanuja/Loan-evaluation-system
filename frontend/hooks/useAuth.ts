'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials } from '@/types';
import { authService } from '@/lib/auth/authService';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  verifyToken: () => Promise<boolean>;
  clearError: () => void;
  isManager: () => boolean;
  isOfficer: () => boolean;
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: LoginCredentials) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await authService.login(credentials);
          
          if (response.success && response.token && response.user) {
            set({ 
              user: response.user, 
              token: response.token,
              isAuthenticated: true,
              isLoading: false,
              error: null
            });
          } else {
            throw new Error(response.message || 'Login failed');
          }
        } catch (error: any) {
          set({ 
            isLoading: false, 
            error: error.message || 'Login failed',
            isAuthenticated: false 
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          const { token } = get();
          if (token) {
            await authService.logout(token);
          }
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          set({ 
            user: null, 
            token: null,
            isAuthenticated: false,
            error: null 
          });
        }
      },

      verifyToken: async () => {
        const { token } = get();
        if (!token) {
          set({ isAuthenticated: false });
          return false;
        }

        try {
          const response = await authService.verifyToken(token);
          if (response.success) {
            set({ isAuthenticated: true });
            return true;
          }
        } catch (error) {
          set({ 
            user: null, 
            token: null,
            isAuthenticated: false 
          });
        }
        return false;
      },

      clearError: () => {
        set({ error: null });
      },

      isManager: () => {
        const { user } = get();
        return user?.role === 'manager';
      },

      isOfficer: () => {
        const { user } = get();
        return user?.role === 'loan_officer';
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
