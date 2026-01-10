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

// Mock pending reviews data
const mockPendingReviews: Review[] = [
  {
    id: 'REV001',
    applicantId: '1',
    applicantName: 'John Doe',
    nic: '951234567V',
    email: 'john@example.com',
    phone: '+94 77 123 4567',
    loanAmount: 500000,
    duration: 24,
    submittedBy: 'Officer A',
    submittedAt: '2024-01-15T10:30:00',
    status: 'pending' as ReviewStatus,
    monthlyIncome: 150000,
    employmentType: 'Full-time',
    employer: 'Tech Corp Ltd',
    creditScore: 720,
  },
  {
    id: 'REV002',
    applicantId: '2',
    applicantName: 'Jane Smith',
    nic: '901234568V',
    email: 'jane@example.com',
    phone: '+94 77 234 5678',
    loanAmount: 1000000,
    duration: 36,
    submittedBy: 'Officer B',
    submittedAt: '2024-01-14T14:45:00',
    status: 'pending' as ReviewStatus,
    monthlyIncome: 250000,
    employmentType: 'Self-employed',
    employer: 'Smith Enterprises',
    creditScore: 680,
  },
  {
    id: 'REV003',
    applicantId: '3',
    applicantName: 'Mike Johnson',
    nic: '881234569V',
    email: 'mike@example.com',
    phone: '+94 77 345 6789',
    loanAmount: 750000,
    duration: 48,
    submittedBy: 'Officer A',
    submittedAt: '2024-01-13T09:15:00',
    status: 'pending' as ReviewStatus,
    monthlyIncome: 180000,
    employmentType: 'Full-time',
    employer: 'Finance Solutions',
    creditScore: 750,
  },
];

type ReviewStatus = 'pending' | 'approved' | 'rejected';

interface Review {
  id: string;
  applicantId: string;
  applicantName: string;
  nic: string;
  email: string;
  phone: string;
  loanAmount: number;
  duration: number;
  submittedBy: string;
  submittedAt: string;
  status: ReviewStatus;
  monthlyIncome: number;
  employmentType: string;
  employer: string;
  creditScore: number;
}

export default function ReviewPage() {
  const { isManager } = useAuth();
  const [reviews, setReviews] = useState<Review[]>(mockPendingReviews);
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState<{ open: boolean; action: 'approve' | 'reject' | null }>({
    open: false,
    action: null,
  });
  const [rejectionReason, setRejectionReason] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  // Filter reviews by status
  const pendingReviews = reviews.filter((r) => r.status === 'pending');
  const processedReviews = reviews.filter((r) => r.status !== 'pending');

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

  const handleViewDetails = (review: Review) => {
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

  const handleExecuteAction = () => {
    if (!selectedReview || !confirmDialog.action) return;

    const newStatus: ReviewStatus = confirmDialog.action === 'approve' ? 'approved' : 'rejected';

    setReviews((prev) =>
      prev.map((r) =>
        r.id === selectedReview.id
          ? { ...r, status: newStatus }
          : r
      )
    );

    setConfirmDialog({ open: false, action: null });
    handleCloseDetails();
  };

  const getStatusChip = (status: ReviewStatus) => {
    switch (status) {
      case 'approved':
        return <Chip label="Approved" color="success" size="small" icon={<CheckCircle />} />;
      case 'rejected':
        return <Chip label="Rejected" color="error" size="small" icon={<Cancel />} />;
      default:
        return <Chip label="Pending" color="warning" size="small" />;
    }
  };

  const renderReviewTable = (reviewList: Review[]) => (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Applicant</TableCell>
            <TableCell>NIC</TableCell>
            <TableCell align="right">Loan Amount</TableCell>
            <TableCell align="center">Duration</TableCell>
            <TableCell>Submitted By</TableCell>
            <TableCell>Submitted At</TableCell>
            <TableCell align="center">Status</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {reviewList.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                <Typography color="text.secondary">No reviews found</Typography>
              </TableCell>
            </TableRow>
          ) : (
            reviewList.map((review) => (
              <TableRow key={review.id} hover>
                <TableCell>
                  <Typography fontWeight={600}>{review.applicantName}</Typography>
                </TableCell>
                <TableCell>{review.nic}</TableCell>
                <TableCell align="right">{formatCurrency(review.loanAmount)}</TableCell>
                <TableCell align="center">{review.duration} months</TableCell>
                <TableCell>{review.submittedBy}</TableCell>
                <TableCell>{formatDate(review.submittedAt)}</TableCell>
                <TableCell align="center">{getStatusChip(review.status)}</TableCell>
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
                <Schedule sx={{ fontSize: 50, color: 'warning.light' }} />
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
                    {reviews.filter((r) => r.status === 'approved').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Approved
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 50, color: 'success.light' }} />
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
                    {reviews.filter((r) => r.status === 'rejected').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Rejected
                  </Typography>
                </Box>
                <Cancel sx={{ fontSize: 50, color: 'error.light' }} />
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

        {activeTab === 0 && renderReviewTable(pendingReviews)}
        {activeTab === 1 && renderReviewTable(processedReviews)}
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
                      <Grid item xs={7}><Typography variant="body2" fontWeight={600}>{selectedReview.applicantName}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">NIC:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.nic}</Typography></Grid>
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
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.duration} months</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Monthly EMI:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{formatCurrency(Math.round(selectedReview.loanAmount / selectedReview.duration * 1.12))}</Typography></Grid>
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
                      <Grid item xs={7}><Typography variant="body2">{formatCurrency(selectedReview.monthlyIncome)}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Employment:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.employmentType}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Employer:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.employer}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Credit Score:</Typography></Grid>
                      <Grid item xs={7}>
                        <Chip
                          label={selectedReview.creditScore}
                          size="small"
                          color={selectedReview.creditScore >= 700 ? 'success' : selectedReview.creditScore >= 600 ? 'warning' : 'error'}
                        />
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
                        Submission Details
                      </Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={1}>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Submitted By:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{selectedReview.submittedBy}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Submitted At:</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2">{formatDate(selectedReview.submittedAt)}</Typography></Grid>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">Status:</Typography></Grid>
                      <Grid item xs={7}>{getStatusChip(selectedReview.status)}</Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Rejection Reason (only for reject action) */}
              {selectedReview.status === 'pending' && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Rejection Reason (required if rejecting)"
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="Enter the reason for rejection..."
                  />
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          {selectedReview?.status === 'pending' && (
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
            <strong>{selectedReview?.applicantName}</strong>?
          </Typography>
          {confirmDialog.action === 'approve' && (
            <Alert severity="info" sx={{ mt: 2 }}>
              This will approve a loan of {selectedReview && formatCurrency(selectedReview.loanAmount)} for{' '}
              {selectedReview?.duration} months.
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
