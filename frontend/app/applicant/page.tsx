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
} from '@mui/material';
import { Search, PersonAdd } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useApplicants } from '@/hooks/usePrediction';
import { TableSkeleton } from '@/components/ui/LoadingSkeleton';
import EmptyState from '@/components/common/EmptyState';
import { formatDate, formatCurrency } from '@/lib/utils';

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'rejected':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getCreditScoreColor = (score: number) => {
    if (score >= 720) return '#2e7d32';
    if (score >= 650) return '#f59e0b';
    return '#d32f2f';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Applicants
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage and review loan applications
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
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
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
        ) : data && data.items.length > 0 ? (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Credit Score</TableCell>
                    <TableCell>Loan Amount</TableCell>
                    <TableCell>Purpose</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.items.map((applicant) => (
                    <TableRow
                      key={applicant.id}
                      hover
                      sx={{ cursor: 'pointer' }}
                      onClick={() => router.push(`/applicant/${applicant.id}`)}
                    >
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {applicant.firstName} {applicant.lastName}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{applicant.email}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          sx={{ color: getCreditScoreColor(applicant.creditScore) }}
                        >
                          {applicant.creditScore}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatCurrency(applicant.loanAmount)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={applicant.loanPurpose} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={applicant.status.toUpperCase()}
                          size="small"
                          color={getStatusColor(applicant.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {formatDate(applicant.createdAt)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={data.total}
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
