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


def _deprecated_history_endpoint(message: str) -> None:
    """Raise a standardized deprecation error for legacy loan-details history routes."""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail=message
    )

# ============================================
# ENDPOINTS
# ============================================

@router.get("/{applicant_id}")
async def get_loan_details(
    applicant_id: int,
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


@router.get("/{applicant_id}/audit-log", deprecated=True)
async def get_audit_log(
    applicant_id: int,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get audit log for a specific loan application
    
    - **applicant_id**: Loan application ID
    
    **Authentication required**: Manager or Loan Officer
    """
    _deprecated_history_endpoint(
        "This endpoint is deprecated. Use /api/applicants/{applicant_id}/audit-trail."
    )


@router.get("/{applicant_id}/repayment", deprecated=True)
async def get_repayment_info(
    applicant_id: int,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get repayment schedule and summary
    
    - **applicant_id**: Loan application ID
    
    **Authentication required**: Manager or Loan Officer
    """
    _deprecated_history_endpoint(
        "This endpoint is deprecated. Use /api/applicants/{applicant_id}/repayment-history."
    )


@router.get("/{applicant_id}/credit-history", deprecated=True)
async def get_credit_history(
    applicant_id: int,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get credit history and profile
    
    - **applicant_id**: Loan application ID
    
    **Authentication required**: Manager or Loan Officer
    """
    _deprecated_history_endpoint(
        "This endpoint is deprecated. Use /api/applicants/{applicant_id}/credit-history."
    )


@router.get("/{applicant_id}/transactions", deprecated=True)
async def get_transactions(
    applicant_id: int,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get transaction history and summary
    
    - **applicant_id**: Loan application ID
    
    **Authentication required**: Manager or Loan Officer
    """
    _deprecated_history_endpoint(
        "This endpoint is deprecated. Use /api/applicants/{applicant_id}/transactions."
    )
