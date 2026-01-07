'use client';

import { Box, Card, CardContent, Skeleton, Grid } from '@mui/material';

// Card skeleton
export function CardSkeleton() {
  return (
    <Card>
      <CardContent>
        <Skeleton variant="text" width="60%" height={30} />
        <Skeleton variant="text" width="40%" height={60} />
      </CardContent>
    </Card>
  );
}

// Table skeleton
export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <Box>
      {Array.from({ length: rows }).map((_, index) => (
        <Box key={index} sx={{ mb: 2 }}>
          <Skeleton variant="rectangular" height={50} />
        </Box>
      ))}
    </Box>
  );
}

// List skeleton
export function ListSkeleton({ items = 3 }: { items?: number }) {
  return (
    <Box>
      {Array.from({ length: items }).map((_, index) => (
        <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="text" width="80%" />
            <Skeleton variant="text" width="60%" />
          </Box>
        </Box>
      ))}
    </Box>
  );
}

// Form skeleton
export function FormSkeleton({ fields = 5 }: { fields?: number }) {
  return (
    <Box>
      {Array.from({ length: fields }).map((_, index) => (
        <Box key={index} sx={{ mb: 3 }}>
          <Skeleton variant="text" width="30%" height={20} sx={{ mb: 1 }} />
          <Skeleton variant="rectangular" height={56} />
        </Box>
      ))}
    </Box>
  );
}

// Dashboard stats skeleton
export function DashboardStatsSkeleton() {
  return (
    <Grid container spacing={3}>
      {Array.from({ length: 4 }).map((_, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <CardSkeleton />
        </Grid>
      ))}
    </Grid>
  );
}

// Chart skeleton
export function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <Card>
      <CardContent>
        <Skeleton variant="text" width="40%" height={30} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={height} />
      </CardContent>
    </Card>
  );
}

// Detail page skeleton
export function DetailSkeleton() {
  return (
    <Box>
      <Skeleton variant="text" width="40%" height={40} sx={{ mb: 3 }} />
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <CardSkeleton />
        </Grid>
        <Grid item xs={12} md={6}>
          <CardSkeleton />
        </Grid>
        <Grid item xs={12}>
          <ChartSkeleton />
        </Grid>
      </Grid>
    </Box>
  );
}
