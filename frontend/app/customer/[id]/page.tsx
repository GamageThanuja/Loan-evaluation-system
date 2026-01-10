'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Avatar,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  ArrowBack,
  Person,
  Phone,
  Work,
  AccountBalance,
  History,
  CreditScore,
  TrendingUp,
  CheckCircle,
  Cancel,
  Schedule,
} from '@mui/icons-material';
import { useRouter, useParams } from 'next/navigation';

// Mock data - replace with actual API calls
const mockCustomerData = {
  id: '1',
  customerId: 'CUST001',
  nic: '951234567V',
  firstName: 'John',
  lastName: 'Doe',
  email: 'john.doe@email.com',
  phone: '+94 77 123 4567',
  dateOfBirth: '1995-03-15',
  gender: 'Male',
  maritalStatus: 'Married',
  address: '123 Main Street, Colombo 05',
  employmentType: 'Employed',
  employmentLength: 5,
  annualIncome: 1200000,
  createdAt: '2023-01-15',
};

const mockLoanHistory = [
  {
    id: 'LOAN001',
    type: 'Personal Loan',
    amount: 500000,
    status: 'approved',
    appliedDate: '2024-01-15',
    approvedDate: '2024-01-20',
    term: 24,
    interestRate: 12.5,
    remainingAmount: 250000,
  },
  {
    id: 'LOAN002',
    type: 'Vehicle Loan',
    amount: 1500000,
    status: 'active',
    appliedDate: '2024-06-10',
    approvedDate: '2024-06-15',
    term: 48,
    interestRate: 10.0,
    remainingAmount: 1350000,
  },
  {
    id: 'LOAN003',
    type: 'Personal Loan',
    amount: 200000,
    status: 'rejected',
    appliedDate: '2023-06-01',
    rejectedDate: '2023-06-05',
    rejectionReason: 'Insufficient income documentation',
  },
  {
    id: 'LOAN004',
    type: 'Home Loan',
    amount: 5000000,
    status: 'pending',
    appliedDate: '2025-01-05',
  },
];

const mockRepaymentHistory = [
  { id: 1, loanId: 'LOAN001', dueDate: '2024-12-15', paidDate: '2024-12-14', amount: 25000, status: 'paid', daysLate: 0 },
  { id: 2, loanId: 'LOAN001', dueDate: '2024-11-15', paidDate: '2024-11-15', amount: 25000, status: 'paid', daysLate: 0 },
  { id: 3, loanId: 'LOAN001', dueDate: '2024-10-15', paidDate: '2024-10-18', amount: 25000, status: 'paid', daysLate: 3 },
  { id: 4, loanId: 'LOAN002', dueDate: '2024-12-15', paidDate: '2024-12-15', amount: 40000, status: 'paid', daysLate: 0 },
  { id: 5, loanId: 'LOAN002', dueDate: '2025-01-15', paidDate: null, amount: 40000, status: 'upcoming', daysLate: 0 },
];

