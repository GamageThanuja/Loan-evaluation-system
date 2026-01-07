'use client';

import { Box, Typography, Paper, Chip } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ShapExplanation as ShapExplanationType } from '@/types';

interface ShapExplanationProps {
  explanation: ShapExplanationType;
}

export default function ShapExplanation({ explanation }: ShapExplanationProps) {
  const chartData = explanation.topFeatures.map((feature) => ({
    name: feature.displayName,
    value: Math.abs(feature.shapValue),
    impact: feature.impact,
    actualValue: feature.shapValue,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Paper sx={{ p: 1 }}>
          <Typography variant="caption" fontWeight={600}>
            {data.name}
          </Typography>
          <Typography variant="caption" display="block">
            Impact: {(data.actualValue * 100).toFixed(2)}%
          </Typography>
        </Paper>
      );
    }
    return null;
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom fontWeight={600}>
        SHAP Explanation
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Top 5 features influencing the prediction
      </Typography>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="name" type="category" width={110} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.impact === 'positive' ? '#2e7d32' : '#d32f2f'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <Box sx={{ mt: 3 }}>
        <Typography variant="body2" fontWeight={600} gutterBottom>
          Feature Impacts
        </Typography>
        {explanation.topFeatures.map((feature, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 1,
              p: 1,
              bgcolor: 'background.default',
              borderRadius: 1,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {feature.impact === 'positive' ? (
                <TrendingDown sx={{ color: '#2e7d32', fontSize: 20 }} />
              ) : (
                <TrendingUp sx={{ color: '#d32f2f', fontSize: 20 }} />
              )}
              <Typography variant="body2">{feature.displayName}</Typography>
            </Box>
            <Chip
              label={`${(feature.shapValue * 100).toFixed(2)}%`}
              size="small"
              sx={{
                bgcolor: feature.impact === 'positive' ? '#2e7d3220' : '#d32f2f20',
                color: feature.impact === 'positive' ? '#2e7d32' : '#d32f2f',
                fontWeight: 600,
              }}
            />
          </Box>
        ))}
      </Box>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 2 }}>
        <Typography variant="caption" color="info.contrastText">
          <strong>Interpretation:</strong> Positive values (green) decrease default risk, 
          while negative values (red) increase it. Larger bars indicate stronger influence.
        </Typography>
      </Box>
    </Paper>
  );
}
