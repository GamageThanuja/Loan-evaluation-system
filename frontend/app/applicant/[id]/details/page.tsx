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
    useTransactionHistory,
    useAuditTrail,
} from '@/hooks/useApplicants';

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
    const { data: applicant, isLoading: isLoadingApplicant } = useApplicant(applicantId);
    const { data: loanDetails, isLoading: isLoadingLoanDetails } = useLoanDetails(applicantId);
    const { data: creditHistory, isLoading: isLoadingCredit } = useCreditHistory(applicantId);
    const { data: repaymentHistory, isLoading: isLoadingRepayment } = useRepaymentHistory(applicantId);
    const { data: transactionHistory, isLoading: isLoadingTransactions } = useTransactionHistory(applicantId);
    const { data: auditLog, isLoading: isLoadingAudit } = useAuditTrail(applicantId);

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue);
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'LKR',
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

    // Show error if applicant not found
    if (!applicant) {
        return (
            <Box sx={{ p: 4 }}>
                <Button startIcon={<ArrowBack />} onClick={() => router.back()} sx={{ mb: 2 }}>
                    Back to Applications
                </Button>
                <Alert severity="error">Applicant not found</Alert>
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
                                {applicant.firstName?.[0] || (applicant as any).name?.[0] || 'U'}{applicant.lastName?.[0] || ''}
                            </Avatar>
                        </Grid>

                        <Grid item xs>
                            <Typography variant="h4" fontWeight={700} gutterBottom>
                                {applicant.firstName && applicant.lastName ? `${applicant.firstName} ${applicant.lastName}` : (applicant as any).name || 'Unknown'}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                                <Chip
                                    label={(applicant.status || 'pending').toUpperCase().replace('_', ' ')}
                                    color={getStatusColor(applicant.status || 'pending')}
                                    size="small"
                                    icon={getStatusIcon(applicant.status || 'pending')}
                                />
                                <Chip
                                    label={`Loan ID: ${applicant.id}`}
                                    variant="outlined"
                                    size="small"
                                />
                                <Typography variant="body2" color="text.secondary">
                                    {applicant.email}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {applicant.phone}
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
                                    {formatCurrency(applicant.loanAmount || 0)}
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Interest Rate
                                </Typography>
                                <Typography variant="h6" fontWeight={600}>
                                    {loanDetails?.interestRate ?? (applicant as any).interestRate ?? 'N/A'}%
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Monthly Payment
                                </Typography>
                                <Typography variant="h6" fontWeight={600}>
                                    {formatCurrency(loanDetails?.monthlyPayment ?? (applicant as any).monthlyPayment ?? 0)}
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Credit Score
                                </Typography>
                                <Typography variant="h6" fontWeight={600} color="success.main">
                                    {applicant.creditScore ?? 'N/A'}
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>
                </Paper>
            </Box>

            {/* Eligibility Assessment Card */}
            {getEligibilityInfo()}

            {/* Rejection Reason (if rejected) */}
            {applicant.status === 'rejected' && (applicant as any)?.rejectionReason && (
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
                                                <Typography variant="body2">{applicant.dateOfBirth ? new Date(applicant.dateOfBirth).toLocaleDateString() : 'N/A'}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Age</Typography>
                                                <Typography variant="body2">{applicant.age ?? 'N/A'} years</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Marital Status</Typography>
                                                <Typography variant="body2">{applicant.maritalStatus ?? 'N/A'}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Dependents</Typography>
                                                <Typography variant="body2">{applicant.dependents ?? 'N/A'}</Typography>
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
                                                <Typography variant="body2">{applicant.employmentType ?? 'N/A'}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Employment Length</Typography>
                                                <Typography variant="body2">{applicant.employmentLength ?? 'N/A'} years</Typography>
                                            </Box>
                                            <Box>
                                                <Typography variant="caption" color="text.secondary">Monthly Income</Typography>
                                                <Typography variant="body2" fontWeight={600}>{formatCurrency((applicant as any).monthlyIncome ?? 0)}</Typography>
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
                                                <Typography variant="body2">{applicant.loanPurpose ?? 'N/A'}</Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Loan Term</Typography>
                                                <Typography variant="body2">{(applicant as any).loanTermMonths ?? applicant.loanTerm ?? 0} months</Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4}>
                                                <Typography variant="caption" color="text.secondary">Total Payable</Typography>
                                                <Typography variant="body2" fontWeight={600}>{formatCurrency(loanDetails?.totalPayable ?? 0)}</Typography>
                                            </Grid>
                                            {loanDetails?.disbursementDate && (
                                                <Grid item xs={12} sm={6} md={4}>
                                                    <Typography variant="caption" color="text.secondary">Disbursement Date</Typography>
                                                    <Typography variant="body2">{new Date(loanDetails.disbursementDate).toLocaleDateString()}</Typography>
                                                </Grid>
                                            )}
                                            {loanDetails?.maturityDate && (
                                                <Grid item xs={12} sm={6} md={4}>
                                                    <Typography variant="caption" color="text.secondary">Maturity Date</Typography>
                                                    <Typography variant="body2">{new Date(loanDetails.maturityDate).toLocaleDateString()}</Typography>
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
                        ) : repaymentHistory ? (
                            <RepaymentHistory
                                schedule={repaymentHistory.schedule}
                                summary={repaymentHistory.summary}
                            />
                        ) : (
                            <Alert severity="info">No repayment history available for this applicant.</Alert>
                        )}
                    </TabPanel>

                    <TabPanel value={activeTab} index={2}>
                        {isLoadingCredit ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                                <CircularProgress />
                            </Box>
                        ) : creditHistory ? (
                            <CreditHistory creditProfile={creditHistory} />
                        ) : (
                            <Alert severity="info">No credit history available for this applicant.</Alert>
                        )}
                    </TabPanel>

                    <TabPanel value={activeTab} index={3}>
                        {isLoadingTransactions ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                                <CircularProgress />
                            </Box>
                        ) : transactionHistory?.transactions && transactionHistory.transactions.length > 0 ? (
                            <TransactionList transactions={transactionHistory.transactions} />
                        ) : (
                            <Alert severity="info">No transaction history available for this applicant.</Alert>
                        )}
                    </TabPanel>

                    <TabPanel value={activeTab} index={4}>
                        {isLoadingAudit ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                                <CircularProgress />
                            </Box>
                        ) : auditLog && auditLog.length > 0 ? (
                            <AuditTrail auditLog={auditLog} />
                        ) : (
                            <Alert severity="info">No audit trail available for this applicant.</Alert>
                        )}
                    </TabPanel>
                </Box>
            </Paper>
        </Box>
    );
}
