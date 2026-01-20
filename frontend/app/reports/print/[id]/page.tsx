'use client';

import { useEffect, useState } from 'react';
import {
    Box,
    Typography,
    Grid,
    Paper,
    Divider,
    Chip,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    LinearProgress,
} from '@mui/material';
import {
    Warning as WarningIcon,
    CheckCircle as CheckCircleIcon,
    TrendingUp as TrendingUpIcon,
    AttachMoney as MoneyIcon,
    AccountBalance as BankIcon,
    Assessment as AssessmentIcon,
} from '@mui/icons-material';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line,
} from 'recharts';
import { useApplicantOperations } from '@/hooks/useApplicants';
import { formatCurrency } from '@/utils/formatters';

interface PageProps {
    params: {
        id: string;
    };
}

// Mock data for charts (replace with real data if available from API)
const CASH_FLOW_DATA = [
    { month: 'Jan', inflow: 150000, outflow: 120000 },
    { month: 'Feb', inflow: 145000, outflow: 125000 },
    { month: 'Mar', inflow: 160000, outflow: 115000 },
    { month: 'Apr', inflow: 155000, outflow: 130000 },
    { month: 'May', inflow: 150000, outflow: 122000 },
    { month: 'Jun', inflow: 158000, outflow: 118000 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function PrintReportPage({ params }: PageProps) {
    const { id } = params;
    const { applicant, checkEligibility, isLoading } = useApplicantOperations(id);
    const [eligibilityData, setEligibilityData] = useState<any>(null);

    useEffect(() => {
        // Trigger eligibility check validation to get fresh reasoning
        if (id) {
            checkEligibility(id)
                .then((response) => {
                    if (response.success) {
                        setEligibilityData(response.data);
                    }
                })
                .catch(err => console.error("Failed to fetch eligibility", err));
        }
    }, [id, checkEligibility]);

    if (isLoading || !applicant) {
        return <Box sx={{ p: 4, textAlign: 'center' }}>Loading report data...</Box>;
    }

    // Derived Data
    const monthlyIncome = applicant.monthlyIncome || 0;
    const loanAmount = applicant.loanAmount || 0;
    const loanTerm = applicant.loanTermMonths || 12;
    const monthlyInstallment = loanAmount / loanTerm; // Simplified
    const debtToIncome = (monthlyInstallment / monthlyIncome) * 100;

    // Exposure Distribution Data
    const exposureData = [
        { name: 'Existing Loans', value: 300000 }, // Mock
        { name: 'Credit Cards', value: 50000 },   // Mock
        { name: 'Overdrafts', value: 25000 },     // Mock
        { name: 'This Request', value: loanAmount },
    ];

    return (
        <Box sx={{ p: 4, maxWidth: '210mm', mx: 'auto', bgcolor: 'white', minHeight: '100vh' }} id="report-content">
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4, borderBottom: '2px solid #1976d2', pb: 2 }}>
                <Box>
                    <Typography variant="h4" fontWeight={800} color="primary">
                        Loan Rejection Report
                    </Typography>
                    <Typography variant="subtitle1" color="text.secondary">
                        Confidential Assessment Document
                    </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="h6">{applicant.name}</Typography>
                    <Typography variant="body2">ID: {applicant.id}</Typography>
                    <Typography variant="body2">Date: {new Date().toLocaleDateString()}</Typography>
                </Box>
            </Box>

            {/* 1. AI Explainability (SHAP Analysis) */}
            <Paper elevation={0} variant="outlined" sx={{ p: 3, mb: 3, bgcolor: '#f8f9fa', borderColor: '#dee2e6' }}>
                <Typography variant="h6" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                    1. AI Explainability (SHAP Analysis)
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                    Feature importance indicating how each factor influenced the loan decision. Positive values (Red) increase rejection risk, while negative values (Green) improve eligibility.
                </Typography>

                <Box sx={{ height: 350, mt: 2 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={eligibilityData?.feature_importance || []}
                            layout="vertical"
                            margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                            <XAxis type="number" domain={[-1, 1]} hide />
                            <YAxis
                                dataKey="feature"
                                type="category"
                                width={120}
                                style={{ fontSize: '12px' }}
                            />
                            <Tooltip
                                formatter={(value: number) => [`${(value * 100).toFixed(1)}% Strength`, 'Impact']}
                            />
                            <Bar
                                dataKey="importance"
                                radius={[0, 4, 4, 0]}
                            >
                                {eligibilityData?.feature_importance?.map((entry: any, index: number) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={entry.direction === 'increases_risk' ? '#f44336' : '#4caf50'}
                                    />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </Box>
            </Paper>

            {/* 2. Key Rejection Reasons */}
            <Paper elevation={0} variant="outlined" sx={{ p: 3, mb: 3, bgcolor: '#fff5f5', borderColor: '#ffcdd2' }}>
                <Typography variant="h6" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <WarningIcon color="error" sx={{ mr: 1 }} />
                    2. Key Rejection Reasons
                </Typography>
                <Typography variant="body1" paragraph>
                    The application for <strong>{formatCurrency(loanAmount)}</strong> was declined due to the following primary concerns:
                </Typography>

                <Grid container spacing={2}>
                    {eligibilityData?.risk_analysis?.concerns?.map((reason: string, index: number) => (
                        <Grid item xs={12} key={index}>
                            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'error.main', mt: 1, mr: 2 }} />
                                <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                                    {reason}
                                </Typography>
                            </Box>
                        </Grid>
                    )) || (
                            <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
                                No detailed concerns found.
                            </Typography>
                        )}
                </Grid>
            </Paper>

            {/* 3. Eligibility Improvement Suggestions */}
            <Paper elevation={0} variant="outlined" sx={{ p: 3, mb: 3, bgcolor: '#f0f9ff', borderColor: '#b3e5fc' }}>
                <Typography variant="h6" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                    3. Eligibility Improvement Suggestions
                </Typography>
                <List dense>
                    {eligibilityData?.recommendations?.map((rec: string, index: number) => (
                        <ListItem key={index}>
                            <ListItemIcon>
                                <CheckCircleIcon color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary={rec} />
                        </ListItem>
                    )) || (
                            <ListItem>
                                <ListItemText primary="No specific recommendations available." />
                            </ListItem>
                        )}
                </List>
            </Paper>

            <Divider sx={{ my: 4 }} />

            {/* 3. Customer Profile & Exposure */}
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ mb: 2 }}>
                3. Customer Profile & Exposure
            </Typography>
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" align="center" gutterBottom>Total Exposure Distribution</Typography>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie
                                data={exposureData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {exposureData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value: number) => formatCurrency(value)} />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <Typography variant="subtitle2" gutterBottom>Debt-to-Income Ratio</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="h4" fontWeight={700} color={debtToIncome > 50 ? 'error.main' : 'warning.main'}>
                                {debtToIncome.toFixed(1)}%
                            </Typography>
                            <Typography variant="caption" sx={{ ml: 1, color: 'text.secondary' }}>(Threshold: 40%)</Typography>
                        </Box>
                        <LinearProgress
                            variant="determinate"
                            value={Math.min(debtToIncome, 100)}
                            color={debtToIncome > 50 ? 'error' : 'warning'}
                            sx={{ height: 10, borderRadius: 5 }}
                        />
                    </Box>
                </Grid>
            </Grid>

            {/* 4. Cash Flow & Repayment Capacity */}
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ mb: 2 }}>
                4. Cash Flow & Repayment Capacity
            </Typography>
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12}>
                    <Typography variant="subtitle2" align="center" gutterBottom>Analyze Monthly Inflows vs Outflows</Typography>
                    <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={CASH_FLOW_DATA}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip formatter={(value: number) => formatCurrency(value)} />
                            <Legend />
                            <Line type="monotone" dataKey="inflow" stroke="#2e7d32" strokeWidth={2} name="Total Inflow" />
                            <Line type="monotone" dataKey="outflow" stroke="#d32f2f" strokeWidth={2} name="Total Outflow" />
                        </LineChart>
                    </ResponsiveContainer>
                </Grid>
            </Grid>

            {/* 5. Collateral Analysis  */}
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ mb: 2 }}>
                5. Collateral Analysis
            </Typography>
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2, mb: 4 }}>
                <Typography variant="body2" color="text.secondary" align="center">
                    No collateral data linked to this application.
                    LTV Ratio cannot be calculated.
                </Typography>
            </Box>

            {/* 6. Risk Scoring & Decisioning */}
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ mb: 2 }}>
                6. Risk Scoring & Decisioning
            </Typography>
            <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#f5f5f5' }}>
                        <Typography variant="caption">Credit Score</Typography>
                        <Typography variant="h5" fontWeight={700}>{applicant.creditScore || 'N/A'}</Typography>
                    </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#ffebee', color: 'error.main' }}>
                        <Typography variant="caption">Default Probability</Typography>
                        <Typography variant="h5" fontWeight={700}>
                            {eligibilityData?.prediction?.probability ? (eligibilityData.prediction.probability * 100).toFixed(1) + '%' : 'N/A'}
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'error.main', color: 'white' }}>
                        <Typography variant="subtitle1">Final Decision</Typography>
                        <Typography variant="h5" fontWeight={800}>DECLINE</Typography>
                    </Paper>
                </Grid>
            </Grid>

            {/* Footer */}
            <Box sx={{ mt: 8, textAlign: 'center', color: 'text.secondary' }}>
                <Typography variant="caption">
                    Generated by Intelligent Loan Evaluation System on {new Date().toLocaleString()}
                </Typography>
            </Box>
        </Box>
    );
}
