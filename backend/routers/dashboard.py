"""
Dashboard API endpoints
Suitable for LoanWise v4.0
"""
from fastapi import APIRouter
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from database.client import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/financial-stats")
async def get_financial_stats() -> Dict[str, Any]:
    """Get financial statistics for dashboard"""
    try:
        # Fetch all applicants
        result = db.client.table("applicants").select("*").execute()
        applicants = result.data or []
        
        total_applicants = len(applicants)
        
        # Status filtering based on standard strings
        approved = [a for a in applicants if a.get("eligibility_status") == "eligible" or a.get("status") == "approved"]
        pending = [a for a in applicants if a.get("eligibility_status") in ["pending", "under_review", None]]
        
        total_loan_amount = sum(float(a.get("loan_amount", 0) or 0) for a in approved)
        
        # Simple interest estimation
        total_interest_earned = total_loan_amount * 0.12 * 0.5 
        
        return {
            "success": True,
            "data": {
                "totalLoansDisbursed": len(approved),
                "totalLoanAmount": total_loan_amount,
                "totalInterestEarned": total_interest_earned,
                "avgInterestRate": 12.0,
                "approvalRate": round((len(approved) / total_applicants * 100) if total_applicants else 0, 1),
                "pendingReviews": len(pending),
                "totalApplications": total_applicants
            }
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/recent-applications")
async def get_recent_applications(limit: int = 10) -> Dict[str, Any]:
    """Get recent loan applications"""
    try:
        # Fetch recent applicants
        result = db.client.table("applicants").select("*").order("created_at", desc=True).limit(limit).execute()
        applicants = result.data or []
        
        recent_apps = []
        for app in applicants:
            risk_score = app.get("risk_score", 0.0)
            status_text = app.get("eligibility_status") or "pending"
            full_name = f"{app.get('first_name', '')} {app.get('last_name', '')}".strip()
            applicant_name = (
                full_name
                or app.get("name")
                or app.get("full_name")
                or app.get("applicant_name")
                or app.get("email")
                or app.get("nic")
                or f"Applicant #{app.get('id', '')}"
            )
            
            decision = "PENDING"
            if status_text == "eligible":
                decision = "APPROVE"
            elif status_text == "not_eligible":
                decision = "REJECT"

            recent_apps.append({
                "id": app["id"],
                "applicantName": applicant_name,
                "riskScore": risk_score,
                "status": status_text.replace("_", " ").title(),
                "decision": decision,
                "loanAmount": app.get("loan_amount", 0),
                "date": app.get("created_at", "")
            })
            
        return {"success": True, "data": recent_apps}
        
    except Exception as e:
        logger.error(f"Recent apps error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/monthly-summary")
async def get_monthly_summary() -> Dict[str, Any]:
    """Get monthly summary statistics"""
    try:
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_start_str = current_month_start.isoformat()
        
        result = db.client.table("applicants").select("*").gte("created_at", current_month_start_str).execute()
        monthly_applicants = result.data or []
        
        approved = [a for a in monthly_applicants if a.get("eligibility_status") == "eligible"]
        pending = [a for a in monthly_applicants if a.get("eligibility_status") in ["pending", "under_review", None]]
        
        return {
            "success": True,
            "data": {
                "applicationsReceived": len(monthly_applicants),
                "loansApproved": len(approved),
                "pendingReview": len(pending),
                "activeLoans": len(approved), # Simplified
                "monthName": current_month_start.strftime("%B %Y")
            }
        }
    except Exception as e:
        logger.error(f"Monthly summary error: {e}")
        return {"success": False, "error": str(e)}
