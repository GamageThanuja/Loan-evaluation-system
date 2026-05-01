'use client';

import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
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
  AccountBalance,
  TrendingUp,
  Payments,
  PeopleOutline,
  PersonAdd,
  Assessment,
  AttachMoney,
  CalendarMonth,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useFinancialStats, useMonthlyStats, useRecentApplications } from '@/hooks/useDashboard';
import { DashboardStatsSkeleton, TableSkeleton } from '@/components/ui/LoadingSkeleton';
import { getRiskLevel, getRiskColor } from '@/lib/utils';
import ErrorBoundary from '@/components/ui/ErrorBoundary';

// Format currency in LKR
function formatLKR(value: number): string {
  if (value >= 1000000) {
    return `LKR ${(value / 1000000).toFixed(2)}M`;
  } else if (value >= 1000) {
    return `LKR ${(value / 1000).toFixed(1)}K`;
  }
  return `LKR ${value.toLocaleString()}`;
}

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
  const { data: financialStats, isLoading: financialLoading, error: financialError } = useFinancialStats();
  const { data: monthlyStats, isLoading: monthlyLoading } = useMonthlyStats();
  const { data: recentApplications, isLoading: applicationsLoading } = useRecentApplications();

  if (financialLoading) {
    return <DashboardStatsSkeleton />;
  }

  if (financialError) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="error" gutterBottom>
          Error Loading Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {financialError.message}
        </Typography>
      </Box>
    );
  }

  return (
    <ErrorBoundary>
      <Box>
        {/* Financial Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Loans Disbursed"
              value={financialStats?.totalLoansDisbursed?.toLocaleString() || '0'}
              icon={<AccountBalance />}
              color="#1976d2"
              subtitle="All time applications"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Loan Amount"
              value={formatLKR(financialStats?.totalLoanAmount || 0)}
              icon={<AttachMoney />}
              color="#2e7d32"
              subtitle="Total amount disbursed"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Interest Earned"
              value={formatLKR(financialStats?.totalInterestEarned || 0)}
              icon={<TrendingUp />}
              color="#ed6c02"
              subtitle={`@ ${financialStats?.avgInterestRate || 12}% APR`}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Approval Rate"
              value={`${financialStats?.approvalRate?.toFixed(1) || '0.0'}%`}
              icon={<Payments />}
              color="#9c27b0"
              subtitle={`${financialStats?.pendingReviews || 0} pending`}
            />
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Monthly Summary */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  <CalendarMonth sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                  {monthlyStats?.monthName || 'Monthly Summary'}
                </Typography>
                {monthlyLoading ? (
                  <Box sx={{ mt: 2 }}>
                    {[...Array(4)].map((_, i) => (
                      <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
                        <Box sx={{ width: '60%', height: 16, bgcolor: 'action.hover', borderRadius: 1 }} />
                        <Box sx={{ width: '20%', height: 16, bgcolor: 'action.hover', borderRadius: 1 }} />
                      </Box>
                    ))}
                  </Box>
                ) : (
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="body2" color="text.secondary">Applications Received</Typography>
                      <Typography variant="body2" fontWeight={600}>{monthlyStats?.applicationsReceived || 0}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="body2" color="text.secondary">Loans Approved</Typography>
                      <Typography variant="body2" fontWeight={600} color="success.main">
                        {monthlyStats?.loansApproved || 0}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="body2" color="text.secondary">Pending Review</Typography>
                      <Typography variant="body2" fontWeight={600} color="warning.main">{monthlyStats?.pendingReview || 0}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1.5 }}>
                      <Typography variant="body2" color="text.secondary">Interest Rate</Typography>
                      <Typography variant="body2" fontWeight={600}>{monthlyStats?.avgInterestRate || 12}% APR</Typography>
                    </Box>
                  </Box>
                )}
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
                      startIcon={<Payments />}
                      onClick={() => router.push('/review')}
                      sx={{ py: 2 }}
                    >
                      Review Applications
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Applications */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  Recent Applications
                </Typography>
                {applicationsLoading ? (
                  <TableSkeleton rows={5} />
                ) : recentApplications && recentApplications.length > 0 ? (
                  <TableContainer component={Paper} elevation={0}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Applicant</TableCell>
                          <TableCell>Loan Amount</TableCell>
                          <TableCell>Risk Level</TableCell>
                          <TableCell>Decision</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {recentApplications.map((application) => {
                          const riskLevel = getRiskLevel(application.riskScore);
                          const riskColor = getRiskColor(riskLevel);
                          
                          return (
                            <TableRow
                              key={application.id}
                              hover
                              sx={{ cursor: 'pointer' }}
                              onClick={() => router.push(`/applicant/${application.id}`)}
                            >
                              <TableCell>
                                <Typography variant="body2" fontWeight={600}>
                                  {application.applicantName}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2">
                                  {formatLKR(application.loanAmount || 0)}
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
                                  label={application.decision || 'PENDING'}
                                  size="small"
                                  color={
                                    application.decision === 'APPROVE'
                                      ? 'success'
                                      : application.decision === 'REJECT'
                                      ? 'error'
                                      : 'warning'
                                  }
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={application.status}
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
                    No recent applications
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
