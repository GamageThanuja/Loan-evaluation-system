'use client';

import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
} from '@mui/material';
import { FileDownload } from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useState } from 'react';
import { useModelPerformance, useBatchPredictions } from '@/hooks/useModel';
import predictionService from '@/services/prediction';
import { ChartSkeleton, TableSkeleton } from '@/components/ui/LoadingSkeleton';
import { formatDate, formatPercent } from '@/lib/utils';

export default function ReportsPage() {
  const [exportFormat, setExportFormat] = useState<'csv' | 'pdf'>('csv');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [exporting, setExporting] = useState(false);

  const { data: performance, isLoading: performanceLoading } = useModelPerformance();
  const { data: batches, isLoading: batchesLoading } = useBatchPredictions();

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await predictionService.exportData(exportFormat);
      if (response.success && response.data) {
        const url = window.URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.download = `report-${Date.now()}.${exportFormat}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExporting(false);
    }
  };

  // Mock current metrics
  const currentMetrics = {
    accuracy: 0.9197,
    precision: 0.891,
    recall: 0.865,
    f1Score: 0.878,
    auc: 0.7545,
  };

  // Decision distribution data
  const decisionData = [
    { name: 'Approved', value: 683, color: '#2e7d32' },
    { name: 'Rejected', value: 214, color: '#d32f2f' },
    { name: 'Manual Review', value: 103, color: '#f59e0b' },
  ];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Reports & Analytics
        </Typography>
        <Typography variant="body2" color="text.secondary">
          View model performance and export data
        </Typography>
      </Box>

      {/* Export Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Export Data
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                label="End Date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                select
                label="Format"
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value as 'csv' | 'pdf')}
              >
                <MenuItem value="csv">CSV</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<FileDownload />}
                onClick={handleExport}
                disabled={exporting}
                sx={{ height: 56 }}
              >
                {exporting ? 'Exporting...' : 'Export'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Model Performance Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Model Performance Over Time
              </Typography>
              {performanceLoading ? (
                <ChartSkeleton height={300} />
              ) : performance ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={performance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0.7, 1]} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="accuracy" stroke="#1976d2" name="Accuracy" />
                    <Line type="monotone" dataKey="precision" stroke="#2e7d32" name="Precision" />
                    <Line type="monotone" dataKey="recall" stroke="#f59e0b" name="Recall" />
                    <Line type="monotone" dataKey="auc" stroke="#d32f2f" name="AUC" />
                  </LineChart>
                </ResponsiveContainer>
              ) : null}
            </CardContent>
          </Card>
        </Grid>

        {/* Current Metrics */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Current Metrics
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">Accuracy</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {formatPercent(currentMetrics.accuracy)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={currentMetrics.accuracy * 100}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">Precision</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {formatPercent(currentMetrics.precision)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={currentMetrics.precision * 100}
                  color="success"
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">Recall</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {formatPercent(currentMetrics.recall)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={currentMetrics.recall * 100}
                  color="warning"
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">F1 Score</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {formatPercent(currentMetrics.f1Score)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={currentMetrics.f1Score * 100}
                  color="info"
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">AUC</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {formatPercent(currentMetrics.auc)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={currentMetrics.auc * 100}
                  color="error"
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Decision Distribution */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Decision Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={decisionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#1976d2" radius={[8, 8, 0, 0]}>
                    {decisionData.map((entry, index) => (
                      <Bar key={index} dataKey="value" fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Batch Predictions */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Batch Predictions History
              </Typography>
              {batchesLoading ? (
                <TableSkeleton rows={3} />
              ) : batches && batches.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>File Name</TableCell>
                        <TableCell align="right">Total</TableCell>
                        <TableCell align="right">Approved</TableCell>
                        <TableCell align="right">Rejected</TableCell>
                        <TableCell>Date</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {batches.map((batch) => (
                        <TableRow key={batch.id}>
                          <TableCell>{batch.fileName}</TableCell>
                          <TableCell align="right">{batch.totalRecords}</TableCell>
                          <TableCell align="right">{batch.approved}</TableCell>
                          <TableCell align="right">{batch.rejected}</TableCell>
                          <TableCell>
                            <Typography variant="caption">
                              {formatDate(batch.createdAt)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                  No batch predictions yet
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
