'use client';

import './globals.css';
import Providers from '@/components/Providers';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import MainLayout from '@/layouts/MainLayout';
import { useRouter } from 'next/navigation';

function AppContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !isAuthenticated && pathname !== '/login') {
      router.push('/login');
    }
  }, [isAuthenticated, pathname, router, mounted]);

  // Don't render anything until mounted
  if (!mounted) {
    return null;
  }

  // Auth layout for login page
  if (pathname === '/login') {
    return children;
  }

  // Main layout for authenticated pages
  if (isAuthenticated) {
    return <MainLayout>{children}</MainLayout>;
  }

  return null;
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <title>Home Credit Loan Approval</title>
        <meta name="description" content="AI-powered loan approval system" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div id="__next">
          <Providers>
            <AppContent>{children}</AppContent>
          </Providers>
        </div>
      </body>
    </html>
  );
}
