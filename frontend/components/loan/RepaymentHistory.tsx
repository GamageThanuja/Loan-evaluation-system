'use client';

import {
    Paper,
    Typography,
    Box,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    LinearProgress,
    Grid,
    Card,
    CardContent,
} from '@mui/material';
import {
    CheckCircle,
    Schedule,
    Warning,
    TrendingUp,
    CalendarToday,
    AttachMoney,
} from '@mui/icons-material';
import { RepaymentSchedule, RepaymentSummary } from '@/types';
import { formatCurrency, formatDate } from '@/lib/utils';

interface RepaymentHistoryProps {
    schedule: RepaymentSchedule[];
    summary: RepaymentSummary;
}

function StatCard({
    title,
    value,
    icon,
    color,
}: {
    title: string;
    value: string;
    icon: React.ReactNode;
    color: string;
}) {
    return (
        <Card sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                        <Typography color="text.secondary" variant="caption" gutterBottom>
                            {title}
                        </Typography>
                        <Typography variant="h6" component="div" fontWeight={700}>
                            {value}
                        </Typography>
                    </Box>
                    <Box
                        sx={{
                            p: 1,
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

const getStatusColor = (status: RepaymentSchedule['status']) => {
    switch (status) {
        case 'paid':
            return 'success';
        case 'overdue':
            return 'error';
        case 'partial':
            return 'warning';
        default:
            return 'default';
    }
};

const getStatusIcon = (status: RepaymentSchedule['status']) => {
    switch (status) {
        case 'paid':
            return <CheckCircle fontSize="small" />;
        case 'overdue':
            return <Warning fontSize="small" />;
        default:
            return <Schedule fontSize="small" />;
    }
};

export default function RepaymentHistory({ schedule, summary }: RepaymentHistoryProps) {
    const completionPercentage = (summary.paymentsCompleted / summary.numberOfPayments) * 100;

    return (
        <Box>
            {/* Summary Cards */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Loan Amount"
                        value={formatCurrency(summary.totalLoanAmount)}
                        icon={<AttachMoney />}
                        color="#1976d2"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Paid"
                        value={formatCurrency(summary.totalPaid)}
                        icon={<CheckCircle />}
                        color="#2e7d32"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Remaining Balance"
                        value={formatCurrency(summary.totalRemaining)}
                        icon={<TrendingUp />}
                        color="#f59e0b"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Next Payment"
                        value={formatCurrency(summary.nextPaymentAmount)}
                        icon={<CalendarToday />}
                        color="#9c27b0"
                    />
                </Grid>
            </Grid>

            {/* Progress Bar */}
            <Paper sx={{ p: 3, mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" fontWeight={600}>
                        Repayment Progress
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {summary.paymentsCompleted} of {summary.numberOfPayments} payments
                    </Typography>
                </Box>
                <LinearProgress
                    variant="determinate"
                    value={completionPercentage}
                    sx={{
                        height: 10,
                        borderRadius: 5,
                        bgcolor: 'rgba(0, 0, 0, 0.05)',
                        '& .MuiLinearProgress-bar': {
                            borderRadius: 5,
                            background: 'linear-gradient(90deg, #2e7d32 0%, #66bb6a 100%)',
                        },
                    }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                    {completionPercentage.toFixed(1)}% Complete
                </Typography>
            </Paper>

            {/* Payment Schedule Table */}
            <Paper>
                <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="h6" fontWeight={600}>
                        Payment Schedule
                    </Typography>
                </Box>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>#</TableCell>
                                <TableCell>Due Date</TableCell>
                                <TableCell align="right">Principal</TableCell>
                                <TableCell align="right">Interest</TableCell>
                                <TableCell align="right">Total Amount</TableCell>
                                <TableCell align="right">Paid Amount</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell align="right">Balance</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {schedule.map((payment) => (
                                <TableRow
                                    key={payment.id}
                                    sx={{
                                        '&:hover': { bgcolor: 'action.hover' },
                                        bgcolor: payment.status === 'overdue' ? 'rgba(211, 47, 47, 0.05)' : 'inherit',
                                    }}
                                >
                                    <TableCell>
                                        <Typography variant="body2" fontWeight={600}>
                                            {payment.installmentNumber}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">
                                            {formatDate(payment.dueDate)}
                                        </Typography>
                                        {payment.paidDate && (
                                            <Typography variant="caption" color="text.secondary" display="block">
                                                Paid: {formatDate(payment.paidDate)}
                                            </Typography>
                                        )}
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography variant="body2">
                                            {formatCurrency(payment.principalAmount)}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography variant="body2">
                                            {formatCurrency(payment.interestAmount)}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography variant="body2" fontWeight={600}>
                                            {formatCurrency(payment.totalAmount)}
                                        </Typography>
                                        {payment.lateFee && payment.lateFee > 0 && (
                                            <Typography variant="caption" color="error" display="block">
                                                +{formatCurrency(payment.lateFee)} late fee
                                            </Typography>
                                        )}
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography variant="body2" color={payment.paidAmount ? 'success.main' : 'text.secondary'}>
                                            {payment.paidAmount ? formatCurrency(payment.paidAmount) : '-'}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Chip
                                            icon={getStatusIcon(payment.status)}
                                            label={payment.status.toUpperCase()}
                                            size="small"
                                            color={getStatusColor(payment.status)}
                                            variant={payment.status === 'pending' ? 'outlined' : 'filled'}
                                        />
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography variant="body2" fontWeight={600}>
                                            {formatCurrency(payment.remainingBalance)}
                                        </Typography>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </Box>
    );
}
