'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
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
    CircularProgress,
    Alert,
    Skeleton,
} from '@mui/material';
import {
    ArrowBack,
    Person,
    AccountBalance,
    Receipt,
    History,
    CreditScore as CreditScoreIcon,
    CheckCircle,
    Cancel,
    Warning,
    Pending,
    Gavel,
} from '@mui/icons-material';
import AuditTrail from '@/components/loan/AuditTrail';
import RepaymentHistory from '@/components/loan/RepaymentHistory';
import CreditHistory from '@/components/loan/CreditHistory';
import TransactionList from '@/components/loan/TransactionList';
import {
    useApplicant,
    useLoanDetails,
    useCreditHistory,
    useRepaymentHistory,
    useAuditTrail,
} from '@/hooks/useApplicants';

// Fallback mock data - used when API is not available
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
    const params = useParams();
    const applicantId = params.id as string;
    const [activeTab, setActiveTab] = useState(0);

    // Fetch data using hooks
    const { data: applicant, isLoading: isLoadingApplicant, error: applicantError } = useApplicant(applicantId);
    const { data: loanDetails, isLoading: isLoadingLoanDetails } = useLoanDetails(applicantId);
    const { data: creditHistory, isLoading: isLoadingCredit } = useCreditHistory(applicantId);
    const { data: repaymentHistory, isLoading: isLoadingRepayment } = useRepaymentHistory(applicantId);
    const { data: auditLog, isLoading: isLoadingAudit } = useAuditTrail(applicantId);

    // Use API data if available, otherwise fall back to mock
    const displayData = applicant || mockLoanData;
    const displayLoanDetails = loanDetails || mockLoanData;
    const displayCreditHistory = creditHistory || mockLoanData.creditProfile;
    const displayRepaymentHistory = repaymentHistory || { 
        schedule: mockLoanData.repaymentSchedule, 
        summary: mockLoanData.repaymentSummary 
    };
    const displayAuditLog = auditLog || mockLoanData.auditLog;
    const displayTransactions = loanDetails?.transactions || mockLoanData.transactions;

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

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'approved':
                return <CheckCircle fontSize="small" />;
            case 'rejected':
                return <Cancel fontSize="small" />;
            case 'under_review':
                return <Pending fontSize="small" />;
            default:
                return <Warning fontSize="small" />;
        }
    };

    const getEligibilityInfo = () => {
        if (!applicant) return null;
        
        const eligibilityStatus = (applicant as any).eligibilityStatus;
        const eligibilityReasons = (applicant as any).eligibilityReasons;
        const riskScore = (applicant as any).riskScore;
        
        if (!eligibilityStatus || eligibilityStatus === 'not_checked') return null;
        
        return (
            <Card sx={{ mb: 2, bgcolor: eligibilityStatus === 'eligible' ? 'success.light' : 'error.light' }}>
                <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <Gavel />
                        <Typography variant="h6" fontWeight={600}>
                            Eligibility Assessment
                        </Typography>
                    </Box>
                    
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">Status</Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                                <Chip
                                    label={eligibilityStatus === 'eligible' ? 'Eligible' : 'Not Eligible'}
                                    color={eligibilityStatus === 'eligible' ? 'success' : 'error'}
                                    size="small"
                                    icon={eligibilityStatus === 'eligible' ? <CheckCircle /> : <Cancel />}
                                />
                            </Box>
                        </Grid>
                        
                        {riskScore !== undefined && (
                            <Grid item xs={12} sm={4}>
                                <Typography variant="caption" color="text.secondary">Risk Score</Typography>
                                <Typography variant="h6" fontWeight={600} color={riskScore < 0.3 ? 'success.main' : riskScore < 0.6 ? 'warning.main' : 'error.main'}>
                                    {(riskScore * 100).toFixed(1)}%
                                </Typography>
                            </Grid>
                        )}
                        
                        {eligibilityReasons && eligibilityReasons.length > 0 && (
                            <Grid item xs={12}>
                                <Typography variant="caption" color="text.secondary">
                                    {eligibilityStatus === 'eligible' ? 'Positive Factors' : 'Reasons for Ineligibility'}
                                </Typography>
                                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    {eligibilityReasons.map((reason: string, index: number) => (
                                        <Chip
                                            key={index}
                                            label={reason}
                                            size="small"
                                            variant="outlined"
                                            color={eligibilityStatus === 'eligible' ? 'success' : 'error'}
                                        />
                                    ))}
                                </Box>
                            </Grid>
                        )}
                    </Grid>
                </CardContent>
            </Card>
        );
    };

    // Show loading state
    if (isLoadingApplicant) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
                <CircularProgress />
            </Box>
        );
    }

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
                                {displayData.firstName[0]}{displayData.lastName[0]}
                            </Avatar>
                        </Grid>

                        <Grid item xs>
                            <Typography variant="h4" fontWeight={700} gutterBottom>
                                {displayData.firstName} {displayData.lastName}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                                <Chip
                                    label={displayData.status.toUpperCase().replace('_', ' ')}
                                    color={getStatusColor(displayData.status)}
                                    size="small"
                                    icon={getStatusIcon(displayData.status)}
                                />
                                <Chip
                                    label={`Loan ID: ${displayData.id}`}
                                    variant="outlined"
                                    size="small"
                                />
                                <Typography variant="body2" color="text.secondary">
                                    {displayData.email}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {displayData.phone}
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
                                    {formatCurrency(displayData.loanAmount)}
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Interest Rate
                                </Typography>
                                <Typography variant="h6" fontWeight={600}>
                                    {displayLoanDetails.interestRate}%
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Monthly Payment
                                </Typography>
                                <Typography variant="h6" fontWeight={600}>
                                    {formatCurrency(displayLoanDetails.monthlyPayment)}
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Credit Score
                                </Typography>
                                <Typography variant="h6" fontWeight={600} color="success.main">
                                    {displayData.creditScore}
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>
                </Paper>
            </Box>

            {/* Eligibility Assessment Card */}
            {getEligibilityInfo()}

            {/* Rejection Reason (if rejected) */}
            {displayData.status === 'rejected' && (applicant as any)?.rejectionReason && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" fontWeight={600}>Rejection Reason:</Typography>
                    <Typography variant="body2">{(applicant as any).rejectionReason}</Typography>
                </Alert>
            )}

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
                                                <Typography variant="body2">{new Date(displayData.dateOfBirth).toLocaleDateString()}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Age</Typography>
                                                <Typography variant="body2">{displayData.age} years</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Marital Status</Typography>
                                                <Typography variant="body2">{displayData.maritalStatus}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Dependents</Typography>
                                                <Typography variant="body2">{displayData.dependents}</Typography>
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
                                                <Typography variant="body2">{displayData.employmentType}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Employment Length</Typography>
                                                <Typography variant="body2">{displayData.employmentLength} years</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Annual Income</Typography>
                                                <Typography variant="body2" fontWeight={600}>{formatCurrency(displayData.annualIncome)}</Typography>
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
                                                <Typography variant="body2">{displayData.loanPurpose}</Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Loan Term</Typography>
                                                <Typography variant="body2">{displayData.loanTerm} months ({displayData.loanTerm / 12} years)</Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Total Payable</Typography>
                                                <Typography variant="body2" fontWeight={600}>{formatCurrency(displayLoanDetails.totalPayable)}</Typography>
                                            </Grid>
                                            {displayLoanDetails.disbursementDate && (
                                                <Grid item xs={12} sm={6} md={4}>
                                                    <Typography variant="caption" color="text.secondary">Disbursement Date</Typography>
                                                    <Typography variant="body2">{new Date(displayLoanDetails.disbursementDate!).toLocaleDateString()}</Typography>
                                                </Grid>
                                            )}
                                            {displayLoanDetails.maturityDate && (
                                                <Grid item xs={12} sm={6} md={4}>
                                                    <Typography variant="caption" color="text.secondary">Maturity Date</Typography>
                                                    <Typography variant="body2">{new Date(displayLoanDetails.maturityDate!).toLocaleDateString()}</Typography>
                                                </Grid>
                                            )}
                                        </Grid>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </TabPanel>

                    <TabPanel value={activeTab} index={1}>
                        {isLoadingRepayment ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                                <CircularProgress />
                            </Box>
                        ) : (
                            <RepaymentHistory
                                schedule={displayRepaymentHistory.schedule}
                                summary={displayRepaymentHistory.summary}
                            />
                        )}
                    </TabPanel>

                    <TabPanel value={activeTab} index={2}>
                        {isLoadingCredit ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                                <CircularProgress />
                            </Box>
                        ) : (
                            <CreditHistory creditProfile={displayCreditHistory} />
                        )}
                    </TabPanel>

                    <TabPanel value={activeTab} index={3}>
                        {isLoadingLoanDetails ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                                <CircularProgress />
                            </Box>
                        ) : (
                            <TransactionList transactions={displayTransactions} />
                        )}
                    </TabPanel>

                    <TabPanel value={activeTab} index={4}>
                        {isLoadingAudit ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                                <CircularProgress />
                            </Box>
                        ) : (
                            <AuditTrail auditLog={displayAuditLog} />
                        )}
                    </TabPanel>
                </Box>
            </Paper>
        </Box>
    );
}
