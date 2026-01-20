'use client';

import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, useMemo, createContext, useContext } from 'react';
import { usePathname } from 'next/navigation';
import createAppTheme from '@/lib/theme';
import { storage } from '@/lib/utils';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

interface ThemeContextType {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  darkMode: false,
  toggleDarkMode: () => {},
});

export const useThemeContext = () => useContext(ThemeContext);

interface ProvidersProps {
  children: React.ReactNode;
}

export default function Providers({ children }: ProvidersProps) {
  const pathname = usePathname();
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      return storage.get('darkMode', false);
    }
    return false;
  });

  const theme = useMemo(() => createAppTheme(darkMode ? 'dark' : 'light'), [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode((prev: boolean) => {
      const newMode = !prev;
      storage.set('darkMode', newMode);
      return newMode;
    });
  };

  const showDevtools = process.env.NODE_ENV !== 'production' && !pathname?.startsWith('/reports/print');

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
          {showDevtools ? <ReactQueryDevtools initialIsOpen={false} /> : null}
        </ThemeProvider>
      </ThemeContext.Provider>
    </QueryClientProvider>
  );
}
