'use client';

import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Chip,
    LinearProgress,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';
import {
    CheckCircle,
    Cancel,
    Warning,
    TrendingUp,
    TrendingDown,
} from '@mui/icons-material';

interface RiskFactor {
    name: string;
    value: number | string;
    threshold: number | string;
    status: 'good' | 'warning' | 'bad';
    impact: 'high' | 'medium' | 'low';
    description: string;
}

interface RiskAssessmentProps {
    riskScore: number; // 0-1 scale
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
    confidence: number; // 0-1 scale
    decision: 'APPROVE' | 'REJECT' | 'MANUAL_REVIEW';
    riskFactors?: RiskFactor[];
}

export default function RiskAssessment({
    riskScore,
    riskLevel,
    confidence,
    decision,
    riskFactors = [],
}: RiskAssessmentProps) {
    const getRiskColor = () => {
        if (riskLevel === 'LOW') return 'success';
        if (riskLevel === 'MEDIUM') return 'warning';
        return 'error';
    };

    const getDecisionColor = () => {
        if (decision === 'APPROVE') return 'success';
        if (decision === 'REJECT') return 'error';
        return 'warning';
    };

    const getStatusIcon = (status: 'good' | 'warning' | 'bad') => {
        if (status === 'good') return <CheckCircle color="success" fontSize="small" />;
        if (status === 'warning') return <Warning color="warning" fontSize="small" />;
        return <Cancel color="error" fontSize="small" />;
    };

    const getImpactColor = (impact: 'high' | 'medium' | 'low') => {
        if (impact === 'high') return 'error';
        if (impact === 'medium') return 'warning';
        return 'info';
    };

    // Calculate risk percentage
    const riskPercentage = Math.round(riskScore * 100);
    const confidencePercentage = Math.round(confidence * 100);

    return (
        <Box>
            {/* Risk Score Gauge */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom fontWeight={600}>
                                Risk Score
                            </Typography>

                            <Box sx={{ position: 'relative', display: 'inline-flex', my: 3 }}>
                                <Box
                                    sx={{
                                        position: 'relative',
                                        display: 'inline-flex',
                                        width: 200,
                                        height: 200,
                                        borderRadius: '50%',
                                        background: `conic-gradient(
                                            ${riskLevel === 'LOW' ? '#4caf50' : riskLevel === 'MEDIUM' ? '#ff9800' : '#f44336'} ${riskPercentage * 3.6}deg,
                                            #e0e0e0 ${riskPercentage * 3.6}deg
                                        )`,
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <Box
                                        sx={{
                                            width: 160,
                                            height: 160,
                                            borderRadius: '50%',
                                            bgcolor: 'background.paper',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                        }}
                                    >
                                        <Typography variant="h3" fontWeight={700} color={getRiskColor()}>
                                            {riskPercentage}%
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Risk Score
                                        </Typography>
                                    </Box>
                                </Box>
                            </Box>

                            <Box sx={{ mt: 2 }}>
                                <Chip
                                    label={`${riskLevel} RISK`}
                                    color={getRiskColor()}
                                    size="large"
                                    sx={{ fontWeight: 600, fontSize: '1rem', px: 2 }}
                                />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom fontWeight={600}>
                                Decision Summary
                            </Typography>

                            <Box sx={{ my: 3 }}>
                                <Box sx={{ mb: 3 }}>
                                    <Typography variant="caption" color="text.secondary" gutterBottom>
                                        Recommendation
                                    </Typography>
                                    <Box sx={{ mt: 1 }}>
                                        <Chip
                                            label={decision.replace('_', ' ')}
                                            color={getDecisionColor()}
                                            size="large"
                                            sx={{ fontWeight: 600, fontSize: '1rem', px: 2 }}
                                        />
                                    </Box>
                                </Box>

                                <Box sx={{ mb: 3 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                        <Typography variant="caption" color="text.secondary">
                                            Model Confidence
                                        </Typography>
                                        <Typography variant="caption" fontWeight={600}>
                                            {confidencePercentage}%
                                        </Typography>
                                    </Box>
                                    <LinearProgress
                                        variant="determinate"
                                        value={confidencePercentage}
                                        sx={{ height: 8, borderRadius: 1 }}
                                        color={confidencePercentage > 80 ? 'success' : confidencePercentage > 60 ? 'warning' : 'error'}
                                    />
                                </Box>

                                <Paper sx={{ p: 2, bgcolor: 'info.light' }}>
                                    <Typography variant="body2" color="info.dark">
                                        {decision === 'APPROVE' && 'The model recommends approving this loan application based on the risk assessment.'}
                                        {decision === 'REJECT' && 'The model recommends rejecting this loan application due to high risk factors.'}
                                        {decision === 'MANUAL_REVIEW' && 'This application requires manual review by a loan officer due to borderline risk factors.'}
                                    </Typography>
                                </Paper>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Risk Metrics */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                        Risk Metrics Breakdown
                    </Typography>

                    <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary">
                                    Credit Risk
                                </Typography>
                                <Typography variant="h5" fontWeight={600} color="success.main" sx={{ my: 1 }}>
                                    {Math.round((1 - riskScore) * 100)}%
                                </Typography>
                                <TrendingUp color="success" />
                            </Paper>
                        </Grid>

                        <Grid item xs={12} sm={6} md={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary">
                                    Income Stability
                                </Typography>
                                <Typography variant="h5" fontWeight={600} color="success.main" sx={{ my: 1 }}>
                                    85%
                                </Typography>
                                <TrendingUp color="success" />
                            </Paper>
                        </Grid>

                        <Grid item xs={12} sm={6} md={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary">
                                    Employment Risk
                                </Typography>
                                <Typography variant="h5" fontWeight={600} color="warning.main" sx={{ my: 1 }}>
                                    {Math.round(riskScore * 50)}%
                                </Typography>
                                <TrendingDown color="warning" />
                            </Paper>
                        </Grid>

                        <Grid item xs={12} sm={6} md={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary">
                                    Debt-to-Income
                                </Typography>
                                <Typography variant="h5" fontWeight={600} color="success.main" sx={{ my: 1 }}>
                                    28%
                                </Typography>
                                <TrendingUp color="success" />
                            </Paper>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {/* Risk Factors Table */}
            {riskFactors.length > 0 && (
                <Card>
                    <CardContent>
                        <Typography variant="h6" gutterBottom fontWeight={600}>
                            Risk Factor Analysis
                        </Typography>

                        <TableContainer sx={{ mt: 2 }}>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Factor</TableCell>
                                        <TableCell>Current Value</TableCell>
                                        <TableCell>Threshold</TableCell>
                                        <TableCell>Status</TableCell>
                                        <TableCell>Impact</TableCell>
                                        <TableCell>Description</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {riskFactors.map((factor, index) => (
                                        <TableRow key={index}>
                                            <TableCell>
                                                <Typography variant="body2" fontWeight={600}>
                                                    {factor.name}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>{factor.value}</TableCell>
                                            <TableCell>{factor.threshold}</TableCell>
                                            <TableCell>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    {getStatusIcon(factor.status)}
                                                    <Typography variant="caption" textTransform="capitalize">
                                                        {factor.status}
                                                    </Typography>
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={factor.impact}
                                                    size="small"
                                                    color={getImpactColor(factor.impact)}
                                                    variant="outlined"
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="caption" color="text.secondary">
                                                    {factor.description}
                                                </Typography>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </CardContent>
                </Card>
            )}
        </Box>
    );
}
