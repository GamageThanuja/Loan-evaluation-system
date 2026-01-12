'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  InputAdornment,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search,
  PersonAdd,
  Visibility,
  CheckCircle,
  Cancel,
  HourglassEmpty,
  RateReview,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useApplicants } from '@/hooks/useApplicants';
import { TableSkeleton } from '@/components/ui/LoadingSkeleton';
import EmptyState from '@/components/common/EmptyState';

export default function ApplicantListPage() {
  const router = useRouter();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');

  const { data, isLoading } = useApplicants(page + 1, rowsPerPage, search);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewApplicant = (applicantId: string) => {
    router.push(`/applicant/${applicantId}`);
  };

  const getStatusChip = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return (
          <Chip
            label="Approved"
            size="small"
            color="success"
            icon={<CheckCircle />}
          />
        );
      case 'rejected':
        return (
          <Chip
            label="Rejected"
            size="small"
            color="error"
            icon={<Cancel />}
          />
        );
      case 'under_review':
        return (
          <Chip
            label="Under Review"
            size="small"
            color="info"
            icon={<RateReview />}
          />
        );
      case 'pending':
      default:
        return (
          <Chip
            label="Pending"
            size="small"
            color="warning"
            icon={<HourglassEmpty />}
          />
        );
    }
  };

  const getEligibilityChip = (eligibilityStatus: string | null | undefined) => {
    if (!eligibilityStatus) return <Chip label="Not Checked" size="small" variant="outlined" />;

    switch (eligibilityStatus.toLowerCase()) {
      case 'eligible':
        return <Chip label="Eligible" size="small" color="success" variant="outlined" />;
      case 'not_eligible':
        return <Chip label="Not Eligible" size="small" color="error" variant="outlined" />;
      default:
        return <Chip label="Pending" size="small" variant="outlined" />;
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-LK', {
      style: 'currency',
      currency: 'LKR',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getCreditScoreColor = (score: number) => {
    if (score >= 720) return 'success.main';
    if (score >= 650) return 'warning.main';
    return 'error.main';
  };

  // Use API data
  const displayData = data?.items || [];
  const totalCount = data?.total || 0;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight={700}>
            All Applicants
          </Typography>
          <Typography variant="body2" color="text.secondary">
            View and manage all loan applications
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<PersonAdd />}
          onClick={() => router.push('/applicant/new')}
        >
          New Applicant
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search by name, email, or NIC..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      <Paper>
        {isLoading ? (
          <Box sx={{ p: 2 }}>
            <TableSkeleton rows={rowsPerPage} />
          </Box>
        ) : displayData.length > 0 ? (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'action.hover' }}>
                    <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Email</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 700 }}>Credit Score</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>Loan Amount</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Purpose</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 700 }}>Eligibility</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 700 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Created</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 700 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {displayData.map((applicant) => (
                    <TableRow
                      key={applicant.id}
                      hover
                      sx={{ cursor: 'pointer' }}
                      onClick={() => handleViewApplicant(applicant.id)}
                    >
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {applicant.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{applicant.email}</Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          sx={{ color: getCreditScoreColor(applicant.creditScore || 0) }}
                        >
                          {applicant.creditScore || '-'}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {formatCurrency(applicant.loanAmount)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={applicant.loanPurpose} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell align="center">
                        {getEligibilityChip(applicant.eligibilityStatus)}
                      </TableCell>
                      <TableCell align="center">
                        {getStatusChip(applicant.status)}
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {formatDate(applicant.createdAt)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleViewApplicant(applicant.id);
                            }}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={totalCount}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </>
        ) : (
          <Box sx={{ p: 4 }}>
            <EmptyState
              title="No applicants found"
              description="Start by creating a new applicant"
              action={{
                label: 'New Applicant',
                onClick: () => router.push('/applicant/new'),
              }}
            />
          </Box>
        )}
      </Paper>
    </Box>
  );
}
