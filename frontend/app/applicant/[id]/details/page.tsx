'use client';

import { useState } from 'react';
import {
    Box,
    Typography,
    Tabs,
    Tab,
    Paper,
    Grid,
    Card,
    CardContent,
    Chip,
    Button,
    Divider,
    Avatar,
} from '@mui/material';
import {
    ArrowBack,
    Person,
    AccountBalance,
    Receipt,
    History,
    CreditScore as CreditScoreIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import AuditTrail from '@/components/loan/AuditTrail';
import RepaymentHistory from '@/components/loan/RepaymentHistory';
import CreditHistory from '@/components/loan/CreditHistory';
import TransactionList from '@/components/loan/TransactionList';

// Mock data - replace with actual API calls
const mockLoanData = {
    id: '1',
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '(555) 123-4567',
    dateOfBirth: '1990-05-15',
    age: 34,
    gender: 'M' as const,
    maritalStatus: 'Married' as const,
    dependents: 2,
    annualIncome: 75000,
    employmentType: 'Employed' as const,
    employmentLength: 8,
    creditScore: 720,
    loanAmount: 250000,
    loanPurpose: 'Home' as const,
    loanTerm: 360,
    interestRate: 4.5,
    monthlyPayment: 1266.71,
    totalPayable: 456195.60,
    disbursementDate: '2024-01-15',
    maturityDate: '2054-01-15',
    createdAt: '2024-01-01T10:00:00Z',
    updatedAt: '2024-01-15T14:30:00Z',
    status: 'approved' as const,

    auditLog: [
        {
            id: '1',
            timestamp: '2024-01-15T14:30:00Z',
            action: 'approved' as const,
            performedBy: { id: '1', name: 'Jane Smith', role: 'loan_officer' as const },
            description: 'Loan application approved and disbursed',
            metadata: { amount: 250000 },
        },
        {
            id: '2',
            timestamp: '2024-01-10T11:20:00Z',
            action: 'reviewed' as const,
            performedBy: { id: '2', name: 'Mike Johnson', role: 'manager' as const },
            description: 'Application reviewed and recommended for approval',
        },
        {
            id: '3',
            timestamp: '2024-01-05T09:15:00Z',
            action: 'status_changed' as const,
            performedBy: { id: '1', name: 'Jane Smith', role: 'loan_officer' as const },
            description: 'Status changed from pending to under_review',
            changes: [
                { field: 'status', oldValue: 'pending', newValue: 'under_review' },
            ],
        },
        {
            id: '4',
            timestamp: '2024-01-01T10:00:00Z',
            action: 'created' as const,
            performedBy: { id: '1', name: 'Jane Smith', role: 'loan_officer' as const },
            description: 'Loan application created',
        },
    ],

    repaymentSchedule: Array.from({ length: 12 }, (_, i) => ({
        id: `payment-${i + 1}`,
        loanId: '1',
        installmentNumber: i + 1,
        dueDate: new Date(2024, i + 1, 15).toISOString(),
        principalAmount: 937.50,
        interestAmount: 329.21,
        totalAmount: 1266.71,
        status: i < 3 ? ('paid' as const) : i === 3 ? ('overdue' as const) : ('pending' as const),
        paidAmount: i < 3 ? 1266.71 : undefined,
        paidDate: i < 3 ? new Date(2024, i + 1, 14).toISOString() : undefined,
        lateFee: i === 3 ? 25 : undefined,
        remainingBalance: 250000 - (937.50 * (i + 1)),
    })),

    repaymentSummary: {
        totalLoanAmount: 250000,
        totalPaid: 3800.13,
        totalRemaining: 246199.87,
        totalInterest: 206195.60,
        nextPaymentDue: new Date(2024, 4, 15).toISOString(),
        nextPaymentAmount: 1291.71,
        overdueAmount: 1291.71,
        numberOfPayments: 360,
        paymentsCompleted: 3,
        paymentStatus: 'late' as const,
    },

    creditProfile: {
        currentScore: 720,
        scoreHistory: [
            { id: '1', date: '2024-01-01', creditScore: 720, bureau: 'Experian' as const, change: 5 },
            { id: '2', date: '2023-10-01', creditScore: 715, bureau: 'Equifax' as const, change: -3 },
            { id: '3', date: '2023-07-01', creditScore: 718, bureau: 'TransUnion' as const, change: 8 },
            { id: '4', date: '2023-04-01', creditScore: 710, bureau: 'Experian' as const, change: 0 },
            { id: '5', date: '2023-01-01', creditScore: 710, bureau: 'Equifax' as const },
        ],
        creditUtilization: 0.28,
        totalCreditLines: 5,
        oldestAccount: '2015-03-20',
        recentInquiries: 2,
        delinquencies: 0,
        publicRecords: 0,
        averageAccountAge: 6.5,
    },

    transactions: [
        {
            id: '1',
            date: '2024-04-14',
            type: 'payment' as const,
            amount: 1266.71,
            description: 'Monthly payment - Installment #3',
            status: 'completed' as const,
            paymentMethod: 'bank_transfer' as const,
            referenceNumber: 'TXN-2024-0414-001',
            balance: 247187.50,
        },
        {
            id: '2',
            date: '2024-03-14',
            type: 'payment' as const,
            amount: 1266.71,
            description: 'Monthly payment - Installment #2',
            status: 'completed' as const,
            paymentMethod: 'bank_transfer' as const,
            referenceNumber: 'TXN-2024-0314-001',
            balance: 248125.00,
        },
        {
            id: '3',
            date: '2024-02-14',
            type: 'payment' as const,
            amount: 1266.71,
            description: 'Monthly payment - Installment #1',
            status: 'completed' as const,
            paymentMethod: 'online' as const,
            referenceNumber: 'TXN-2024-0214-001',
            balance: 249062.50,
        },
        {
            id: '4',
            date: '2024-01-20',
            type: 'fee' as const,
            amount: 500,
            description: 'Loan processing fee',
            status: 'completed' as const,
            referenceNumber: 'FEE-2024-001',
            balance: 250000,
        },
        {
            id: '5',
            date: '2024-01-15',
            type: 'disbursement' as const,
            amount: 250000,
            description: 'Loan disbursement',
            status: 'completed' as const,
            paymentMethod: 'bank_transfer' as const,
            referenceNumber: 'DISB-2024-001',
            balance: 250000,
        },
    ],

    transactionSummary: {
        totalTransactions: 5,
        totalDebits: 4300.13,
        totalCredits: 250000,
        monthlyTransactions: [
            { month: 'Jan 2024', count: 2, amount: 250500 },
            { month: 'Feb 2024', count: 1, amount: 1266.71 },
            { month: 'Mar 2024', count: 1, amount: 1266.71 },
            { month: 'Apr 2024', count: 1, amount: 1266.71 },
        ],
    },
};

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
    return (
        <div role="tabpanel" hidden={value !== index}>
            {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
        </div>
    );
}

export default function LoanApplicationDetails() {
    const router = useRouter();
    const [activeTab, setActiveTab] = useState(0);

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue);
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'approved':
                return 'success';
            case 'rejected':
                return 'error';
            case 'under_review':
                return 'warning';
            default:
                return 'default';
        }
    };

    return (
        <Box>
            {/* Header */}
            <Box sx={{ mb: 3 }}>
                <Button
                    startIcon={<ArrowBack />}
                    onClick={() => router.back()}
                    sx={{ mb: 2 }}
                >
                    Back to Applications
                </Button>

                <Paper sx={{ p: 3 }}>
                    <Grid container spacing={3} alignItems="center">
                        <Grid item>
                            <Avatar
                                sx={{
                                    width: 80,
                                    height: 80,
                                    bgcolor: 'primary.main',
                                    fontSize: '2rem',
                                }}
                            >
                                {mockLoanData.firstName[0]}{mockLoanData.lastName[0]}
                            </Avatar>
                        </Grid>

                        <Grid item xs>
                            <Typography variant="h4" fontWeight={700} gutterBottom>
                                {mockLoanData.firstName} {mockLoanData.lastName}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                                <Chip
                                    label={mockLoanData.status.toUpperCase().replace('_', ' ')}
                                    color={getStatusColor(mockLoanData.status)}
                                    size="small"
                                />
                                <Chip
                                    label={`Loan ID: ${mockLoanData.id}`}
                                    variant="outlined"
                                    size="small"
                                />
                                <Typography variant="body2" color="text.secondary">
                                    {mockLoanData.email}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {mockLoanData.phone}
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>

                    <Divider sx={{ my: 3 }} />

                    {/* Key Metrics */}
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Loan Amount
                                </Typography>
                                <Typography variant="h6" fontWeight={600}>
                                    {formatCurrency(mockLoanData.loanAmount)}
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Interest Rate
                                </Typography>
                                <Typography variant="h6" fontWeight={600}>
                                    {mockLoanData.interestRate}%
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Monthly Payment
                                </Typography>
                                <Typography variant="h6" fontWeight={600}>
                                    {formatCurrency(mockLoanData.monthlyPayment)}
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Credit Score
                                </Typography>
                                <Typography variant="h6" fontWeight={600} color="success.main">
                                    {mockLoanData.creditScore}
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>
                </Paper>
            </Box>

            {/* Tabs */}
            <Paper>
                <Tabs
                    value={activeTab}
                    onChange={handleTabChange}
                    variant="scrollable"
                    scrollButtons="auto"
                    sx={{
                        borderBottom: 1,
                        borderColor: 'divider',
                        px: 2,
                    }}
                >
                    <Tab icon={<Person />} iconPosition="start" label="Overview" />
                    <Tab icon={<AccountBalance />} iconPosition="start" label="Repayment History" />
                    <Tab icon={<CreditScoreIcon />} iconPosition="start" label="Credit History" />
                    <Tab icon={<Receipt />} iconPosition="start" label="Transactions" />
                    <Tab icon={<History />} iconPosition="start" label="Audit Trail" />
                </Tabs>

                <Box sx={{ px: 3 }}>
                    <TabPanel value={activeTab} index={0}>
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom fontWeight={600}>
                                            Personal Information
                                        </Typography>
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Date of Birth</Typography>
                                                <Typography variant="body2">{new Date(mockLoanData.dateOfBirth).toLocaleDateString()}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Age</Typography>
                                                <Typography variant="body2">{mockLoanData.age} years</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Marital Status</Typography>
                                                <Typography variant="body2">{mockLoanData.maritalStatus}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Dependents</Typography>
                                                <Typography variant="body2">{mockLoanData.dependents}</Typography>
                                            </Box>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>

                            <Grid item xs={12} md={6}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom fontWeight={600}>
                                            Employment & Income
                                        </Typography>
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Employment Type</Typography>
                                                <Typography variant="body2">{mockLoanData.employmentType}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Employment Length</Typography>
                                                <Typography variant="body2">{mockLoanData.employmentLength} years</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Annual Income</Typography>
                                                <Typography variant="body2" fontWeight={600}>{formatCurrency(mockLoanData.annualIncome)}</Typography>
                                            </Box>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>

                            <Grid item xs={12}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom fontWeight={600}>
                                            Loan Details
                                        </Typography>
                                        <Grid container spacing={2}>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Loan Purpose</Typography>
                                                <Typography variant="body2">{mockLoanData.loanPurpose}</Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Loan Term</Typography>
                                                <Typography variant="body2">{mockLoanData.loanTerm} months ({mockLoanData.loanTerm / 12} years)</Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Total Payable</Typography>
                                                <Typography variant="body2" fontWeight={600}>{formatCurrency(mockLoanData.totalPayable)}</Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Disbursement Date</Typography>
                                                <Typography variant="body2">{new Date(mockLoanData.disbursementDate!).toLocaleDateString()}</Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Maturity Date</Typography>
                                                <Typography variant="body2">{new Date(mockLoanData.maturityDate!).toLocaleDateString()}</Typography>
                                            </Grid>
                                        </Grid>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </TabPanel>

                    <TabPanel value={activeTab} index={1}>
                        <RepaymentHistory
                            schedule={mockLoanData.repaymentSchedule}
                            summary={mockLoanData.repaymentSummary}
                        />
                    </TabPanel>

                    <TabPanel value={activeTab} index={2}>
                        <CreditHistory creditProfile={mockLoanData.creditProfile} />
                    </TabPanel>

                    <TabPanel value={activeTab} index={3}>
                        <TransactionList transactions={mockLoanData.transactions} />
                    </TabPanel>

                    <TabPanel value={activeTab} index={4}>
                        <AuditTrail auditLog={mockLoanData.auditLog} />
                    </TabPanel>
                </Box>
            </Paper>
        </Box>
    );
}
