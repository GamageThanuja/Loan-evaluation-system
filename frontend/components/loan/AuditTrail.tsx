'use client';

import {
    Timeline,
    TimelineItem,
    TimelineSeparator,
    TimelineConnector,
    TimelineContent,
    TimelineDot,
    TimelineOppositeContent,
} from '@mui/lab';
import {
    Paper,
    Typography,
    Box,
    Chip,
    Accordion,
    AccordionSummary,
    AccordionDetails,
} from '@mui/material';
import {
    CheckCircle,
    Cancel,
    Edit,
    PersonAdd,
    Description,
    Payment,
    NoteAdd,
    ExpandMore,
} from '@mui/icons-material';
import { AuditLogEntry } from '@/types';
import { formatRelativeTime } from '@/lib/utils';

interface AuditTrailProps {
    auditLog: AuditLogEntry[];
}

const getActionIcon = (action: AuditLogEntry['action']) => {
    const iconProps = { fontSize: 'small' as const };

    switch (action) {
        case 'created':
            return <PersonAdd {...iconProps} />;
        case 'approved':
            return <CheckCircle {...iconProps} />;
        case 'rejected':
            return <Cancel {...iconProps} />;
        case 'updated':
        case 'status_changed':
            return <Edit {...iconProps} />;
        case 'payment_made':
            return <Payment {...iconProps} />;
        case 'document_uploaded':
            return <Description {...iconProps} />;
        case 'note_added':
            return <NoteAdd {...iconProps} />;
        default:
            return <Edit {...iconProps} />;
    }
};

const getActionColor = (action: AuditLogEntry['action']): 'success' | 'error' | 'primary' | 'info' | 'grey' => {
    switch (action) {
        case 'approved':
            return 'success';
        case 'rejected':
            return 'error';
        case 'payment_made':
            return 'primary';
        case 'created':
            return 'info';
        default:
            return 'grey';
    }
};

export default function AuditTrail({ auditLog }: AuditTrailProps) {
    if (!auditLog || auditLog.length === 0) {
        return (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                    No audit trail available
                </Typography>
            </Paper>
        );
    }

    return (
        <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight={600} sx={{ mb: 3 }}>
                Audit Trail
            </Typography>

            <Timeline position="right">
                {auditLog.map((entry, index) => (
                    <TimelineItem key={entry.id}>
                        <TimelineOppositeContent
                            sx={{ m: 'auto 0', minWidth: 120, textAlign: 'right' }}
                        >
                            <Typography variant="body2" color="text.secondary">
                                {formatRelativeTime(entry.timestamp)}
                            </Typography>
                            <Typography variant="caption" display="block" sx={{ mt: 0.5 }} color="text.secondary">
                                {new Date(entry.timestamp).toLocaleString()}
                            </Typography>
                        </TimelineOppositeContent>

                        <TimelineSeparator>
                            <TimelineDot color={getActionColor(entry.action)}>
                                {getActionIcon(entry.action)}
                            </TimelineDot>
                            {index < auditLog.length - 1 && <TimelineConnector />}
                        </TimelineSeparator>

                        <TimelineContent sx={{ py: '12px', px: 2 }}>
                            <Paper
                                elevation={0}
                                sx={{
                                    p: 2,
                                    bgcolor: 'background.default',
                                    border: '1px solid',
                                    borderColor: 'divider',
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                        borderColor: 'primary.main',
                                        boxShadow: 1,
                                    },
                                }}
                            >
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <Chip
                                        label={entry.action.replace(/_/g, ' ').toUpperCase()}
                                        size="small"
                                        color={(getActionColor(entry.action) === 'grey' ? 'default' : getActionColor(entry.action)) as 'success' | 'error' | 'primary' | 'info' | 'default'}
                                        variant="outlined"
                                    />
                                    <Chip
                                        label={entry.performedBy.role.replace(/_/g, ' ')}
                                        size="small"
                                        variant="outlined"
                                    />
                                </Box>

                                <Typography variant="body2" fontWeight={600} gutterBottom>
                                    {entry.description}
                                </Typography>

                                <Typography variant="caption" color="text.secondary" display="block">
                                    By {entry.performedBy.name}
                                </Typography>

                                {entry.changes && entry.changes.length > 0 && (
                                    <Accordion
                                        elevation={0}
                                        sx={{
                                            mt: 1,
                                            '&:before': { display: 'none' },
                                            bgcolor: 'transparent',
                                        }}
                                    >
                                        <AccordionSummary
                                            expandIcon={<ExpandMore />}
                                            sx={{ minHeight: 40, px: 0 }}
                                        >
                                            <Typography variant="caption" color="primary">
                                                View Changes ({entry.changes.length})
                                            </Typography>
                                        </AccordionSummary>
                                        <AccordionDetails sx={{ px: 0, pt: 0 }}>
                                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                                {entry.changes.map((change, idx) => (
                                                    <Box
                                                        key={idx}
                                                        sx={{
                                                            p: 1,
                                                            bgcolor: 'background.paper',
                                                            borderRadius: 1,
                                                            border: '1px solid',
                                                            borderColor: 'divider',
                                                        }}
                                                    >
                                                        <Typography variant="caption" fontWeight={600} display="block">
                                                            {change.field}
                                                        </Typography>
                                                        <Box sx={{ display: 'flex', gap: 1, mt: 0.5, alignItems: 'center' }}>
                                                            <Chip
                                                                label={change.oldValue || 'N/A'}
                                                                size="small"
                                                                sx={{ bgcolor: '#ffebee', color: '#c62828' }}
                                                            />
                                                            <Typography variant="caption">→</Typography>
                                                            <Chip
                                                                label={change.newValue}
                                                                size="small"
                                                                sx={{ bgcolor: '#e8f5e9', color: '#2e7d32' }}
                                                            />
                                                        </Box>
                                                    </Box>
                                                ))}
                                            </Box>
                                        </AccordionDetails>
                                    </Accordion>
                                )}
                            </Paper>
                        </TimelineContent>
                    </TimelineItem>
                ))}
            </Timeline>
        </Paper>
    );
}
