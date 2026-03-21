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
    TextField,
    InputAdornment,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
} from '@mui/material';
import {
    Payment,
    TrendingUp,
    TrendingDown,
    Receipt,
    Refresh,
    Search,
} from '@mui/icons-material';
import { useState } from 'react';
import { Transaction } from '@/types';
import { formatCurrency, formatDate } from '@/lib/utils';

interface TransactionListProps {
    transactions: Transaction[];
}

const getTransactionIcon = (type: Transaction['type']) => {
    switch (type) {
        case 'payment':
            return <Payment fontSize="small" />;
        case 'disbursement':
            return <TrendingUp fontSize="small" />;
        case 'fee':
        case 'penalty':
            return <TrendingDown fontSize="small" />;
        case 'refund':
            return <Refresh fontSize="small" />;
        default:
            return <Receipt fontSize="small" />;
    }
};

const getTransactionColor = (type: Transaction['type']) => {
    switch (type) {
        case 'payment':
            return '#2e7d32';
        case 'disbursement':
            return '#1976d2';
        case 'fee':
        case 'penalty':
            return '#d32f2f';
        case 'refund':
            return '#f59e0b';
        default:
            return '#666';
    }
};

const getStatusColor = (status: Transaction['status']) => {
    switch (status) {
        case 'completed':
            return 'success';
        case 'pending':
            return 'warning';
        case 'failed':
            return 'error';
        case 'reversed':
            return 'default';
        default:
            return 'default';
    }
};

export default function TransactionList({ transactions }: TransactionListProps) {
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState<string>('all');
    const [filterStatus, setFilterStatus] = useState<string>('all');

    // Add null safety check
    if (!transactions || transactions.length === 0) {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Previous Transactions
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    This applicant has no transaction history. Transactions will appear here once loan activity begins.
                </Typography>
            </Box>
        );
    }

    // Filter transactions
    const filteredTransactions = transactions.filter((transaction) => {
        const matchesSearch =
            (transaction.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
            (transaction.referenceNumber || '').toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = filterType === 'all' || transaction.type === filterType;
        const matchesStatus = filterStatus === 'all' || transaction.status === filterStatus;

        return matchesSearch && matchesType && matchesStatus;
    });

    // Calculate totals
    const totalDebits = filteredTransactions
        .filter((t) => ['payment', 'fee', 'penalty'].includes(t.type))
        .reduce((sum, t) => sum + t.amount, 0);

    const totalCredits = filteredTransactions
        .filter((t) => ['disbursement', 'refund'].includes(t.type))
        .reduce((sum, t) => sum + t.amount, 0);

    return (
        <Box>
            {/* Filters */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                    <TextField
                        size="small"
                        placeholder="Search transactions..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        sx={{ flexGrow: 1, minWidth: 200 }}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <Search fontSize="small" />
                                </InputAdornment>
                            ),
                        }}
                    />

                    <FormControl size="small" sx={{ minWidth: 150 }}>
                        <InputLabel>Type</InputLabel>
                        <Select
                            value={filterType}
                            label="Type"
                            onChange={(e) => setFilterType(e.target.value)}
                        >
                            <MenuItem value="all">All Types</MenuItem>
                            <MenuItem value="payment">Payment</MenuItem>
                            <MenuItem value="disbursement">Disbursement</MenuItem>
                            <MenuItem value="fee">Fee</MenuItem>
                            <MenuItem value="refund">Refund</MenuItem>
                            <MenuItem value="penalty">Penalty</MenuItem>
                        </Select>
                    </FormControl>

                    <FormControl size="small" sx={{ minWidth: 150 }}>
                        <InputLabel>Status</InputLabel>
                        <Select
                            value={filterStatus}
                            label="Status"
                            onChange={(e) => setFilterStatus(e.target.value)}
                        >
                            <MenuItem value="all">All Status</MenuItem>
                            <MenuItem value="completed">Completed</MenuItem>
                            <MenuItem value="pending">Pending</MenuItem>
                            <MenuItem value="failed">Failed</MenuItem>
                            <MenuItem value="reversed">Reversed</MenuItem>
                        </Select>
                    </FormControl>
                </Box>

                {/* Summary */}
                <Box sx={{ display: 'flex', gap: 3, mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                    <Box>
                        <Typography variant="caption" color="text.secondary">
                            Total Debits
                        </Typography>
                        <Typography variant="h6" fontWeight={600} color="error.main">
                            {formatCurrency(totalDebits)}
                        </Typography>
                    </Box>
                    <Box>
                        <Typography variant="caption" color="text.secondary">
                            Total Credits
                        </Typography>
                        <Typography variant="h6" fontWeight={600} color="success.main">
                            {formatCurrency(totalCredits)}
                        </Typography>
                    </Box>
                    <Box>
                        <Typography variant="caption" color="text.secondary">
                            Net Amount
                        </Typography>
                        <Typography variant="h6" fontWeight={600}>
                            {formatCurrency(totalCredits - totalDebits)}
                        </Typography>
                    </Box>
                </Box>
            </Paper>

            {/* Transactions Table */}
            <Paper>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Date</TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell>Description</TableCell>
                                <TableCell align="right">Amount</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Payment Method</TableCell>
                                <TableCell>Reference</TableCell>
                                <TableCell align="right">Balance</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {filteredTransactions.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                                        <Typography variant="body2" color="text.secondary">
                                            No transactions found
                                        </Typography>
                                    </TableCell>
                                </TableRow>
                            ) : (
                                filteredTransactions.map((transaction) => {
                                    const isDebit = ['payment', 'fee', 'penalty'].includes(transaction.type);
                                    const color = getTransactionColor(transaction.type);

                                    return (
                                        <TableRow
                                            key={transaction.id}
                                            sx={{
                                                '&:hover': { bgcolor: 'action.hover' },
                                                transition: 'background-color 0.2s',
                                            }}
                                        >
                                            <TableCell>
                                                <Typography variant="body2">
                                                    {formatDate(transaction.date)}
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">
                                                    {new Date(transaction.date).toLocaleTimeString()}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    icon={getTransactionIcon(transaction.type)}
                                                    label={transaction.type.replace(/_/g, ' ').toUpperCase()}
                                                    size="small"
                                                    sx={{
                                                        bgcolor: `${color}20`,
                                                        color: color,
                                                        fontWeight: 600,
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" fontWeight={500}>
                                                    {transaction.description}
                                                </Typography>
                                                {transaction.notes && (
                                                    <Typography variant="caption" color="text.secondary" display="block">
                                                        {transaction.notes}
                                                    </Typography>
                                                )}
                                            </TableCell>
                                            <TableCell align="right">
                                                <Typography
                                                    variant="body2"
                                                    fontWeight={600}
                                                    color={isDebit ? 'error.main' : 'success.main'}
                                                >
                                                    {isDebit ? '-' : '+'}{formatCurrency(transaction.amount)}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={transaction.status.toUpperCase()}
                                                    size="small"
                                                    color={getStatusColor(transaction.status)}
                                                    variant={transaction.status === 'pending' ? 'outlined' : 'filled'}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                {transaction.paymentMethod ? (
                                                    <Chip
                                                        label={transaction.paymentMethod.replace(/_/g, ' ')}
                                                        size="small"
                                                        variant="outlined"
                                                    />
                                                ) : (
                                                    <Typography variant="body2" color="text.secondary">
                                                        -
                                                    </Typography>
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="caption" color="text.secondary">
                                                    {transaction.referenceNumber || '-'}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="right">
                                                <Typography variant="body2" fontWeight={600}>
                                                    {formatCurrency(transaction.balance)}
                                                </Typography>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </Box>
    );
}
