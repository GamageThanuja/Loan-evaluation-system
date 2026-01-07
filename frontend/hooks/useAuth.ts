'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials } from '@/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isManager: () => boolean;
  isOfficer: () => boolean;
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,

      login: async (credentials: LoginCredentials) => {
        // Mock authentication - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000));

        const mockUser: User = {
          id: '1',
          email: credentials.email,
          name: credentials.email.split('@')[0],
          role: credentials.role,
        };

        set({ user: mockUser, isAuthenticated: true });
      },

      logout: () => {
        set({ user: null, isAuthenticated: false });
      },

      isManager: () => {
        const { user } = get();
        return user?.role === 'bank_manager';
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
