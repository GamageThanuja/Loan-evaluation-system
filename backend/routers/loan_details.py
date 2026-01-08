"""
Loan Details Router
Handles loan application details including audit trail, repayment history, credit history, and transactions
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add parent directories to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/loan-details", tags=["Loan Details"])

# ============================================
# MODELS
# ============================================

class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    action: str = Field(..., description="Action type: created, updated, status_changed, reviewed, approved, rejected, payment_made, document_uploaded, note_added")
    performed_by: Dict[str, str] = Field(..., description="User who performed the action")
    description: str
    changes: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict] = None

class RepaymentScheduleItem(BaseModel):
    id: str
    loan_id: str
    installment_number: int
    due_date: str
    principal_amount: float
    interest_amount: float
    total_amount: float
    status: str = Field(..., description="Status: pending, paid, overdue, partial")
    paid_amount: Optional[float] = None
    paid_date: Optional[str] = None
    late_fee: Optional[float] = None
    remaining_balance: float

class RepaymentSummary(BaseModel):
    total_loan_amount: float
    total_paid: float
    total_remaining: float
    total_interest: float
    next_payment_due: str
    next_payment_amount: float
    overdue_amount: float
    number_of_payments: int
    payments_completed: int
    payment_status: str = Field(..., description="Status: on_time, late, defaulted, completed")

class CreditHistoryEntry(BaseModel):
    id: str
    date: str
    credit_score: int
    bureau: str = Field(..., description="Bureau: Experian, Equifax, TransUnion")
    reason: Optional[str] = None
    change: Optional[int] = None

class CreditProfile(BaseModel):
    current_score: int
    score_history: List[CreditHistoryEntry]
    credit_utilization: float
    total_credit_lines: int
    oldest_account: str
    recent_inquiries: int
    delinquencies: int
    public_records: int
    average_account_age: float

class Transaction(BaseModel):
    id: str
    date: str
    type: str = Field(..., description="Type: payment, disbursement, fee, refund, adjustment, penalty")
    amount: float
    description: str
    status: str = Field(..., description="Status: completed, pending, failed, reversed")
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    balance: float
    notes: Optional[str] = None

class TransactionSummary(BaseModel):
    total_transactions: int
    total_debits: float
    total_credits: float
    last_transaction: Optional[Transaction] = None
    monthly_transactions: List[Dict[str, Any]]

class LoanApplicationDetails(BaseModel):
    # Basic applicant info
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: str
    age: int
    gender: str
    marital_status: str
    dependents: int
    
    # Financial info
    annual_income: float
    employment_type: str
    employment_length: int
    credit_score: int
    
    # Loan info
    loan_amount: float
    loan_purpose: str
    loan_term: int
    interest_rate: float
    monthly_payment: float
    total_payable: float
    disbursement_date: Optional[str] = None
    maturity_date: Optional[str] = None
    
    # Status
    created_at: str
    updated_at: str
    status: str
    
    # Related data
    audit_log: List[AuditLogEntry]
    repayment_schedule: List[RepaymentScheduleItem]
    repayment_summary: RepaymentSummary
    credit_profile: CreditProfile
    transactions: List[Transaction]
    transaction_summary: TransactionSummary

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_mock_loan_details(applicant_id: str) -> LoanApplicationDetails:
    """Generate mock loan application details"""
    
    # Mock audit log
    audit_log = [
        AuditLogEntry(
            id="1",
            timestamp=datetime.now().isoformat(),
            action="approved",
            performed_by={"id": "1", "name": "Jane Smith", "role": "loan_officer"},
            description="Loan application approved and disbursed",
            metadata={"amount": 250000}
        ),
        AuditLogEntry(
            id="2",
            timestamp=datetime.now().isoformat(),
            action="reviewed",
            performed_by={"id": "2", "name": "Mike Johnson", "role": "manager"},
            description="Application reviewed and recommended for approval"
        ),
        AuditLogEntry(
            id="3",
            timestamp=datetime.now().isoformat(),
            action="status_changed",
            performed_by={"id": "1", "name": "Jane Smith", "role": "loan_officer"},
            description="Status changed from pending to under_review",
            changes=[{"field": "status", "oldValue": "pending", "newValue": "under_review"}]
        ),
        AuditLogEntry(
            id="4",
            timestamp=datetime.now().isoformat(),
            action="created",
            performed_by={"id": "1", "name": "Jane Smith", "role": "loan_officer"},
            description="Loan application created"
        )
    ]
    
    # Mock repayment schedule
    repayment_schedule = [
        RepaymentScheduleItem(
            id=f"payment-{i+1}",
            loan_id=applicant_id,
            installment_number=i+1,
            due_date=datetime.now().isoformat(),
            principal_amount=937.50,
            interest_amount=329.21,
            total_amount=1266.71,
            status="paid" if i < 3 else "overdue" if i == 3 else "pending",
            paid_amount=1266.71 if i < 3 else None,
            paid_date=datetime.now().isoformat() if i < 3 else None,
            late_fee=25 if i == 3 else None,
            remaining_balance=250000 - (937.50 * (i + 1))
        )
        for i in range(12)
    ]
    
    # Mock repayment summary
    repayment_summary = RepaymentSummary(
        total_loan_amount=250000,
        total_paid=3800.13,
        total_remaining=246199.87,
        total_interest=206195.60,
        next_payment_due=datetime.now().isoformat(),
        next_payment_amount=1291.71,
        overdue_amount=1291.71,
        number_of_payments=360,
        payments_completed=3,
        payment_status="late"
    )
    
    # Mock credit history
    credit_history = [
        CreditHistoryEntry(
            id=str(i+1),
            date=datetime.now().isoformat(),
            credit_score=720 - (i * 5),
            bureau=["Experian", "Equifax", "TransUnion"][i % 3],
            change=5 if i == 0 else -3 if i == 1 else 8 if i == 2 else 0,
            reason="Payment history updated" if i < 3 else None
        )
        for i in range(5)
    ]
    
    credit_profile = CreditProfile(
        current_score=720,
        score_history=credit_history,
        credit_utilization=0.28,
        total_credit_lines=5,
        oldest_account="2015-03-20",
        recent_inquiries=2,
        delinquencies=0,
        public_records=0,
        average_account_age=6.5
    )
    
    # Mock transactions
    transactions = [
        Transaction(
            id="1",
            date="2024-04-14",
            type="payment",
            amount=1266.71,
            description="Monthly payment - Installment #3",
            status="completed",
            payment_method="bank_transfer",
            reference_number="TXN-2024-0414-001",
            balance=247187.50
        ),
        Transaction(
            id="2",
            date="2024-03-14",
            type="payment",
            amount=1266.71,
            description="Monthly payment - Installment #2",
            status="completed",
            payment_method="bank_transfer",
            reference_number="TXN-2024-0314-001",
            balance=248125.00
        ),
        Transaction(
            id="3",
            date="2024-02-14",
            type="payment",
            amount=1266.71,
            description="Monthly payment - Installment #1",
            status="completed",
            payment_method="online",
            reference_number="TXN-2024-0214-001",
            balance=249062.50
        ),
        Transaction(
            id="4",
            date="2024-01-20",
            type="fee",
            amount=500,
            description="Loan processing fee",
            status="completed",
            reference_number="FEE-2024-001",
            balance=250000
        ),
        Transaction(
            id="5",
            date="2024-01-15",
            type="disbursement",
            amount=250000,
            description="Loan disbursement",
            status="completed",
            payment_method="bank_transfer",
            reference_number="DISB-2024-001",
            balance=250000
        )
    ]
    
    transaction_summary = TransactionSummary(
        total_transactions=5,
        total_debits=4300.13,
        total_credits=250000,
        last_transaction=transactions[0],
        monthly_transactions=[
            {"month": "Jan 2024", "count": 2, "amount": 250500},
            {"month": "Feb 2024", "count": 1, "amount": 1266.71},
            {"month": "Mar 2024", "count": 1, "amount": 1266.71},
            {"month": "Apr 2024", "count": 1, "amount": 1266.71}
        ]
    )
    
    return LoanApplicationDetails(
        id=applicant_id,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="(555) 123-4567",
        date_of_birth="1990-05-15",
        age=34,
        gender="M",
        marital_status="Married",
        dependents=2,
        annual_income=75000,
        employment_type="Employed",
        employment_length=8,
        credit_score=720,
        loan_amount=250000,
        loan_purpose="Home",
        loan_term=360,
        interest_rate=4.5,
        monthly_payment=1266.71,
        total_payable=456195.60,
        disbursement_date="2024-01-15",
        maturity_date="2054-01-15",
        created_at="2024-01-01T10:00:00Z",
        updated_at="2024-01-15T14:30:00Z",
        status="approved",
        audit_log=audit_log,
        repayment_schedule=repayment_schedule,
        repayment_summary=repayment_summary,
        credit_profile=credit_profile,
        transactions=transactions,
        transaction_summary=transaction_summary
    )

# ============================================
# ENDPOINTS
# ============================================

@router.get("/{applicant_id}", response_model=LoanApplicationDetails)
async def get_loan_details(applicant_id: str):
    """
    Get comprehensive loan application details
    
    - **applicant_id**: Loan application ID
    
    Returns complete loan information including:
    - Audit trail
    - Repayment schedule and summary
    - Credit history and profile
    - Transaction history
    """
    try:
        # TODO: Replace with actual database query
        # For now, return mock data
        loan_details = generate_mock_loan_details(applicant_id)
        
        return loan_details
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch loan details: {str(e)}"
        )


@router.get("/{applicant_id}/audit-log", response_model=List[AuditLogEntry])
async def get_audit_log(applicant_id: str):
    """
    Get audit log for a specific loan application
    
    - **applicant_id**: Loan application ID
    """
    try:
        loan_details = generate_mock_loan_details(applicant_id)
        return loan_details.audit_log
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit log: {str(e)}"
        )


@router.get("/{applicant_id}/repayment", response_model=Dict)
async def get_repayment_info(applicant_id: str):
    """
    Get repayment schedule and summary
    
    - **applicant_id**: Loan application ID
    """
    try:
        loan_details = generate_mock_loan_details(applicant_id)
        return {
            "schedule": loan_details.repayment_schedule,
            "summary": loan_details.repayment_summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch repayment info: {str(e)}"
        )


@router.get("/{applicant_id}/credit-history", response_model=CreditProfile)
async def get_credit_history(applicant_id: str):
    """
    Get credit history and profile
    
    - **applicant_id**: Loan application ID
    """
    try:
        loan_details = generate_mock_loan_details(applicant_id)
        return loan_details.credit_profile
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch credit history: {str(e)}"
        )


@router.get("/{applicant_id}/transactions", response_model=Dict)
async def get_transactions(applicant_id: str):
    """
    Get transaction history and summary
    
    - **applicant_id**: Loan application ID
    """
    try:
        loan_details = generate_mock_loan_details(applicant_id)
        return {
            "transactions": loan_details.transactions,
            "summary": loan_details.transaction_summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transactions: {str(e)}"
        )
