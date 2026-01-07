'use client';

import { Box, Typography, LinearProgress, Chip, Paper } from '@mui/material';
import { RiskLevel } from '@/types';
import { getRiskColor } from '@/lib/utils';

interface RiskGaugeProps {
  riskScore: number;
  riskLevel: RiskLevel;
  confidence?: number;
}

export default function RiskGauge({ riskScore, riskLevel, confidence }: RiskGaugeProps) {
  const riskColor = getRiskColor(riskLevel);
  const percentage = riskScore * 100;

  // Calculate position for circular gauge
  const circumference = 2 * Math.PI * 70;
  const dashOffset = circumference - (percentage / 100) * circumference;

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom fontWeight={600}>
        Risk Assessment
      </Typography>
      
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
        <Box sx={{ position: 'relative', width: 200, height: 200 }}>
          {/* Circular gauge */}
          <svg width="200" height="200" style={{ transform: 'rotate(-90deg)' }}>
            {/* Background circle */}
            <circle
              cx="100"
              cy="100"
              r="70"
              fill="none"
              stroke="#e0e0e0"
              strokeWidth="12"
            />
            {/* Progress circle */}
            <circle
              cx="100"
              cy="100"
              r="70"
              fill="none"
              stroke={riskColor}
              strokeWidth="12"
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.5s ease' }}
            />
          </svg>
          
          {/* Center content */}
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
            }}
          >
            <Typography variant="h3" fontWeight={700} sx={{ color: riskColor }}>
              {percentage.toFixed(1)}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Risk Score
            </Typography>
          </Box>
        </Box>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2">Risk Level</Typography>
          <Chip
            label={riskLevel}
            size="small"
            sx={{
              bgcolor: `${riskColor}20`,
              color: riskColor,
              fontWeight: 600,
            }}
          />
        </Box>
        <LinearProgress
          variant="determinate"
          value={percentage}
          sx={{
            height: 8,
            borderRadius: 4,
            bgcolor: '#e0e0e0',
            '& .MuiLinearProgress-bar': {
              bgcolor: riskColor,
              borderRadius: 4,
            },
          }}
        />
      </Box>

      {confidence && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption">Model Confidence</Typography>
            <Typography variant="caption" fontWeight={600}>
              {(confidence * 100).toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={confidence * 100}
            sx={{
              height: 4,
              borderRadius: 2,
              bgcolor: '#e0e0e0',
            }}
          />
        </Box>
      )}
    </Paper>
  );
}
