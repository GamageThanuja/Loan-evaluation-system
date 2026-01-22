'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  PictureAsPdfRounded as PdfIcon
} from '@mui/icons-material';
import { useApplicants } from '@/hooks/useApplicants';
import { useStatusUtils } from '@/hooks/useStatusUtils';
import { TableSkeleton } from '@/components/ui/LoadingSkeleton';
import axios from 'axios';
import {
  CheckCircle,
  Cancel,
  HourglassEmpty,
  RateReview,
} from '@mui/icons-material';

export default function ReportsPage() {
  const [page] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [downloadingIds, setDownloadingIds] = useState<Set<number>>(new Set());
  const statusUtils = useStatusUtils();
  
  // Wait for status data to load before rendering chips with colors
  const isStatusDataReady = !statusUtils.isLoading;

  // Fetch ONLY not-eligible (+ rejected) applicants (eligibilityStatus = 0)
  const {
    data,
    isLoading,
    error,
    refetch
  } = useApplicants(page, 10, searchTerm, undefined, 0);

  const getStatusIcon = (statusCode: string) => {
    switch (statusCode?.toLowerCase()) {
      case 'approved':
        return <CheckCircle />;
      case 'rejected':
        return <Cancel />;
      case 'under_review':
        return <RateReview />;
      case 'pending':
      default:
        return <HourglassEmpty />;
    }
  };

  const getStatusChip = (status: string) => {
    const statusInfo = statusUtils.getApplicationStatus(status);
    const statusName = statusInfo?.name || statusUtils.getStatusName(status);
    const statusCode = statusInfo?.code || status?.toLowerCase() || 'pending';
    const colorCode = statusInfo?.colorCode;

    // If we have a color code from API and data is ready, use it directly
    if (isStatusDataReady && colorCode) {
      return (
        <Chip
          label={statusName}
          size="small"
          icon={getStatusIcon(statusCode)}
          sx={{
            bgcolor: `${colorCode}20`,
            color: colorCode,
            border: `1px solid ${colorCode}40`,
            fontWeight: 600,
            '& .MuiChip-icon': {
              color: colorCode,
            },
          }}
        />
      );
    }

    // Fallback to Material-UI theme colors (while loading or if no color code)
    const statusColor = statusUtils.getStatusColorName(status);
    return (
      <Chip
        label={statusName}
        size="small"
        color={statusColor}
        icon={getStatusIcon(statusCode)}
      />
    );
  };

  const getEligibilityChip = (eligibilityStatus: string | null | undefined) => {
    if (!eligibilityStatus) {
      const notCheckedStatus = statusUtils.getEligibilityStatus('not_checked');
      return (
        <Chip 
          label={notCheckedStatus?.name || 'Not Checked'} 
          size="small" 
          variant="outlined" 
        />
      );
    }

    const eligibilityInfo = statusUtils.getEligibilityStatus(eligibilityStatus);
    const eligibilityName = eligibilityInfo?.name || statusUtils.getEligibilityName(eligibilityStatus);
    
    // Map eligibility to color
    let color: 'success' | 'error' | 'default' = 'default';
    if (eligibilityInfo?.code === 'eligible') color = 'success';
    else if (eligibilityInfo?.code === 'not_eligible') color = 'error';

    return (
      <Chip 
        label={eligibilityName} 
        size="small" 
        color={color}
        variant="outlined" 
      />
    );
  };

  const handleGenerateReport = async (applicantId: number) => {
    try {
      setDownloadingIds(prev => new Set(prev).add(applicantId));

      // Get full auth state from localStorage
      let authData = null;
      try {
        const authStorage = localStorage.getItem('auth-storage');
        if (authStorage) {
          authData = JSON.parse(authStorage);
        }
      } catch (e) {
        console.error("Error reading auth state", e);
      }

      const response = await axios.post('/api/reports/generate',
        { applicantId, authState: authData },
        {
          responseType: 'blob',
          headers: { 'Content-Type': 'application/json' }
        }
      );

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Rejection_Report_${applicantId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);

    } catch (error) {
      console.error("Download failed:", error);
      alert("Failed to generate report. Please try again.");
    } finally {
      setDownloadingIds(prev => {
        const next = new Set(prev);
        next.delete(applicantId);
        return next;
      });
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Reports
          </Typography>
        </Box>
      </Box>

      {/* Filters & Search */}
      <Card sx={{ mb: 4, p: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
          <TextField
            fullWidth
            placeholder="Search by name, NIC, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
            size="small"
          />
          <Button
            startIcon={<RefreshIcon />}
            onClick={() => refetch()}
            variant="outlined"
          >
            Refresh
          </Button>
        </Stack>
      </Card>

      {/* Applicants Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Rejected / Not Eligible Applicants
          </Typography>

          {isLoading ? (
            <Box sx={{ p: 2 }}>
              <TableSkeleton rows={5} />
            </Box>
          ) : error ? (
            <Typography color="error">Failed to load applicants</Typography>
          ) : (
            <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e0e0e0' }}>
              <Table>
                <TableHead sx={{ bgcolor: 'grey.50' }}>
                  <TableRow>
                    <TableCell>Applicant Details</TableCell>
                    <TableCell>Loan Request</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Risk Assessment</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data?.items.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                        <Typography color="text.secondary">
                          No rejected applications found matching your criteria.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    data?.items.map((applicant) => (
                      <TableRow key={applicant.id} hover>
                        <TableCell>
                          <Typography variant="subtitle2" fontWeight={600}>
                            {applicant.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" display="block">
                            {applicant.nic}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {applicant.email}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            LKR {applicant.loanAmount?.toLocaleString()}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {applicant.loanTermMonths} months
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {/* Display status using API color codes */}
                          {getStatusChip(applicant.status || 'pending')}
                        </TableCell>
                        <TableCell>
                          {/* Show Credit Score if available, else generic risk indicator */}
                          <Typography variant="body2">
                            Credit Score: {applicant.creditScore || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <Button
                              variant="contained"
                              size="small"
                              startIcon={downloadingIds.has(applicant.id) ? <CircularProgress size={20} color="inherit" /> : <PdfIcon />}
                              onClick={() => handleGenerateReport(applicant.id)}
                              disabled={downloadingIds.has(applicant.id)}
                              sx={{ textTransform: 'none' }}
                            >
                              {downloadingIds.has(applicant.id) ? 'Generating...' : 'Generate Report'}
                            </Button>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
