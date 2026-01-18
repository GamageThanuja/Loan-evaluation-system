'use client';

import {
    Paper,
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    Chip,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';
import {
    TrendingUp,
    TrendingDown,
    CreditScore,
    AccountBalance,
    CalendarToday,
    Assessment,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CreditProfile } from '@/types';
import { formatDate } from '@/lib/utils';

interface CreditHistoryProps {
    creditProfile: CreditProfile;
}

function InfoCard({
    title,
    value,
    icon,
    color,
    subtitle,
}: {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
}) {
    return (
        <Card sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                        <Typography color="text.secondary" variant="caption" gutterBottom>
                            {title}
                        </Typography>
                        <Typography variant="h5" component="div" fontWeight={700}>
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

const getCreditScoreColor = (score: number) => {
    if (score >= 750) return '#2e7d32';
    if (score >= 650) return '#f59e0b';
    return '#d32f2f';
};

const getCreditScoreLabel = (score: number) => {
    if (score >= 750) return 'Excellent';
    if (score >= 700) return 'Good';
    if (score >= 650) return 'Fair';
    if (score >= 600) return 'Poor';
    return 'Very Poor';
};

export default function CreditHistory({ creditProfile }: CreditHistoryProps) {
    // Add null safety check
    if (!creditProfile) {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Credit History Available
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Credit information will appear here once available.
                </Typography>
            </Box>
        );
    }

    // Safe defaults for all properties
    const safeProfile = {
        currentScore: creditProfile.currentScore ?? 0,
        scoreHistory: creditProfile.scoreHistory ?? [],
        creditUtilization: creditProfile.creditUtilization ?? 0,
        totalCreditLines: creditProfile.totalCreditLines ?? 0,
        oldestAccount: creditProfile.oldestAccount ?? '',
        recentInquiries: creditProfile.recentInquiries ?? 0,
        delinquencies: creditProfile.delinquencies ?? 0,
        publicRecords: creditProfile.publicRecords ?? 0,
        averageAccountAge: creditProfile.averageAccountAge ?? 0,
    };

    const scoreColor = getCreditScoreColor(safeProfile.currentScore);
    const scoreLabel = getCreditScoreLabel(safeProfile.currentScore);

    // Prepare chart data
    const chartData = safeProfile.scoreHistory
        .slice()
        .reverse()
        .map((entry) => ({
            date: new Date(entry.date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
            score: entry.creditScore,
            fullDate: formatDate(entry.date),
        }));

    // Calculate trend
    const latestScore = safeProfile.scoreHistory[0]?.creditScore || 0;
    const previousScore = safeProfile.scoreHistory[1]?.creditScore || latestScore;
    const scoreTrend = latestScore - previousScore;

    return (
        <Box>
            {/* Credit Score Overview */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${scoreColor}20 0%, ${scoreColor}05 100%)` }}>
                        <CardContent>
                            <Box sx={{ textAlign: 'center', py: 2 }}>
                                <Typography variant="caption" color="text.secondary" gutterBottom>
                                    Current Credit Score
                                </Typography>
                                <Typography variant="h2" fontWeight={700} color={scoreColor} sx={{ my: 1 }}>
                                    {safeProfile.currentScore}
                                </Typography>
                                <Chip
                                    label={scoreLabel}
                                    sx={{
                                        bgcolor: scoreColor,
                                        color: 'white',
                                        fontWeight: 600,
                                    }}
                                />
                                {scoreTrend !== 0 && (
                                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 2 }}>
                                        {scoreTrend > 0 ? (
                                            <TrendingUp sx={{ color: '#2e7d32', mr: 0.5 }} />
                                        ) : (
                                            <TrendingDown sx={{ color: '#d32f2f', mr: 0.5 }} />
                                        )}
                                        <Typography
                                            variant="body2"
                                            color={scoreTrend > 0 ? 'success.main' : 'error.main'}
                                            fontWeight={600}
                                        >
                                            {scoreTrend > 0 ? '+' : ''}{scoreTrend} points
                                        </Typography>
                                    </Box>
                                )}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={8}>
                    <Grid container spacing={2}>
                        <Grid item xs={6} sm={6}>
                            <InfoCard
                                title="Credit Utilization"
                                value={`${((safeProfile.creditUtilization || 0) * 100).toFixed(1)}%`}
                                icon={<CreditScore />}
                                color="#1976d2"
                            />
                        </Grid>
                        <Grid item xs={6} sm={6}>
                            <InfoCard
                                title="Total Credit Lines"
                                value={safeProfile.totalCreditLines}
                                icon={<AccountBalance />}
                                color="#9c27b0"
                            />
                        </Grid>
                        <Grid item xs={6} sm={6}>
                            <InfoCard
                                title="Account Age"
                                value={`${safeProfile.averageAccountAge} yrs`}
                                icon={<CalendarToday />}
                                color="#f59e0b"
                                subtitle="Average"
                            />
                        </Grid>
                        <Grid item xs={6} sm={6}>
                            <InfoCard
                                title="Recent Inquiries"
                                value={safeProfile.recentInquiries}
                                icon={<Assessment />}
                                color={safeProfile.recentInquiries > 3 ? '#d32f2f' : '#2e7d32'}
                            />
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>

            {/* Credit Score Trend Chart */}
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                    Credit Score Trend
                </Typography>
                <Box sx={{ width: '100%', height: 300, mt: 2 }}>
                    <ResponsiveContainer>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                            <XAxis
                                dataKey="date"
                                tick={{ fontSize: 12 }}
                                stroke="#666"
                            />
                            <YAxis
                                domain={[300, 850]}
                                tick={{ fontSize: 12 }}
                                stroke="#666"
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'white',
                                    border: '1px solid #e0e0e0',
                                    borderRadius: 8,
                                }}
                                labelFormatter={(label, payload) => {
                                    if (payload && payload[0]) {
                                        return payload[0].payload.fullDate;
                                    }
                                    return label;
                                }}
                            />
                            <Line
                                type="monotone"
                                dataKey="score"
                                stroke={scoreColor}
                                strokeWidth={3}
                                dot={{ fill: scoreColor, r: 5 }}
                                activeDot={{ r: 7 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </Box>
            </Paper>

            {/* Credit History Details */}
            <Paper>
                <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="h6" fontWeight={600}>
                        Credit History Details
                    </Typography>
                </Box>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Date</TableCell>
                                <TableCell>Bureau</TableCell>
                                <TableCell align="right">Score</TableCell>
                                <TableCell align="right">Change</TableCell>
                                <TableCell>Reason</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {safeProfile.scoreHistory.map((entry) => (
                                <TableRow key={entry.id} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                                    <TableCell>
                                        <Typography variant="body2">
                                            {formatDate(entry.date)}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Chip label={entry.bureau} size="small" variant="outlined" />
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography variant="body2" fontWeight={600}>
                                            {entry.creditScore}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        {entry.change !== undefined && entry.change !== 0 && (
                                            <Chip
                                                label={`${entry.change > 0 ? '+' : ''}${entry.change}`}
                                                size="small"
                                                sx={{
                                                    bgcolor: entry.change > 0 ? '#e8f5e9' : '#ffebee',
                                                    color: entry.change > 0 ? '#2e7d32' : '#d32f2f',
                                                    fontWeight: 600,
                                                }}
                                            />
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2" color="text.secondary">
                                            {entry.reason || '-'}
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
