'use client';

import { Box, Typography, Paper, Chip, Alert } from '@mui/material';
import { Warning, Info, Error as ErrorIcon, CheckCircle } from '@mui/icons-material';
import { BusinessRule } from '@/types';

interface BusinessRulesProps {
  rules: BusinessRule[];
}

export default function BusinessRules({ rules }: BusinessRulesProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon />;
      case 'warning':
        return <Warning />;
      case 'info':
        return <Info />;
      default:
        return <CheckCircle />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'success';
    }
  };

  const triggeredRules = rules.filter(r => r.triggered);
  const criticalCount = triggeredRules.filter(r => r.severity === 'critical').length;
  const warningCount = triggeredRules.filter(r => r.severity === 'warning').length;
  const infoCount = triggeredRules.filter(r => r.severity === 'info').length;

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight={600}>
          Business Rules
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {criticalCount > 0 && (
            <Chip label={`${criticalCount} Critical`} color="error" size="small" />
          )}
          {warningCount > 0 && (
            <Chip label={`${warningCount} Warning`} color="warning" size="small" />
          )}
          {infoCount > 0 && (
            <Chip label={`${infoCount} Info`} color="info" size="small" />
          )}
        </Box>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Triggered rules and recommendations
      </Typography>

      {triggeredRules.length === 0 ? (
        <Alert severity="success">
          All business rules passed. No specific concerns identified.
        </Alert>
      ) : (
        <Box>
          {triggeredRules.map((rule) => (
            <Box
              key={rule.id}
              sx={{
                mb: 2,
                p: 2,
                border: '1px solid',
                borderColor: `${getSeverityColor(rule.severity)}.main`,
                borderRadius: 2,
                bgcolor: `${getSeverityColor(rule.severity)}.light`,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                <Box sx={{ color: `${getSeverityColor(rule.severity)}.main`, mt: 0.5 }}>
                  {getSeverityIcon(rule.severity)}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body2" fontWeight={600} gutterBottom>
                    {rule.rule}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {rule.recommendation}
                  </Typography>
                  {rule.actionRequired && (
                    <Chip
                      label="Action Required"
                      size="small"
                      color={getSeverityColor(rule.severity) as any}
                      variant="outlined"
                    />
                  )}
                </Box>
              </Box>
            </Box>
          ))}
        </Box>
      )}

      <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
        <Typography variant="caption" color="text.secondary">
          <strong>Summary:</strong> Business rules are predefined conditions that must be met 
          for loan approval. Critical rules require immediate attention, while warnings should 
          be reviewed by a loan officer.
        </Typography>
      </Box>
    </Paper>
  );
}
