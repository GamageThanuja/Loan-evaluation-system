"""
Loan Details Router
Handles fetching single loan application details
Suitable for LoanWise v4.0
"""

from fastapi import APIRouter, HTTPException, status, Depends
from database.client import db
from middleware.auth import AuthMiddleware

router = APIRouter(prefix="/api/loan-details", tags=["Loan Details"])

@router.get("/{applicant_id}")
async def get_loan_details(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Get comprehensive loan application details"""
    try:
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
            
        return {
            "success": True,
            "data": applicant
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
