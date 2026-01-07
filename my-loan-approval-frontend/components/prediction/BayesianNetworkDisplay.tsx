'use client';

import { Box, Typography, Paper, Chip, Grid } from '@mui/material';
import { AccountTree } from '@mui/icons-material';
import { BayesianNetwork as BayesianNetworkType } from '@/types';

interface BayesianNetworkDisplayProps {
  network: BayesianNetworkType;
}

export default function BayesianNetworkDisplay({ network }: BayesianNetworkDisplayProps) {
  const getStrengthColor = (strength: number) => {
    if (strength >= 0.6) return '#2e7d32';
    if (strength >= 0.4) return '#f59e0b';
    return '#d32f2f';
  };

  const getStrengthLabel = (strength: number) => {
    if (strength >= 0.6) return 'Strong';
    if (strength >= 0.4) return 'Moderate';
    return 'Weak';
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom fontWeight={600}>
        Bayesian Network Analysis
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Causal relationships affecting the prediction
      </Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {network.nodes.map((node) => (
          <Grid item xs={12} sm={6} key={node.id}>
            <Box
              sx={{
                p: 2,
                border: '2px solid',
                borderColor: 'primary.main',
                borderRadius: 2,
                bgcolor: 'background.default',
              }}
            >
              <Typography variant="body2" fontWeight={600} gutterBottom>
                {node.displayName}
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                  State: {node.state}
                </Typography>
                <Chip
                  label={`${(node.probability * 100).toFixed(0)}%`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
            </Box>
          </Grid>
        ))}
      </Grid>

      <Typography variant="body2" fontWeight={600} gutterBottom>
        Causal Paths
      </Typography>
      {network.causalPaths.map((path, index) => {
        const strength = path.impact;
        const strengthColor = getStrengthColor(strength);
        const strengthLabel = getStrengthLabel(strength);

        return (
          <Box
            key={index}
            sx={{
              mb: 2,
              p: 2,
              bgcolor: 'background.default',
              borderRadius: 2,
              borderLeft: '4px solid',
              borderColor: strengthColor,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <AccountTree sx={{ fontSize: 20, color: 'text.secondary' }} />
              <Typography variant="body2" fontWeight={600}>
                {path.path.map((node, i) => {
                  const displayNode = network.nodes.find(n => n.name === node);
                  return (
                    <span key={i}>
                      {displayNode?.displayName || node}
                      {i < path.path.length - 1 && ' → '}
                    </span>
                  );
                })}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                {path.description}
              </Typography>
              <Chip
                label={strengthLabel}
                size="small"
                sx={{
                  bgcolor: `${strengthColor}20`,
                  color: strengthColor,
                  fontWeight: 600,
                }}
              />
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Probability
                </Typography>
                <Typography variant="caption" fontWeight={600}>
                  {(path.probability * 100).toFixed(0)}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Impact
                </Typography>
                <Typography variant="caption" fontWeight={600}>
                  {(path.impact * 100).toFixed(0)}%
                </Typography>
              </Box>
            </Box>
          </Box>
        );
      })}

      <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
        <Typography variant="caption" color="text.secondary">
          <strong>Note:</strong> The Bayesian Network shows probabilistic causal relationships 
          between features. Stronger paths have more influence on the final prediction.
        </Typography>
      </Box>
    </Paper>
  );
}
