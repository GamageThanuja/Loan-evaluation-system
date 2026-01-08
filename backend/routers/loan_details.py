"""
Loan Details Router
Handles loan application details including audit trail, repayment history, credit history, and transactions
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add parent directories to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field

# Import database client
from database.client import db
from middleware.auth import AuthMiddleware

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

# ============================================
# ENDPOINTS
# ============================================

@router.get("/{applicant_id}")
async def get_loan_details(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get comprehensive loan application details
    
    - **applicant_id**: Loan application ID
    
    Returns complete loan information including:
    - Audit trail
    - Repayment schedule and summary
    - Credit history and profile
    - Transaction history
    
    **Authentication required**: Manager or Loan Officer
    """
    try:
        # Get loan application from database
        loan_application = db.get_applicant_by_id(applicant_id)
        
        if not loan_application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan application not found"
            )
        
        # TODO: Fetch related data from database
        # - Audit logs from audit_logs table
        # - Repayment schedule from repayment_schedule table
        # - Credit history from credit_history table
        # - Transactions from transactions table
        
        return {
            "success": True,
            "data": loan_application
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch loan details: {str(e)}"
        )


@router.get("/{applicant_id}/audit-log")
async def get_audit_log(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get audit log for a specific loan application
    
    - **applicant_id**: Loan application ID
    
    **Authentication required**: Manager or Loan Officer
    """
    try:
        # TODO: Fetch from audit_logs table
        # SELECT * FROM audit_logs WHERE applicant_id = applicant_id ORDER BY timestamp DESC
        
        audit_logs = []  # Replace with actual database query
        
        return {
            "success": True,
            "data": audit_logs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit log: {str(e)}"
        )


@router.get("/{applicant_id}/repayment")
async def get_repayment_info(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get repayment schedule and summary
    
    - **applicant_id**: Loan application ID
    
    **Authentication required**: Manager or Loan Officer
    """
    try:
        # TODO: Fetch from repayment_schedule table
        # SELECT * FROM repayment_schedule WHERE loan_id = applicant_id ORDER BY installment_number
        
        schedule = []  # Replace with actual database query
        summary = {}   # Calculate summary from schedule
        
        return {
            "success": True,
            "data": {
                "schedule": schedule,
                "summary": summary
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch repayment info: {str(e)}"
        )


@router.get("/{applicant_id}/credit-history")
async def get_credit_history(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get credit history and profile
    
    - **applicant_id**: Loan application ID
    
    **Authentication required**: Manager or Loan Officer
    """
    try:
        # TODO: Fetch from credit_history table
        # SELECT * FROM credit_history WHERE applicant_id = applicant_id ORDER BY date DESC
        
        credit_profile = {}  # Replace with actual database query
        
        return {
            "success": True,
            "data": credit_profile
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch credit history: {str(e)}"
        )


@router.get("/{applicant_id}/transactions")
async def get_transactions(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get transaction history and summary
    
    - **applicant_id**: Loan application ID
    
    **Authentication required**: Manager or Loan Officer
    """
    try:
        # TODO: Fetch from transactions table
        # SELECT * FROM transactions WHERE loan_id = applicant_id ORDER BY date DESC
        
        transactions = []  # Replace with actual database query
        summary = {}       # Calculate summary from transactions
        
        return {
            "success": True,
            "data": {
                "transactions": transactions,
                "summary": summary
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transactions: {str(e)}"
        )
