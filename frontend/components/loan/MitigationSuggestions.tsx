'use client';

import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Paper,
    Chip,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    LinearProgress,
    Alert,
    Accordion,
    AccordionSummary,
    AccordionDetails,
} from '@mui/material';
import {
    CheckCircle,
    TrendingUp,
    Schedule,
    ExpandMore,
    Lightbulb,
    Warning,
    Info,
    Star,
} from '@mui/icons-material';

interface Suggestion {
    id: string;
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
    category: string;
    actionItems: string[];
    expectedImpact: number; // 0-100
    timeline: string;
    difficulty: 'easy' | 'moderate' | 'challenging';
}

interface BusinessRule {
    rule: string;
    passed: boolean;
    description: string;
    suggestion?: string;
}

interface MitigationSuggestionsProps {
    riskScore: number;
    decision: 'APPROVE' | 'REJECT' | 'MANUAL_REVIEW';
    creditScore?: number;
    debtToIncomeRatio?: number;
    employmentLength?: number;
    businessRules?: BusinessRule[];
}

export default function MitigationSuggestions({
    riskScore,
    decision,
    creditScore = 720,
    debtToIncomeRatio = 0.28,
    employmentLength = 8,
    businessRules = [],
}: MitigationSuggestionsProps) {
    // Generate suggestions based on risk factors
    const generateSuggestions = (): Suggestion[] => {
        const suggestions: Suggestion[] = [];

        // Credit score suggestions
        if (creditScore < 700) {
            suggestions.push({
                id: 'credit-1',
                title: 'Improve Credit Score',
                description: 'Your credit score is below the optimal threshold. Improving it will significantly increase approval chances.',
                priority: 'high',
                category: 'Credit',
                actionItems: [
                    'Pay down credit card balances to below 30% utilization',
                    'Make all payments on time for the next 6 months',
                    'Dispute any errors on your credit report',
                    'Avoid opening new credit accounts',
                    'Consider becoming an authorized user on a well-managed account',
                ],
                expectedImpact: 85,
                timeline: '6-12 months',
                difficulty: 'moderate',
            });
        }

        // Debt-to-income ratio suggestions
        if (debtToIncomeRatio > 0.36) {
            suggestions.push({
                id: 'debt-1',
                title: 'Reduce Debt-to-Income Ratio',
                description: 'Your debt-to-income ratio is above the recommended threshold. Lowering it will improve your financial profile.',
                priority: 'high',
                category: 'Debt Management',
                actionItems: [
                    `Reduce monthly debt payments by $${Math.round((debtToIncomeRatio - 0.36) * 5000)}`,
                    'Consider debt consolidation to lower monthly payments',
                    'Increase your income through additional work or side business',
                    'Pay off smaller debts first to reduce number of obligations',
                    'Avoid taking on new debt',
                ],
                expectedImpact: 75,
                timeline: '3-6 months',
                difficulty: 'challenging',
            });
        }

        // Employment suggestions
        if (employmentLength < 2) {
            suggestions.push({
                id: 'employment-1',
                title: 'Strengthen Employment History',
                description: 'A longer employment history demonstrates stability and reduces risk.',
                priority: 'medium',
                category: 'Employment',
                actionItems: [
                    `Maintain current employment for ${24 - employmentLength} more months`,
                    'Provide additional documentation of income stability',
                    'Consider a co-signer with longer employment history',
                    'Document any previous employment in the same field',
                ],
                expectedImpact: 60,
                timeline: `${24 - employmentLength} months`,
                difficulty: 'easy',
            });
        }

        // General improvement suggestions
        if (decision !== 'APPROVE') {
            suggestions.push({
                id: 'general-1',
                title: 'Build Emergency Fund',
                description: 'Having 3-6 months of expenses saved demonstrates financial responsibility.',
                priority: 'medium',
                category: 'Financial Health',
                actionItems: [
                    'Save at least 3 months of living expenses',
                    'Open a dedicated savings account',
                    'Set up automatic transfers to savings',
                    'Reduce discretionary spending',
                ],
                expectedImpact: 50,
                timeline: '6-12 months',
                difficulty: 'moderate',
            });

            suggestions.push({
                id: 'general-2',
                title: 'Consider Alternative Loan Options',
                description: 'Exploring different loan products might better match your current financial situation.',
                priority: 'low',
                category: 'Alternatives',
                actionItems: [
                    'Apply for a smaller loan amount',
                    'Consider a secured loan with collateral',
                    'Explore loans with a co-signer',
                    'Look into credit union options',
                    'Consider a longer repayment term to lower monthly payments',
                ],
                expectedImpact: 70,
                timeline: 'Immediate',
                difficulty: 'easy',
            });
        }

        // Sort by priority
        const priorityOrder = { high: 0, medium: 1, low: 2 };
        return suggestions.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    };

    const suggestions = generateSuggestions();

    const getPriorityColor = (priority: 'high' | 'medium' | 'low') => {
        if (priority === 'high') return 'error';
        if (priority === 'medium') return 'warning';
        return 'info';
    };

    const getDifficultyColor = (difficulty: 'easy' | 'moderate' | 'challenging') => {
        if (difficulty === 'easy') return 'success';
        if (difficulty === 'moderate') return 'warning';
        return 'error';
    };

    // Calculate potential improvement
    const potentialImprovement = suggestions.reduce((sum, s) => sum + (s.expectedImpact * 0.01), 0) / suggestions.length;
    const improvedScore = Math.min(100, Math.round((1 - riskScore) * 100 + potentialImprovement * 20));

    return (
        <Box>
            {/* Overview */}
            {decision !== 'APPROVE' && (
                <Alert severity="info" sx={{ mb: 3 }} icon={<Lightbulb />}>
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                        Improvement Potential
                    </Typography>
                    <Typography variant="body2">
                        By following these suggestions, you could potentially improve your approval chances by up to{' '}
                        <strong>{Math.round(potentialImprovement * 100)}%</strong> and achieve a risk score of{' '}
                        <strong>{improvedScore}%</strong>.
                    </Typography>
                </Alert>
            )}

            {/* Priority Recommendations */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                        Priority Recommendations
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Focus on these high-impact actions first to maximize your chances of approval.
                    </Typography>

                    <Grid container spacing={2}>
                        {suggestions.map((suggestion) => (
                            <Grid item xs={12} key={suggestion.id}>
                                <Accordion>
                                    <AccordionSummary expandIcon={<ExpandMore />}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', pr: 2 }}>
                                            <Star color={suggestion.priority === 'high' ? 'error' : suggestion.priority === 'medium' ? 'warning' : 'action'} />
                                            <Box sx={{ flexGrow: 1 }}>
                                                <Typography variant="subtitle1" fontWeight={600}>
                                                    {suggestion.title}
                                                </Typography>
                                                <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                                                    <Chip
                                                        label={suggestion.priority.toUpperCase()}
                                                        size="small"
                                                        color={getPriorityColor(suggestion.priority)}
                                                    />
                                                    <Chip
                                                        label={suggestion.category}
                                                        size="small"
                                                        variant="outlined"
                                                    />
                                                </Box>
                                            </Box>
                                        </Box>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                            {suggestion.description}
                                        </Typography>

                                        <Grid container spacing={2} sx={{ mb: 2 }}>
                                            <Grid item xs={12} sm={4}>
                                                <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                    <TrendingUp color="success" />
                                                    <Typography variant="caption" display="block" color="text.secondary">
                                                        Expected Impact
                                                    </Typography>
                                                    <Typography variant="h6" fontWeight={600}>
                                                        {suggestion.expectedImpact}%
                                                    </Typography>
                                                    <LinearProgress
                                                        variant="determinate"
                                                        value={suggestion.expectedImpact}
                                                        sx={{ mt: 1 }}
                                                        color="success"
                                                    />
                                                </Paper>
                                            </Grid>
                                            <Grid item xs={12} sm={4}>
                                                <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                    <Schedule color="primary" />
                                                    <Typography variant="caption" display="block" color="text.secondary">
                                                        Timeline
                                                    </Typography>
                                                    <Typography variant="h6" fontWeight={600}>
                                                        {suggestion.timeline}
                                                    </Typography>
                                                </Paper>
                                            </Grid>
                                            <Grid item xs={12} sm={4}>
                                                <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                    <Info color={getDifficultyColor(suggestion.difficulty)} />
                                                    <Typography variant="caption" display="block" color="text.secondary">
                                                        Difficulty
                                                    </Typography>
                                                    <Typography variant="h6" fontWeight={600} textTransform="capitalize">
                                                        {suggestion.difficulty}
                                                    </Typography>
                                                </Paper>
                                            </Grid>
                                        </Grid>

                                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                            Action Items:
                                        </Typography>
                                        <List dense>
                                            {suggestion.actionItems.map((item, index) => (
                                                <ListItem key={index}>
                                                    <ListItemIcon sx={{ minWidth: 36 }}>
                                                        <CheckCircle fontSize="small" color="action" />
                                                    </ListItemIcon>
                                                    <ListItemText primary={item} />
                                                </ListItem>
                                            ))}
                                        </List>
                                    </AccordionDetails>
                                </Accordion>
                            </Grid>
                        ))}
                    </Grid>
                </CardContent>
            </Card>

            {/* Business Rules */}
            {businessRules.length > 0 && (
                <Card>
                    <CardContent>
                        <Typography variant="h6" gutterBottom fontWeight={600}>
                            Business Rules Assessment
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            These are the specific lending criteria evaluated for your application.
                        </Typography>

                        <List>
                            {businessRules.map((rule, index) => (
                                <ListItem key={index} sx={{ bgcolor: 'background.default', mb: 1, borderRadius: 1 }}>
                                    <ListItemIcon>
                                        {rule.passed ? (
                                            <CheckCircle color="success" />
                                        ) : (
                                            <Warning color="error" />
                                        )}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={
                                            <Typography variant="subtitle2" fontWeight={600}>
                                                {rule.rule}
                                            </Typography>
                                        }
                                        secondary={
                                            <>
                                                <Typography variant="body2" color="text.secondary">
                                                    {rule.description}
                                                </Typography>
                                                {!rule.passed && rule.suggestion && (
                                                    <Typography variant="body2" color="primary" sx={{ mt: 0.5 }}>
                                                        💡 {rule.suggestion}
                                                    </Typography>
                                                )}
                                            </>
                                        }
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </CardContent>
                </Card>
            )}
        </Box>
    );
}
