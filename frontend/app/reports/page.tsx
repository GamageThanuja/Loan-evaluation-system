'use client';

import {
  Box,
  Typography,
} from '@mui/material';
import ShapReports from '@/components/reports/ShapReports';

export default function ReportsPage() {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight={700}>
          SHAP Explainability Reports
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Comprehensive SHAP (SHapley Additive exPlanations) analysis and visualizations
        </Typography>
      </Box>

      {/* SHAP Explainability Analysis */}
      <ShapReports />
    </Box>
  );
}
