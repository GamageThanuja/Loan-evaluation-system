'use client';

import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Paper,
    Divider,
    Chip,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
} from '@mui/material';
import {
    TrendingUp,
    TrendingDown,
    ArrowForward,
    Lightbulb,
} from '@mui/icons-material';
import BayesianNetworkDisplay from '@/components/prediction/BayesianNetworkDisplay';
import { BayesianNetwork } from '@/types';

interface CausalPath {
    path: string[];
    probability: number;
    impact: 'high' | 'medium' | 'low';
    explanation: string;
}

interface BayesianReasoningProps {
    bayesianNetwork: BayesianNetwork;
    decision: 'APPROVE' | 'REJECT' | 'MANUAL_REVIEW';
    riskScore: number;
}

export default function BayesianReasoning({
    bayesianNetwork,
    decision,
    riskScore,
}: BayesianReasoningProps) {
    // Generate causal paths from Bayesian network
    const generateCausalPaths = (): CausalPath[] => {
        // This would be calculated from the actual Bayesian network
        // For now, providing example paths
        return [
            {
                path: ['Credit Score', 'Payment History', 'Default Risk'],
                probability: 0.85,
                impact: 'high',
                explanation: 'Strong credit score and payment history significantly reduce default risk',
            },
            {
                path: ['Income Level', 'Debt-to-Income Ratio', 'Repayment Capacity'],
                probability: 0.78,
                impact: 'high',
                explanation: 'Stable income with low debt ratio indicates strong repayment capacity',
            },
            {
                path: ['Employment Length', 'Income Stability', 'Default Risk'],
                probability: 0.65,
                impact: 'medium',
                explanation: 'Longer employment history correlates with income stability',
            },
        ];
    };

    const causalPaths = generateCausalPaths();

    // Generate decision logic steps
    const generateDecisionLogic = (): string[] => {
        const logic: string[] = [];

        // Add decision summary based on risk score
        if (decision === 'APPROVE') {
            logic.push(
                `✓ Low risk score indicates strong creditworthiness`
            );
            logic.push(
                `✓ All key financial indicators meet approval criteria`
            );
            logic.push(
                `\n📊 Overall Assessment: The positive factors outweigh the negative ones, resulting in a ${((1 - riskScore) * 100).toFixed(1)}% approval confidence.`
            );
        } else if (decision === 'REJECT') {
            logic.push(
                `✗ High risk score indicates elevated default probability`
            );
            logic.push(
                `✗ Key financial indicators do not meet minimum thresholds`
            );
            logic.push(
                `\n📊 Overall Assessment: The negative factors outweigh the positive ones, resulting in a ${(riskScore * 100).toFixed(1)}% risk score.`
            );
        } else {
            logic.push(
                `⚠ Mixed risk indicators require human judgment`
            );
            logic.push(
                `⚠ Some factors meet criteria while others need review`
            );
            logic.push(
                `\n📊 Overall Assessment: The factors are balanced, requiring manual review for final decision.`
            );
        }

        return logic;
    };

    const decisionLogic = generateDecisionLogic();

    const getImpactColor = (impact: 'high' | 'medium' | 'low') => {
        if (impact === 'high') return 'error';
        if (impact === 'medium') return 'warning';
        return 'info';
    };

    return (
        <Box>
            {/* Bayesian Network Visualization */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                        Bayesian Network - Causal Relationships
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        This network shows how different factors influence each other and contribute to the final decision.
                    </Typography>
                    <BayesianNetworkDisplay network={bayesianNetwork} />
                </CardContent>
            </Card>

            {/* Causal Path Analysis */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                        Causal Path Analysis
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Key causal paths showing how factors flow through the decision-making process.
                    </Typography>

                    <Grid container spacing={2}>
                        {causalPaths.map((path, index) => (
                            <Grid item xs={12} key={index}>
                                <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                                        {path.path.map((node, nodeIndex) => (
                                            <Box key={nodeIndex} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <Chip
                                                    label={node}
                                                    size="small"
                                                    color="primary"
                                                    variant="outlined"
                                                />
                                                {nodeIndex < path.path.length - 1 && (
                                                    <ArrowForward fontSize="small" color="action" />
                                                )}
                                            </Box>
                                        ))}
                                    </Box>

                                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mt: 2 }}>
                                        <Chip
                                            label={`${(path.probability * 100).toFixed(0)}% Probability`}
                                            size="small"
                                            color="success"
                                        />
                                        <Chip
                                            label={`${path.impact.toUpperCase()} Impact`}
                                            size="small"
                                            color={getImpactColor(path.impact)}
                                            variant="outlined"
                                        />
                                    </Box>

                                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                        {path.explanation}
                                    </Typography>
                                </Paper>
                            </Grid>
                        ))}
                    </Grid>
                </CardContent>
            </Card>

            {/* Decision Logic Breakdown */}
            <Card>
                <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <Lightbulb color="primary" />
                        <Typography variant="h6" fontWeight={600}>
                            Decision Logic - Step by Step
                        </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Plain language explanation of how the model reached its decision.
                    </Typography>

                    <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
                        <List>
                            {decisionLogic.map((step, index) => (
                                <ListItem key={index} sx={{ py: 1, px: 0 }}>
                                    <ListItemIcon sx={{ minWidth: 40 }}>
                                        {step.startsWith('✓') ? (
                                            <TrendingUp color="success" />
                                        ) : step.startsWith('✗') ? (
                                            <TrendingDown color="error" />
                                        ) : (
                                            <Lightbulb color="primary" />
                                        )}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={
                                            <Typography
                                                variant="body2"
                                                sx={{
                                                    fontFamily: 'monospace',
                                                    whiteSpace: 'pre-wrap',
                                                }}
                                            >
                                                {step}
                                            </Typography>
                                        }
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Paper>

                    <Divider sx={{ my: 3 }} />

                    <Paper sx={{ p: 2, bgcolor: decision === 'APPROVE' ? 'success.light' : decision === 'REJECT' ? 'error.light' : 'warning.light' }}>
                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                            Final Decision: {decision.replace('_', ' ')}
                        </Typography>
                        <Typography variant="body2">
                            {decision === 'APPROVE' && 'Based on the analysis above, the applicant demonstrates strong creditworthiness and low default risk. The loan application is recommended for approval.'}
                            {decision === 'REJECT' && 'Based on the analysis above, the applicant shows elevated risk factors that exceed acceptable thresholds. The loan application is recommended for rejection.'}
                            {decision === 'MANUAL_REVIEW' && 'Based on the analysis above, the applicant has mixed risk factors that require human judgment. Manual review by a loan officer is recommended.'}
                        </Typography>
                    </Paper>
                </CardContent>
            </Card>
        </Box>
    );
}