const mockCreditHistory = {
  creditScore: 720,
  scoreChange: +15,
  lastUpdated: '2025-01-01',
  creditUtilization: 35,
  paymentHistory: 95,
  creditAge: 8,
  inquiries: 2,
  derogatorMarks: 0,
  factors: [
    { factor: 'Payment History', impact: 'positive', description: 'Consistent on-time payments' },
    { factor: 'Credit Utilization', impact: 'positive', description: 'Below 40% utilization' },
    { factor: 'Recent Inquiries', impact: 'neutral', description: '2 inquiries in last 6 months' },
  ],
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function CustomerProfilePage() {
  const router = useRouter();
  // TODO: Use useParams().id to fetch customer data from API
  useParams(); // Will be used for API calls
  const [tabValue, setTabValue] = useState(0);

  // TODO: Replace mock data with API call

  const customer = mockCustomerData;
  const loanHistory = mockLoanHistory;
  const repaymentHistory = mockRepaymentHistory;
  const creditHistory = mockCreditHistory;

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
      case 'active':
      case 'paid':
        return 'success';
      case 'rejected':
        return 'error';
      case 'pending':
      case 'upcoming':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
      case 'active':
      case 'paid':
        return <CheckCircle fontSize="small" />;
      case 'rejected':
        return <Cancel fontSize="small" />;
      case 'pending':
      case 'upcoming':
        return <Schedule fontSize="small" />;
      default:
        return undefined;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-LK', {
      style: 'currency',
      currency: 'LKR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getCreditScoreColor = (score: number) => {
    if (score >= 750) return '#2e7d32';
    if (score >= 700) return '#4caf50';
    if (score >= 650) return '#ff9800';
    if (score >= 600) return '#f57c00';
    return '#d32f2f';
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Button startIcon={<ArrowBack />} onClick={() => router.back()} sx={{ mb: 2 }}>
          Back
        </Button>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: 'primary.main',
                fontSize: '2rem',
              }}
            >
              {customer.firstName.charAt(0)}{customer.lastName.charAt(0)}
            </Avatar>
            <Box>
              <Typography variant="h4" fontWeight={700}>
                {customer.firstName} {customer.lastName}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Customer ID: {customer.customerId} | NIC: {customer.nic}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Member since {new Date(customer.createdAt).toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
          <Button
            variant="contained"
            onClick={() => router.push('/applicant/new')}
          >
            New Loan Application
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<Person />} label="Personal Details" iconPosition="start" />
          <Tab icon={<AccountBalance />} label="Loan History" iconPosition="start" />
          <Tab icon={<History />} label="Repayment History" iconPosition="start" />
          <Tab icon={<CreditScore />} label="Credit History" iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Personal Details Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Personal Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Full Name</Typography>
                    <Typography variant="body1">{customer.firstName} {customer.lastName}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Date of Birth</Typography>
                    <Typography variant="body1">{new Date(customer.dateOfBirth).toLocaleDateString()}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Gender</Typography>
                    <Typography variant="body1">{customer.gender}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Marital Status</Typography>
                    <Typography variant="body1">{customer.maritalStatus}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">NIC Number</Typography>
                    <Typography variant="body1">{customer.nic}</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  <Phone sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Contact Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">Email Address</Typography>
                    <Typography variant="body1">{customer.email}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">Phone Number</Typography>
                    <Typography variant="body1">{customer.phone}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">Address</Typography>
                    <Typography variant="body1">{customer.address}</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  <Work sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Employment & Financial Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Employment Type</Typography>
                    <Typography variant="body1">{customer.employmentType}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Employment Length</Typography>
                    <Typography variant="body1">{customer.employmentLength} years</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Annual Income</Typography>
                    <Typography variant="body1" fontWeight={600}>{formatCurrency(customer.annualIncome)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Credit Score</Typography>
                    <Typography 
                      variant="body1" 
                      fontWeight={600}
                      sx={{ color: getCreditScoreColor(creditHistory.creditScore) }}
                    >
                      {creditHistory.creditScore}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Loan History Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={6} md={3}>
            <Card sx={{ bgcolor: 'success.light', color: 'success.contrastText' }}>
              <CardContent>
                <Typography variant="h4" fontWeight={700}>
                  {loanHistory.filter(l => l.status === 'approved' || l.status === 'active').length}
                </Typography>
                <Typography variant="body2">Approved/Active</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} md={3}>
            <Card sx={{ bgcolor: 'warning.light', color: 'warning.contrastText' }}>
              <CardContent>
                <Typography variant="h4" fontWeight={700}>
                  {loanHistory.filter(l => l.status === 'pending').length}
                </Typography>
                <Typography variant="body2">Pending</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} md={3}>
            <Card sx={{ bgcolor: 'error.light', color: 'error.contrastText' }}>
              <CardContent>
                <Typography variant="h4" fontWeight={700}>
                  {loanHistory.filter(l => l.status === 'rejected').length}
                </Typography>
                <Typography variant="body2">Rejected</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} md={3}>
            <Card sx={{ bgcolor: 'primary.light', color: 'primary.contrastText' }}>
              <CardContent>
                <Typography variant="h4" fontWeight={700}>
                  {formatCurrency(loanHistory.reduce((sum, l) => sum + (l.remainingAmount || 0), 0))}
                </Typography>
                <Typography variant="body2">Outstanding</Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Loan Table */}
          <Grid item xs={12}>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Loan ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Term</TableCell>
                    <TableCell>Interest Rate</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Applied Date</TableCell>
                    <TableCell>Remaining</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loanHistory.map((loan) => (
                    <TableRow key={loan.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>{loan.id}</Typography>
                      </TableCell>
                      <TableCell>{loan.type}</TableCell>
                      <TableCell>{formatCurrency(loan.amount)}</TableCell>
                      <TableCell>{loan.term ? `${loan.term} months` : '-'}</TableCell>
                      <TableCell>{loan.interestRate ? `${loan.interestRate}%` : '-'}</TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(loan.status)}
                          label={loan.status.toUpperCase()}
                          size="small"
                          color={getStatusColor(loan.status) as any}
                        />
                      </TableCell>
                      <TableCell>{new Date(loan.appliedDate).toLocaleDateString()}</TableCell>
                      <TableCell>
                        {loan.remainingAmount ? formatCurrency(loan.remainingAmount) : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Repayment History Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          {/* Payment Summary */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Payment Summary
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">On-Time Payments</Typography>
                    <Typography variant="h5" fontWeight={700} color="success.main">
                      {repaymentHistory.filter(r => r.daysLate === 0 && r.status === 'paid').length}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Late Payments</Typography>
                    <Typography variant="h5" fontWeight={700} color="warning.main">
                      {repaymentHistory.filter(r => r.daysLate > 0).length}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Upcoming Payments</Typography>
                    <Typography variant="h5" fontWeight={700} color="info.main">
                      {repaymentHistory.filter(r => r.status === 'upcoming').length}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Payment Rate</Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {Math.round((repaymentHistory.filter(r => r.daysLate === 0 && r.status === 'paid').length / 
                        repaymentHistory.filter(r => r.status === 'paid').length) * 100)}%
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Repayment Table */}
          <Grid item xs={12}>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Loan ID</TableCell>
                    <TableCell>Due Date</TableCell>
                    <TableCell>Paid Date</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Days Late</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {repaymentHistory.map((payment) => (
                    <TableRow key={payment.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>{payment.loanId}</Typography>
                      </TableCell>
                      <TableCell>{new Date(payment.dueDate).toLocaleDateString()}</TableCell>
                      <TableCell>
                        {payment.paidDate ? new Date(payment.paidDate).toLocaleDateString() : '-'}
                      </TableCell>
                      <TableCell>{formatCurrency(payment.amount)}</TableCell>
                      <TableCell>
                        <Chip
                          label={payment.status.toUpperCase()}
                          size="small"
                          color={getStatusColor(payment.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography 
                          variant="body2" 
                          color={payment.daysLate > 0 ? 'warning.main' : 'text.secondary'}
                        >
                          {payment.daysLate > 0 ? `${payment.daysLate} days` : '-'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Credit History Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          {/* Credit Score Card */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Credit Score
                </Typography>
                <Box
                  sx={{
                    width: 150,
                    height: 150,
                    borderRadius: '50%',
                    border: `8px solid ${getCreditScoreColor(creditHistory.creditScore)}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: 'column',
                    mx: 'auto',
                    my: 2,
                  }}
                >
                  <Typography variant="h3" fontWeight={700} color={getCreditScoreColor(creditHistory.creditScore)}>
                    {creditHistory.creditScore}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <TrendingUp fontSize="small" color="success" />
                    <Typography variant="caption" color="success.main">
                      +{creditHistory.scoreChange}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Last updated: {new Date(creditHistory.lastUpdated).toLocaleDateString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Credit Metrics */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Credit Metrics
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Credit Utilization</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={creditHistory.creditUtilization} 
                        sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                        color={creditHistory.creditUtilization < 30 ? 'success' : creditHistory.creditUtilization < 50 ? 'warning' : 'error'}
                      />
                      <Typography variant="body2" fontWeight={600}>
                        {creditHistory.creditUtilization}%
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Payment History</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={creditHistory.paymentHistory} 
                        sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                        color="success"
                      />
                      <Typography variant="body2" fontWeight={600}>
                        {creditHistory.paymentHistory}%
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Credit Age</Typography>
                    <Typography variant="h6">{creditHistory.creditAge} years</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Recent Inquiries</Typography>
                    <Typography variant="h6">{creditHistory.inquiries}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">Derogatory Marks</Typography>
                    <Typography variant="h6" color={creditHistory.derogatorMarks === 0 ? 'success.main' : 'error.main'}>
                      {creditHistory.derogatorMarks}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Credit Factors */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Credit Score Factors
                </Typography>
                <Grid container spacing={2}>
                  {creditHistory.factors.map((factor, index) => (
                    <Grid item xs={12} md={4} key={index}>
                      <Paper 
                        sx={{ 
                          p: 2, 
                          borderLeft: `4px solid ${
                            factor.impact === 'positive' ? '#2e7d32' : 
                            factor.impact === 'negative' ? '#d32f2f' : '#ff9800'
                          }` 
                        }}
                      >
                        <Typography variant="subtitle2" fontWeight={600}>
                          {factor.factor}
                        </Typography>
                        <Chip 
                          label={factor.impact.toUpperCase()} 
                          size="small" 
                          color={
                            factor.impact === 'positive' ? 'success' : 
                            factor.impact === 'negative' ? 'error' : 'warning'
                          }
                          sx={{ my: 1 }}
                        />
                        <Typography variant="body2" color="text.secondary">
                          {factor.description}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
}
