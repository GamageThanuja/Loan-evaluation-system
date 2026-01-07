'use client';

import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  TrendingUp,
  AssessmentOutlined,
  PeopleOutline,
  CheckCircleOutline,
  PersonAdd,
  Assessment,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useModelStats, useModelHealth } from '@/hooks/useModel';
import { useRecentPredictions } from '@/hooks/usePrediction';
import { DashboardStatsSkeleton, TableSkeleton, CardSkeleton } from '@/components/ui/LoadingSkeleton';
import { formatPercent, formatRelativeTime, getRiskLevel, getRiskColor } from '@/lib/utils';
import ErrorBoundary from '@/components/ui/ErrorBoundary';

function StatCard({
  title,
  value,
  icon,
  color,
  subtitle,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography color="text.secondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div" fontWeight={700}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              bgcolor: `${color}20`,
              color: color,
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const router = useRouter();
  const { data: stats, isLoading: statsLoading } = useModelStats();
  const { data: health, isLoading: healthLoading } = useModelHealth();
  const { data: recentPredictions, isLoading: predictionsLoading } = useRecentPredictions();

  if (statsLoading) {
    return <DashboardStatsSkeleton />;
  }

  return (
    <ErrorBoundary>
      <Box>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome to the Home Credit Loan Approval System
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Model AUC"
              value={stats ? formatPercent(stats.modelAUC, 2) : '-'}
              icon={<TrendingUp />}
              color="#2e7d32"
              subtitle="Area Under Curve"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Accuracy"
              value={stats ? formatPercent(stats.modelAccuracy, 2) : '-'}
              icon={<AssessmentOutlined />}
              color="#1976d2"
              subtitle="Model Performance"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Predictions"
              value={stats ? stats.totalPredictions.toLocaleString() : '-'}
              icon={<PeopleOutline />}
              color="#f59e0b"
              subtitle="All time"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Approval Rate"
              value={stats ? formatPercent(stats.approvalRate, 1) : '-'}
              icon={<CheckCircleOutline />}
              color="#2e7d32"
              subtitle={`${stats ? stats.pendingReviews : 0} pending`}
            />
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Model Health */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  Model Health
                </Typography>
                {healthLoading ? (
                  <CardSkeleton />
                ) : health ? (
                  <Box>
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Status</Typography>
                        <Chip
                          label={health.status.toUpperCase()}
                          color={health.status === 'healthy' ? 'success' : 'warning'}
                          size="small"
                        />
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Version</Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {health.version}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Avg Response Time</Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {health.avgResponseTime}ms
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ mb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption">Success Rate</Typography>
                        <Typography variant="caption" fontWeight={600}>
                          {formatPercent(health.successRate)}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={health.successRate * 100}
                        color="success"
                      />
                    </Box>
                  </Box>
                ) : null}
              </CardContent>
            </Card>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<PersonAdd />}
                      onClick={() => router.push('/applicant/new')}
                      sx={{ py: 2 }}
                    >
                      New Application
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<PeopleOutline />}
                      onClick={() => router.push('/applicant')}
                      sx={{ py: 2 }}
                    >
                      View All Applicants
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<Assessment />}
                      onClick={() => router.push('/reports')}
                      sx={{ py: 2 }}
                    >
                      View Reports
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="outlined"
                      disabled
                      sx={{ py: 2 }}
                    >
                      Batch Upload
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Predictions */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  Recent Predictions
                </Typography>
                {predictionsLoading ? (
                  <TableSkeleton rows={5} />
                ) : recentPredictions && recentPredictions.length > 0 ? (
                  <TableContainer component={Paper} elevation={0}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Applicant</TableCell>
                          <TableCell>Risk Score</TableCell>
                          <TableCell>Risk Level</TableCell>
                          <TableCell>Decision</TableCell>
                          <TableCell>Time</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {recentPredictions.map((prediction) => {
                          const riskLevel = getRiskLevel(prediction.riskScore);
                          const riskColor = getRiskColor(riskLevel);
                          
                          return (
                            <TableRow
                              key={prediction.id}
                              hover
                              sx={{ cursor: 'pointer' }}
                              onClick={() => router.push(`/applicant/${prediction.id}`)}
                            >
                              <TableCell>
                                <Typography variant="body2" fontWeight={600}>
                                  {prediction.applicantName}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2">
                                  {(prediction.riskScore * 100).toFixed(1)}%
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={riskLevel}
                                  size="small"
                                  sx={{
                                    bgcolor: `${riskColor}20`,
                                    color: riskColor,
                                    fontWeight: 600,
                                  }}
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={prediction.decision}
                                  size="small"
                                  color={
                                    prediction.decision === 'APPROVE'
                                      ? 'success'
                                      : prediction.decision === 'REJECT'
                                      ? 'error'
                                      : 'warning'
                                  }
                                />
                              </TableCell>
                              <TableCell>
                                <Typography variant="caption" color="text.secondary">
                                  {formatRelativeTime(prediction.timestamp)}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={prediction.status.toUpperCase()}
                                  size="small"
                                  variant="outlined"
                                />
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                    No recent predictions
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </ErrorBoundary>
  );
}
