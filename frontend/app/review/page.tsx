'use client';

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Divider,
  Card,
  CardContent,
  TextField,
  Alert,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Visibility,
  Person,
  AttachMoney,
  Schedule,
  Description,
  Close,
} from '@mui/icons-material';
import { useAuth } from '@/hooks/useAuth';
import { useApplicants, useApproveApplication, useRejectApplication, applicantKeys } from '@/hooks/useApplicants';
import { useQueryClient } from '@tanstack/react-query';
import { TableSkeleton } from '@/components/ui/LoadingSkeleton';
import { Applicant } from '@/types';

export default function ReviewPage() {
  const { isManager } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState(0);

  // API Hooks
  const { data: pendingData, isLoading: isLoadingPending } = useApplicants(1, 100, undefined, 'under_review');
  const { data: approvedData, isLoading: isLoadingApproved } = useApplicants(1, 50, undefined, 'approved');
  const { data: rejectedData, isLoading: isLoadingRejected } = useApplicants(1, 50, undefined, 'rejected');

  const approveMutation = useApproveApplication();
  const rejectMutation = useRejectApplication();

  const [selectedReview, setSelectedReview] = useState<Applicant | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState<{ open: boolean; action: 'approve' | 'reject' | null }>({
    open: false,
    action: null,
  });
  const [rejectionReason, setRejectionReason] = useState('');

  const pendingReviews = pendingData?.items || [];
  const processedReviews = [...(approvedData?.items || []), ...(rejectedData?.items || [])].sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );

  const isLoading = isLoadingPending || isLoadingApproved || isLoadingRejected;

  // Redirect non-managers
  if (!isManager) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Alert severity="error">
          You do not have permission to access this page. This page is only accessible to Bank Managers.
        </Alert>
      </Box>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-LK', {
      style: 'currency',
      currency: 'LKR',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleViewDetails = (review: Applicant) => {
    setSelectedReview(review);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedReview(null);
    setRejectionReason('');
  };

  const handleConfirmAction = (action: 'approve' | 'reject') => {
    setConfirmDialog({ open: true, action });
  };

  const handleExecuteAction = async () => {
    if (!selectedReview || !confirmDialog.action) return;

    const applicantId = selectedReview.id.toString();

    try {
      if (confirmDialog.action === 'approve') {
        await approveMutation.mutateAsync({
          applicantId,
          data: { notes: 'Approved by manager' }
        });
      } else {
        await rejectMutation.mutateAsync({
          applicantId,
          data: { reason: rejectionReason }
        });
      }

      // Refresh data
      queryClient.invalidateQueries({ queryKey: applicantKeys.all });

      setConfirmDialog({ open: false, action: null });
      handleCloseDetails();
    } catch (error) {
      console.error('Error processing review:', error);
    }
  };

  const getStatusChip = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return <Chip label="Approved" color="success" size="small" icon={<CheckCircle />} />;
      case 'rejected':
        return <Chip label="Rejected" color="error" size="small" icon={<Cancel />} />;
      case 'under_review':
        return <Chip label="Under Review" color="info" size="small" icon={<Schedule />} />;
      case 'pending':
        return <Chip label="Pending" color="warning" size="small" icon={<Schedule />} />;
      default:
        return <Chip label={status || 'Unknown'} size="small" />;
    }
  };

  const renderReviewTable = (reviewList: Applicant[]) => (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow sx={{ bgcolor: 'action.hover' }}>
            <TableCell sx={{ fontWeight: 700 }}>Applicant</TableCell>
            <TableCell sx={{ fontWeight: 700 }}>NIC</TableCell>
            <TableCell align="right" sx={{ fontWeight: 700 }}>Loan Amount</TableCell>
            <TableCell align="center" sx={{ fontWeight: 700 }}>Duration</TableCell>
            <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
            <TableCell sx={{ fontWeight: 700 }}>Submitted At</TableCell>
            <TableCell align="center" sx={{ fontWeight: 700 }}>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {reviewList.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                <Typography color="text.secondary">No applications currently in this status</Typography>
              </TableCell>
            </TableRow>
          ) : (
            reviewList.map((review) => (
              <TableRow key={review.id} hover>
                <TableCell>
                  <Typography fontWeight={600}>{review.name}</Typography>
                  <Typography variant="caption" color="text.secondary">{review.email}</Typography>
                </TableCell>
                <TableCell>{review.nic}</TableCell>
                <TableCell align="right">{formatCurrency(review.loanAmount)}</TableCell>
                <TableCell align="center">{review.loanTermMonths || review.loanTerm || 12} months</TableCell>
                <TableCell>{getStatusChip(review.status)}</TableCell>
                <TableCell>{formatDate(review.createdAt)}</TableCell>
                <TableCell align="center">
                  <Tooltip title="View Details">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleViewDetails(review)}
                    >
                      <Visibility />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Loan Application Review
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Review and approve or reject loan applications submitted for manager approval
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h3" fontWeight={700} color="warning.main">
                    {pendingReviews.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending Reviews
                  </Typography>
                </Box>
                <Schedule sx={{ fontSize: 40, color: 'warning.light' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h3" fontWeight={700} color="success.main">
                    {approvedData?.total || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Approved
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, color: 'success.light' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h3" fontWeight={700} color="error.main">
                    {rejectedData?.total || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Rejected
                  </Typography>
                </Box>
                <Cancel sx={{ fontSize: 40, color: 'error.light' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Reviews Table */}
      <Paper>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab label={`Pending (${pendingReviews.length})`} />
          <Tab label={`Processed (${processedReviews.length})`} />
        </Tabs>

        {isLoading ? (
          <Box sx={{ p: 4 }}>
            <TableSkeleton rows={5} />
          </Box>
        ) : (
          <>
            {activeTab === 0 && renderReviewTable(pendingReviews)}
            {activeTab === 1 && renderReviewTable(processedReviews)}
          </>
        )}
      </Paper>

      {/* Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6" fontWeight={600}>
              Application Details
            </Typography>
            <IconButton onClick={handleCloseDetails} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedReview && (
            <Grid container spacing={3}>
              {/* Applicant Information */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Person sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="subtitle1" fontWeight={600}>
                        Applicant Information
                      </Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={1}>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Name:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2" fontWeight={600}>{selectedReview.name || 'N/A'}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">NIC:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.nic || 'N/A'}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Email:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.email}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Phone:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.phone}</Typography></Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Loan Details */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <AttachMoney sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="subtitle1" fontWeight={600}>
                        Loan Details
                      </Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={1}>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Amount:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2" fontWeight={600}>{formatCurrency(selectedReview.loanAmount)}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Duration:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.loanTermMonths || selectedReview.loanTerm || 12} months</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Monthly EMI:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{formatCurrency(Math.round(selectedReview.loanAmount / (selectedReview.loanTermMonths || selectedReview.loanTerm || 12) * 1.12))}</Typography></Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Financial Information */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Description sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="subtitle1" fontWeight={600}>
                        Financial Information
                      </Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={1}>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Monthly Income:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{formatCurrency(selectedReview.monthlyIncome || 0)}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Employment:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.employmentStatus || selectedReview.employmentType || 'N/A'}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Employer:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.employerName || 'N/A'}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Credit Score:</Typography></Grid>
                      <Grid item xs={7}>
                        {selectedReview.creditScore !== undefined ? (
                          <Chip
                            label={selectedReview.creditScore}
                            size="small"
                            color={selectedReview.creditScore >= 700 ? 'success' : selectedReview.creditScore >= 600 ? 'warning' : 'error'}
                          />
                        ) : 'N/A'}
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Submission Details */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Schedule sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="subtitle1" fontWeight={600}>
                        Review Details
                      </Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={1}>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Submitted At:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{formatDate(selectedReview.createdAt)}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Eligibility:</Typography></Grid>
                      <Grid item xs={7}>
                        <Chip
                          label={selectedReview.eligibilityStatus || 'Not Checked'}
                          size="small"
                          color={selectedReview.eligibilityStatus === 'eligible' ? 'success' : 'default'}
                          variant="outlined"
                        />
                      </Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Current Status:</Typography></Grid>
                      <Grid item xs={7}>{getStatusChip(selectedReview.status)}</Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Rejection Reason (only for reject action) */}
              {selectedReview.status === 'under_review' && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Decision Notes / Rejection Reason"
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="Enter approval comments or rejection reason..."
                  />
                </Grid>
              )}
              {selectedReview.status === 'rejected' && (
                <Grid item xs={12}>
                  <Alert severity="error" icon={<Cancel />}>
                    <strong>Rejection Reason:</strong> {selectedReview.rejectionReason || 'No reason specified'}
                  </Alert>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          {selectedReview?.status === 'under_review' && (
            <>
              <Button
                variant="contained"
                color="error"
                startIcon={<Cancel />}
                onClick={() => handleConfirmAction('reject')}
                disabled={!rejectionReason.trim()}
              >
                Reject Application
              </Button>
              <Button
                variant="contained"
                color="success"
                startIcon={<CheckCircle />}
                onClick={() => handleConfirmAction('approve')}
              >
                Approve Application
              </Button>
            </>
          )}
          <Button variant="outlined" onClick={handleCloseDetails}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ open: false, action: null })}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>
          Confirm {confirmDialog.action === 'approve' ? 'Approval' : 'Rejection'}
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to {confirmDialog.action} the loan application for{' '}
            <strong>{selectedReview?.name}</strong>?
          </Typography>
          {confirmDialog.action === 'approve' && (
            <Alert severity="info" sx={{ mt: 2 }}>
              This will approve a loan of {selectedReview && formatCurrency(selectedReview.loanAmount)} for{' '}
              {selectedReview?.loanTermMonths || selectedReview?.loanTerm || 12} months.
            </Alert>
          )}
          {confirmDialog.action === 'reject' && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              The applicant will be notified of the rejection with the reason provided.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog({ open: false, action: null })}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color={confirmDialog.action === 'approve' ? 'success' : 'error'}
            onClick={handleExecuteAction}
          >
            Confirm {confirmDialog.action === 'approve' ? 'Approval' : 'Rejection'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
