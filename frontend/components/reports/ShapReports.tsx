'use client';

import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Paper,
    Chip,
} from '@mui/material';
import {
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

interface ShapReportsProps {
    // You can pass actual SHAP data here when available
    applicantId?: string;
}

export default function ShapReports({ applicantId }: ShapReportsProps) {
    // Mock SHAP data - replace with actual data from API
    const featureImportance = [
        { feature: 'Credit Score', importance: 0.28, impact: 'positive' },
        { feature: 'Income Level', importance: 0.22, impact: 'positive' },
        { feature: 'Debt-to-Income Ratio', importance: 0.18, impact: 'negative' },
        { feature: 'Employment Length', importance: 0.12, impact: 'positive' },
        { feature: 'Age', importance: 0.08, impact: 'positive' },
        { feature: 'Loan Amount', importance: 0.06, impact: 'negative' },
        { feature: 'Previous Defaults', importance: 0.04, impact: 'negative' },
        { feature: 'Education Level', importance: 0.02, impact: 'positive' },
    ];

    // Feature distribution for pie chart
    const featureDistribution = [
        { name: 'Financial Factors', value: 48, color: '#1976d2' },
        { name: 'Employment Factors', value: 20, color: '#2e7d32' },
        { name: 'Personal Factors', value: 18, color: '#f59e0b' },
        { name: 'Credit History', value: 14, color: '#d32f2f' },
    ];

    // Impact breakdown
    const impactData = [
        { category: 'Positive Impact', value: 70, color: '#2e7d32' },
        { category: 'Negative Impact', value: 28, color: '#d32f2f' },
        { category: 'Neutral', value: 2, color: '#757575' },
    ];

    // SHAP values heatmap data (simplified)
    const shapHeatmapData = [
        { feature: 'Credit Score', low: -0.15, medium: 0.05, high: 0.28 },
        { feature: 'Income', low: -0.12, medium: 0.08, high: 0.22 },
        { feature: 'DTI Ratio', low: 0.18, medium: 0.05, high: -0.18 },
        { feature: 'Employment', low: -0.08, medium: 0.02, high: 0.12 },
        { feature: 'Age', low: -0.05, medium: 0.02, high: 0.08 },
    ];

    const COLORS = ['#1976d2', '#2e7d32', '#f59e0b', '#d32f2f'];

    const getImpactColor = (impact: string) => {
        return impact === 'positive' ? '#2e7d32' : impact === 'negative' ? '#d32f2f' : '#757575';
    };

    return (
        <Box>
            <Typography variant="h5" gutterBottom fontWeight={700} sx={{ mb: 3 }}>
                SHAP Explainability Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                Comprehensive SHAP (SHapley Additive exPlanations) visualizations showing feature importance and impact on model predictions
            </Typography>

            <Grid container spacing={3}>
                {/* Feature Importance Bar Chart */}
                <Grid item xs={12} lg={8}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom fontWeight={600}>
                                Feature Importance (SHAP Values)
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Bar chart showing the absolute mean SHAP values for each feature
                            </Typography>
                            <ResponsiveContainer width="100%" height={400}>
                                <BarChart
                                    data={featureImportance}
                                    layout="vertical"
                                    margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis type="number" domain={[0, 0.3]} />
                                    <YAxis dataKey="feature" type="category" />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="importance" name="SHAP Importance" radius={[0, 8, 8, 0]}>
                                        {featureImportance.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={getImpactColor(entry.impact)} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                            <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'center' }}>
                                <Chip label="Positive Impact" size="small" sx={{ bgcolor: '#2e7d32', color: 'white' }} />
                                <Chip label="Negative Impact" size="small" sx={{ bgcolor: '#d32f2f', color: 'white' }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Impact Distribution Pie Chart */}
                <Grid item xs={12} lg={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom fontWeight={600}>
                                Overall Impact Distribution
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Breakdown of positive vs negative feature impacts
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={impactData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, value }) => `${name}: ${value}%`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {impactData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Feature Category Distribution */}
                <Grid item xs={12} lg={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom fontWeight={600}>
                                Feature Category Distribution
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Contribution by feature category
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={featureDistribution}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={true}
                                        label={({ name, value }) => `${name} (${value}%)`}
                                        outerRadius={100}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {featureDistribution.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* SHAP Heatmap Simulation */}
                <Grid item xs={12} lg={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom fontWeight={600}>
                                SHAP Values by Feature Range
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Impact of features across different value ranges
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={shapHeatmapData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="feature" />
                                    <YAxis domain={[-0.2, 0.3]} />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="low" fill="#d32f2f" name="Low Range" />
                                    <Bar dataKey="medium" fill="#f59e0b" name="Medium Range" />
                                    <Bar dataKey="high" fill="#2e7d32" name="High Range" />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Summary Statistics */}
                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom fontWeight={600}>
                                SHAP Analysis Summary
                            </Typography>
                            <Grid container spacing={2} sx={{ mt: 1 }}>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light' }}>
                                        <Typography variant="caption" color="primary.dark">
                                            Top Feature
                                        </Typography>
                                        <Typography variant="h6" fontWeight={600} color="primary.dark">
                                            Credit Score
                                        </Typography>
                                        <Typography variant="body2" color="primary.dark">
                                            28% Impact
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light' }}>
                                        <Typography variant="caption" color="success.dark">
                                            Positive Features
                                        </Typography>
                                        <Typography variant="h6" fontWeight={600} color="success.dark">
                                            5 / 8
                                        </Typography>
                                        <Typography variant="body2" color="success.dark">
                                            62.5%
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'error.light' }}>
                                        <Typography variant="caption" color="error.dark">
                                            Negative Features
                                        </Typography>
                                        <Typography variant="h6" fontWeight={600} color="error.dark">
                                            3 / 8
                                        </Typography>
                                        <Typography variant="body2" color="error.dark">
                                            37.5%
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.light' }}>
                                        <Typography variant="caption" color="warning.dark">
                                            Avg SHAP Value
                                        </Typography>
                                        <Typography variant="h6" fontWeight={600} color="warning.dark">
                                            0.125
                                        </Typography>
                                        <Typography variant="body2" color="warning.dark">
                                            Moderate Impact
                                        </Typography>
                                    </Paper>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}
