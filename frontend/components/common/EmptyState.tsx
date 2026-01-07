'use client';

import { Box, Typography, Button, Paper } from '@mui/material';
import { InboxOutlined } from '@mui/icons-material';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export default function EmptyState({
  title,
  description,
  icon,
  action,
}: EmptyStateProps) {
  return (
    <Paper
      sx={{
        p: 6,
        textAlign: 'center',
        bgcolor: 'background.default',
      }}
    >
      <Box sx={{ mb: 3 }}>
        {icon || <InboxOutlined sx={{ fontSize: 64, color: 'text.secondary' }} />}
      </Box>
      <Typography variant="h6" gutterBottom color="text.primary">
        {title}
      </Typography>
      {description && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {description}
        </Typography>
      )}
      {action && (
        <Button variant="contained" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </Paper>
  );
}
