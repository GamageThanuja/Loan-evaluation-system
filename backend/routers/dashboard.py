"""
Dashboard API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

from database.client import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/financial-stats")
async def get_financial_stats() -> Dict[str, Any]:
    """
    Get financial statistics for dashboard
    Returns real data from database instead of hardcoded values
    """
    try:
        # Get applicant counts and approval stats
        applicants_result = db.client.table("applicants").select("*").execute()
        applicants = applicants_result.data if applicants_result.data else []
        
        total_applicants = len(applicants)
        approved_applicants = [a for a in applicants if a.get("eligibility_status") == "approved"]
        pending_applicants = [a for a in applicants if a.get("eligibility_status") == "under_review"]
        
        # Calculate loan amounts
        total_loan_amount = sum(float(a.get("loan_amount", 0)) for a in approved_applicants)
        
        # Get repayment history for interest calculations
        repayment_result = db.client.table("repayment_history").select("*").execute()
        repayments = repayment_result.data if repayment_result.data else []
        
        # Calculate total interest earned from repayments
        total_interest_earned = 0
        for repayment in repayments:
            original_amount = float(repayment.get("original_amount", 0))
            remaining_balance = float(repayment.get("remaining_balance", 0))
            paid_amount = original_amount - remaining_balance
            
            # Estimate interest portion (roughly 60% of payments go to interest in early payments)
            if paid_amount > 0:
                estimated_interest = paid_amount * 0.4  # Conservative estimate
                total_interest_earned += estimated_interest
        
        # Calculate average interest rate
        avg_interest_rate = 12.0  # Standard rate, could be calculated from repayment_history
        if repayments:
            rates = [float(r.get("interest_rate", 12.0)) for r in repayments if r.get("interest_rate")]
            if rates:
                avg_interest_rate = sum(rates) / len(rates)
        
        # Get recent activity (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_applicants = [a for a in applicants if a.get("created_at", "") >= thirty_days_ago]
        
        approval_rate = (len(approved_applicants) / total_applicants * 100) if total_applicants > 0 else 0
        
        return {
            "success": True,
            "data": {
                "totalLoansDisbursed": len(approved_applicants),
                "totalLoanAmount": total_loan_amount,
                "totalInterestEarned": total_interest_earned,
                "avgInterestRate": round(avg_interest_rate, 2),
                "approvalRate": round(approval_rate, 2),
                "pendingReviews": len(pending_applicants),
                "applicationsReceived": len(recent_applicants),
                "loansApproved": len([a for a in recent_applicants if a.get("eligibility_status") == "approved"]),
                "totalApplications": total_applicants
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching financial stats: {e}")
        return {
            "success": False,
            "error": "Failed to fetch financial statistics",
            "data": None
        }

@router.get("/monthly-summary")
async def get_monthly_summary() -> Dict[str, Any]:
    """
    Get monthly summary statistics
    """
    try:
        # Get current month data
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_start_str = current_month_start.isoformat()
        
        # Get all applicants for current month
        applicants_result = db.client.table("applicants").select("*").gte("created_at", current_month_start_str).execute()
        monthly_applicants = applicants_result.data if applicants_result.data else []
        
        monthly_approved = [a for a in monthly_applicants if a.get("eligibility_status") == "approved"]
        monthly_pending = [a for a in monthly_applicants if a.get("eligibility_status") == "under_review"]
        
        # Get active loans count
        repayment_result = db.client.table("repayment_history").select("*").eq("loan_status", "active").execute()
        active_loans = len(repayment_result.data) if repayment_result.data else 0
        
        return {
            "success": True,
            "data": {
                "applicationsReceived": len(monthly_applicants),
                "loansApproved": len(monthly_approved),
                "pendingReview": len(monthly_pending),
                "activeLoans": active_loans,
                "avgInterestRate": 12.0,  # Could be calculated from current active loans
                "monthName": current_month_start.strftime("%B %Y")
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching monthly summary: {e}")
        return {
            "success": False,
            "error": "Failed to fetch monthly summary",
            "data": None
        }

@router.get("/recent-applications")
async def get_recent_applications(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent loan applications for dashboard table
    """
    try:
        # Get recent applicants with eligibility data
        applicants_result = db.client.table("applicants").select("*").order("created_at", desc=True).limit(limit).execute()
        applicants = applicants_result.data if applicants_result.data else []
        
        recent_apps = []
        for app in applicants:
            # Get the latest prediction/eligibility for this applicant
            prediction_result = db.client.table("predictions").select("*").eq("applicant_id", app["id"]).order("created_at", desc=True).limit(1).execute()
            
            latest_prediction = None
            if prediction_result.data and len(prediction_result.data) > 0:
                latest_prediction = prediction_result.data[0]
            
            recent_apps.append({
                "id": app["id"],
                "applicantName": f"{app.get('first_name', '')} {app.get('last_name', '')}".strip() or app.get("name", "Unknown"),
                "riskScore": latest_prediction.get("risk_score", 0) if latest_prediction else 0,
                "decision": latest_prediction.get("decision", "PENDING") if latest_prediction else "PENDING",
                "timestamp": latest_prediction.get("created_at", app.get("created_at", "")) if latest_prediction else app.get("created_at", ""),
                "status": (app.get("eligibility_status") or "new").replace("_", " ").title(),
                "loanAmount": app.get("loan_amount", 0),
                "eligibilityStatus": app.get("eligibility_status") or "new"
            })
        
        return {
            "success": True,
            "data": recent_apps
        }
        
    except Exception as e:
        logger.error(f"Error fetching recent applications: {e}")
        return {
            "success": False,
            "error": "Failed to fetch recent applications",
            "data": []
        }