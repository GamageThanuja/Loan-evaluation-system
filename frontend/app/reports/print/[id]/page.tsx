'use client';

import { useEffect, useState } from 'react';
import { useApplicantOperations } from '@/hooks/useApplicants';
import { predictionService } from '@/services/prediction';
import { formatCurrency } from '@/utils/formatters';
import { EligibilityResult } from '@/types';

interface PageProps {
    params: {
        id: string;
    };
}

export default function PrintReportPage({ params }: PageProps) {
    const { id } = params;
    const {
        applicant,
        loanDetails,
        repaymentHistory,
        isLoading,
        isLoadingRepaymentHistory,
    } = useApplicantOperations(id);
    const [eligibilityData, setEligibilityData] = useState<EligibilityResult | null>(null);
    const [isEligibilityLoading, setIsEligibilityLoading] = useState(false);

    useEffect(() => {
        if (!id || !applicant) {
            setEligibilityData(null);
            return;
        }

        const applicantId = Number(id);
        if (!Number.isFinite(applicantId)) {
            setEligibilityData(null);
            return;
        }

        const requestedAmount = loanDetails?.loanAmount ?? applicant.loanAmount ?? 0;
        const termMonths = loanDetails?.loanTermMonths ?? loanDetails?.loanTerm ?? applicant.loanTermMonths ?? applicant.loanTerm ?? 12;
        const income = loanDetails?.monthlyIncome ?? applicant.monthlyIncome;

        if (requestedAmount <= 0 || termMonths <= 0) {
            setEligibilityData(null);
            return;
        }

        let isActive = true;
        setIsEligibilityLoading(true);
        predictionService
            .checkEligibility(applicantId, requestedAmount, termMonths, income)
            .then((response) => {
                if (!isActive) return;
                if (response.success && response.data) {
                    setEligibilityData(response.data);
                } else {
                    setEligibilityData(null);
                }
            })
            .catch(err => console.error("Failed to fetch eligibility", err))
            .finally(() => {
                if (isActive) setIsEligibilityLoading(false);
            });

        return () => {
            isActive = false;
        };
    }, [id, applicant, loanDetails]);

    if (isLoading || isLoadingRepaymentHistory || !applicant || isEligibilityLoading) {
        return <div style={{ padding: 32, textAlign: 'center' }}>Loading report data...</div>;
    }

    // Derived Data
    const monthlyIncome = loanDetails?.monthlyIncome ?? applicant.monthlyIncome ?? eligibilityData?.financial_profile?.monthly_income ?? 0;
    const loanAmount = loanDetails?.loanAmount ?? applicant.loanAmount ?? eligibilityData?.loan_details?.requested_amount ?? 0;
    const loanTerm = loanDetails?.loanTermMonths ?? loanDetails?.loanTerm ?? applicant.loanTermMonths ?? applicant.loanTerm ?? eligibilityData?.loan_details?.loan_term_months ?? 12;
    const monthlyInstallment = loanTerm > 0 ? loanAmount / loanTerm : 0; // Simplified
    const debtToIncome = monthlyIncome > 0 ? (monthlyInstallment / monthlyIncome) * 100 : 0;

    const applicantName = applicant.name || `${applicant.firstName ?? ''} ${applicant.lastName ?? ''}`.trim() || 'Applicant';

    const existingLoanBalance = repaymentHistory?.summary?.totalRemaining ?? applicant.existingDebtAmount ?? 0;
    const exposureData = [
        { name: 'Existing Loans', value: existingLoanBalance },
        { name: 'This Request', value: loanAmount },
    ];

    const formatMonthLabel = (dateValue?: string) => {
        if (!dateValue) return 'N/A';
        const parsedDate = new Date(dateValue);
        if (Number.isNaN(parsedDate.getTime())) return 'N/A';
        return parsedDate.toLocaleString('en-US', { month: 'short', year: 'numeric' });
    };

    const estimatedExistingPayment = repaymentHistory?.summary?.nextPaymentAmount ?? 0;
    const estimatedOutflow = monthlyInstallment + estimatedExistingPayment;
    const schedule = repaymentHistory?.schedule || [];
    const cashFlowRows = schedule.length > 0
        ? schedule
            .filter((item) => item.dueDate || item.paidDate)
            .sort((a, b) => new Date(a.dueDate || a.paidDate || '').getTime() - new Date(b.dueDate || b.paidDate || '').getTime())
            .slice(-6)
            .map((item) => {
                const candidateOutflow = item.totalAmount || 0;
                const outflow = candidateOutflow > 0 && (loanAmount ? candidateOutflow < loanAmount : true) ? candidateOutflow : estimatedOutflow;
                return {
                    month: formatMonthLabel(item.dueDate || item.paidDate),
                    inflow: monthlyIncome,
                    outflow,
                };
            })
        : Array.from({ length: 6 }, (_, index) => {
            const date = new Date();
            date.setMonth(date.getMonth() - (5 - index));
            return {
                month: formatMonthLabel(date.toISOString()),
                inflow: monthlyIncome,
                outflow: estimatedOutflow,
            };
        });

    const featureRows = (eligibilityData?.feature_importance && eligibilityData.feature_importance.length > 0)
        ? eligibilityData.feature_importance
        : [
            ...(eligibilityData?.risk_factors || []).map((factor: any) => ({
                feature: factor.feature || factor.feature_name || 'Risk factor',
                importance: typeof factor.influence_strength === 'number' ? factor.influence_strength : null,
                direction: 'increases_risk',
            })),
            ...(eligibilityData?.protective_factors || []).map((factor: any) => ({
                feature: factor.feature || factor.feature_name || 'Protective factor',
                importance: typeof factor.influence_strength === 'number' ? factor.influence_strength : null,
                direction: 'decreases_risk',
            })),
        ];

    const concernItems = (eligibilityData?.risk_analysis?.concerns || []).map((item) => {
        const factor = item.factor ? `${item.factor}: ` : '';
        const explanation = item.explanation || '';
        return `${factor}${explanation}`.trim();
    }).filter((item) => item);

    const fallbackConcerns = (eligibilityData?.risk_factors || []).map((item: any) => {
        const factor = item.feature || item.feature_name || 'Risk factor';
        const explanation = item.explanation || item.description || '';
        return explanation ? `${factor}: ${explanation}` : factor;
    }).filter((item) => item);

    const rejectionConcerns = concernItems.length > 0 ? concernItems : fallbackConcerns;

    const defaultProbability = typeof eligibilityData?.probability === 'number'
        ? eligibilityData.probability
        : (typeof eligibilityData?.risk_score === 'number' ? eligibilityData.risk_score : null);
    const decisionStatus = eligibilityData?.decision || 'REJECT';

    return (
        <div
            id="report-content"
            style={{
                padding: 32,
                maxWidth: '210mm',
                margin: '0 auto',
                background: '#ffffff',
                minHeight: '100vh',
                color: '#111111',
                fontFamily: 'Arial, sans-serif',
                lineHeight: 1.5,
            }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '2px solid #1976d2', paddingBottom: 12, marginBottom: 24 }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: 28, color: '#1976d2' }}>Loan Rejection Report</h1>
                    <div style={{ color: '#555555' }}>Confidential Assessment Document</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 16, fontWeight: 700 }}>{applicantName}</div>
                    <div style={{ fontSize: 12 }}>ID: {applicant.id}</div>
                    <div style={{ fontSize: 12 }}>Date: {new Date().toLocaleDateString()}</div>
                </div>
            </div>

            <div style={{ border: '1px solid #dee2e6', background: '#f8f9fa', padding: 16, marginBottom: 16 }}>
                <h2 style={{ marginTop: 0, fontSize: 18 }}>1. AI Explainability (SHAP Analysis)</h2>
                <p style={{ marginTop: 0, color: '#555555' }}>
                    Feature importance indicating how each factor influenced the loan decision. Positive values increase rejection risk, while negative values improve eligibility.
                </p>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                    <thead>
                        <tr>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #cccccc', paddingBottom: 6 }}>Feature</th>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #cccccc', paddingBottom: 6 }}>Impact</th>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #cccccc', paddingBottom: 6 }}>Direction</th>
                        </tr>
                    </thead>
                    <tbody>
                        {featureRows.map((entry: any, index: number) => (
                            <tr key={`feature-${index}`}>
                                <td style={{ padding: '6px 0' }}>{entry.feature}</td>
                                <td style={{ padding: '6px 0' }}>
                                    {typeof entry.importance === 'number' ? `${(entry.importance * 100).toFixed(1)}%` : 'N/A'}
                                </td>
                                <td style={{ padding: '6px 0' }}>
                                    {entry.direction === 'increases_risk'
                                        ? 'Increases risk'
                                        : entry.direction === 'decreases_risk'
                                            ? 'Improves eligibility'
                                            : 'Neutral'}
                                </td>
                            </tr>
                        ))}
                        {featureRows.length === 0 && (
                            <tr>
                                <td colSpan={3} style={{ padding: '6px 0', color: '#777777' }}>No feature importance data available.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div style={{ border: '1px solid #ffcdd2', background: '#fff5f5', padding: 16, marginBottom: 16 }}>
                <h2 style={{ marginTop: 0, fontSize: 18 }}>2. Key Rejection Reasons</h2>
                <p style={{ marginTop: 0 }}>
                    The application for <strong>{formatCurrency(loanAmount)}</strong> was declined due to the following primary concerns:
                </p>
                <ul style={{ margin: 0, paddingLeft: 18 }}>
                    {rejectionConcerns.map((reason: string, index: number) => (
                        <li key={`reason-${index}`} style={{ marginBottom: 6 }}>{reason}</li>
                    ))}
                    {rejectionConcerns.length === 0 && (
                        <li style={{ color: '#777777' }}>No detailed concerns found.</li>
                    )}
                </ul>
            </div>

            <div style={{ border: '1px solid #b3e5fc', background: '#f0f9ff', padding: 16, marginBottom: 24 }}>
                <h2 style={{ marginTop: 0, fontSize: 18 }}>3. Eligibility Improvement Suggestions</h2>
                <ul style={{ margin: 0, paddingLeft: 18 }}>
                    {eligibilityData?.recommendations?.map((rec: string, index: number) => (
                        <li key={`rec-${index}`} style={{ marginBottom: 6 }}>{rec}</li>
                    ))}
                    {(!eligibilityData?.recommendations || eligibilityData.recommendations.length === 0) && (
                        <li style={{ color: '#777777' }}>No specific recommendations available.</li>
                    )}
                </ul>
            </div>

            <div style={{ borderTop: '1px solid #dddddd', margin: '24px 0' }} />

            <h2 style={{ fontSize: 18 }}>4. Customer Profile & Exposure</h2>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
                <div style={{ flex: '1 1 280px' }}>
                    <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 8 }}>Total Exposure Distribution</div>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                        <thead>
                            <tr>
                                <th style={{ textAlign: 'left', borderBottom: '1px solid #cccccc', paddingBottom: 6 }}>Type</th>
                                <th style={{ textAlign: 'right', borderBottom: '1px solid #cccccc', paddingBottom: 6 }}>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {exposureData.map((entry, index) => (
                                <tr key={`exposure-${index}`}>
                                    <td style={{ padding: '6px 0' }}>{entry.name}</td>
                                    <td style={{ padding: '6px 0', textAlign: 'right' }}>{formatCurrency(entry.value)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div style={{ flex: '1 1 280px' }}>
                    <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 8 }}>Debt-to-Income Ratio</div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                        <div style={{ fontSize: 28, fontWeight: 700, color: debtToIncome > 50 ? '#d32f2f' : '#ed6c02' }}>
                            {debtToIncome.toFixed(1)}%
                        </div>
                        <div style={{ fontSize: 12, color: '#777777' }}>(Threshold: 40%)</div>
                    </div>
                    <div style={{ marginTop: 8, background: '#eeeeee', height: 10, borderRadius: 6 }}>
                        <div
                            style={{
                                width: `${Math.min(debtToIncome, 100)}%`,
                                height: '100%',
                                borderRadius: 6,
                                background: debtToIncome > 50 ? '#d32f2f' : '#ed6c02',
                            }}
                        />
                    </div>
                </div>
            </div>

            <h2 style={{ fontSize: 18 }}>5. Cash Flow & Repayment Capacity</h2>
            <div style={{ marginBottom: 24 }}>
                <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 8 }}>Monthly Inflows vs Outflows</div>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                    <thead>
                        <tr>
                            <th style={{ textAlign: 'left', borderBottom: '1px solid #cccccc', paddingBottom: 6 }}>Month</th>
                            <th style={{ textAlign: 'right', borderBottom: '1px solid #cccccc', paddingBottom: 6 }}>Inflow</th>
                            <th style={{ textAlign: 'right', borderBottom: '1px solid #cccccc', paddingBottom: 6 }}>Outflow</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cashFlowRows.map((row) => (
                            <tr key={row.month}>
                                <td style={{ padding: '6px 0' }}>{row.month}</td>
                                <td style={{ padding: '6px 0', textAlign: 'right' }}>{formatCurrency(row.inflow)}</td>
                                <td style={{ padding: '6px 0', textAlign: 'right' }}>{formatCurrency(row.outflow)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <h2 style={{ fontSize: 18 }}>6. Collateral Analysis</h2>
            <div style={{ padding: 12, background: '#f7f7f7', marginBottom: 24, fontSize: 12, textAlign: 'center', color: '#777777' }}>
                No collateral data linked to this application. LTV Ratio cannot be calculated.
            </div>

            <h2 style={{ fontSize: 18 }}>7. Risk Scoring & Decisioning</h2>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <div style={{ flex: '1 1 140px', border: '1px solid #dddddd', padding: 12, textAlign: 'center' }}>
                    <div style={{ fontSize: 11, color: '#666666' }}>Credit Score</div>
                    <div style={{ fontSize: 20, fontWeight: 700 }}>{applicant.creditScore || 'N/A'}</div>
                </div>
                <div style={{ flex: '1 1 140px', border: '1px solid #ffebee', padding: 12, textAlign: 'center', color: '#d32f2f' }}>
                    <div style={{ fontSize: 11 }}>Default Probability</div>
                    <div style={{ fontSize: 20, fontWeight: 700 }}>
                        {typeof defaultProbability === 'number' ? (defaultProbability * 100).toFixed(1) + '%' : 'N/A'}
                    </div>
                </div>
                <div
                    style={{
                        flex: '2 1 240px',
                        background: decisionStatus === 'APPROVE' ? '#2e7d32' : '#d32f2f',
                        color: '#ffffff',
                        padding: 12,
                        textAlign: 'center',
                    }}
                >
                    <div style={{ fontSize: 13 }}>Final Decision</div>
                    <div style={{ fontSize: 22, fontWeight: 800 }}>
                        {decisionStatus === 'APPROVE' ? 'APPROVE' : 'DECLINE'}
                    </div>
                </div>
            </div>

            <div style={{ marginTop: 32, textAlign: 'center', color: '#777777', fontSize: 11 }}>
                Generated by Intelligent Loan Evaluation System on {new Date().toLocaleString()}
            </div>
        </div>
    );
}
