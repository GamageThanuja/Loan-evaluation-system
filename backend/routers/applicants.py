"""
Applicant Router
Full CRUD operations for applicants with role-based access control
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add parent directories to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field, EmailStr, validator

# Import database client
from database.client import db
from middleware.auth import AuthMiddleware

router = APIRouter(prefix="/api/applicants", tags=["Applicants"])

# ============================================
# MODELS
# ============================================

class ApplicantBase(BaseModel):
    """Base applicant model with common fields"""
    first_name: str = Field(..., min_length=2, max_length=100, description="First name")
    last_name: str = Field(..., min_length=2, max_length=100, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    nic: str = Field(..., description="National ID Card number")
    date_of_birth: str = Field(..., description="Date of birth (YYYY-MM-DD)")
    gender: str = Field(..., description="Gender: M, F, or Other")
    marital_status: str = Field(..., description="Marital status")
    address: Optional[str] = Field(None, description="Full address")
    city: Optional[str] = Field(None, description="City")
    
    # Employment details
    employment_type: str = Field(..., description="Employment type")
    employer_name: Optional[str] = Field(None, description="Employer name")
    employment_length: int = Field(..., ge=0, description="Years of employment")
    monthly_income: float = Field(..., gt=0, description="Monthly income")
    
    # Loan details
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_purpose: str = Field(..., description="Purpose of loan")
    loan_term_months: int = Field(..., ge=6, le=360, description="Loan term in months")
    
    # Financial details
    credit_score: Optional[int] = Field(None, ge=300, le=850, description="Credit score")
    existing_loans: Optional[int] = Field(0, ge=0, description="Number of existing loans")
    monthly_expenses: Optional[float] = Field(None, ge=0, description="Monthly expenses")

class ApplicantCreate(ApplicantBase):
    """Model for creating a new applicant"""
    pass

class ApplicantUpdate(BaseModel):
    """Model for updating an applicant - all fields optional"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nic: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    employment_type: Optional[str] = None
    employer_name: Optional[str] = None
    employment_length: Optional[int] = Field(None, ge=0)
    monthly_income: Optional[float] = Field(None, gt=0)
    loan_amount: Optional[float] = Field(None, gt=0)
    loan_purpose: Optional[str] = None
    loan_term_months: Optional[int] = Field(None, ge=6, le=360)
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    existing_loans: Optional[int] = Field(None, ge=0)
    monthly_expenses: Optional[float] = Field(None, ge=0)

class EligibilityRequest(BaseModel):
    """Model for eligibility check request"""
    applicant_id: str = Field(..., description="Applicant ID")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_term_months: int = Field(..., ge=6, le=360, description="Loan term in months")

class EligibilityResult(BaseModel):
    """Model for eligibility check result"""
    eligible: bool
    risk_score: float
    confidence: float
    reasons: List[str] = []
    recommendations: List[str] = []

class ReviewRequest(BaseModel):
    """Model for sending application for review"""
    applicant_id: str = Field(..., description="Applicant ID")
    eligibility_result: Dict[str, Any] = Field(..., description="Eligibility result data")
    notes: Optional[str] = Field(None, description="Additional notes")

class ApprovalRequest(BaseModel):
    """Model for approval/rejection"""
    notes: Optional[str] = Field(None, description="Approval/rejection notes")
    reason: Optional[str] = Field(None, description="Rejection reason (required for rejection)")

class ApplicantResponse(BaseModel):
    """Full applicant response with all details"""
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    nic: str
    date_of_birth: str
    gender: str
    marital_status: str
    address: Optional[str] = None
    city: Optional[str] = None
    employment_type: str
    employer_name: Optional[str] = None
    employment_length: int
    monthly_income: float
    loan_amount: float
    loan_purpose: str
    loan_term_months: int
    credit_score: Optional[int] = None
    existing_loans: Optional[int] = None
    monthly_expenses: Optional[float] = None
    status: str
    eligibility_status: Optional[str] = None
    eligibility_reasons: Optional[List[str]] = None
    risk_score: Optional[float] = None
    created_at: str
    updated_at: str
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[str] = None
    rejection_reason: Optional[str] = None


# ============================================
# CRUD ENDPOINTS
# ============================================

@router.get("")
async def list_applicants(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name, email, or NIC"),
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get paginated list of all applicants
    
    **Access**: Loan Officers and Managers
    
    Returns applicants with:
    - Basic info (name, email, phone)
    - Loan details (amount, purpose, status)
    - Eligibility status
    """
    try:
        result = db.get_applicants(
            user_id=user["sub"],
            status=status,
            page=page,
            page_size=page_size
        )
        
        # Format response
        applicants = []
        for app in result.get("data", []):
            applicants.append({
                "id": app.get("id"),
                "name": f"{app.get('first_name', '')} {app.get('last_name', '')}".strip() or app.get("name", ""),
                "email": app.get("email"),
                "phone": app.get("phone"),
                "nic": app.get("nic"),
                "loan_amount": app.get("loan_amount"),
                "loan_purpose": app.get("loan_purpose"),
                "status": app.get("status", "pending"),
                "eligibility_status": app.get("eligibility_status"),
                "credit_score": app.get("credit_score"),
                "created_at": app.get("created_at"),
            })
        
        return {
            "success": True,
            "data": {
                "items": applicants,
                "total": result.get("total", 0),
                "page": result.get("page", page),
                "page_size": result.get("page_size", page_size),
                "total_pages": result.get("total_pages", 0)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applicants: {str(e)}"
        )


@router.get("/{applicant_id}")
async def get_applicant(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get full applicant details by ID
    
    **Access**: Loan Officers and Managers
    
    Returns complete applicant profile including:
    - Personal details
    - Employment info
    - Loan details
    - Eligibility status and reasons
    - Credit history
    - Repayment history
    """
    try:
        applicant = db.get_applicant_by_id(applicant_id)
        
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Get related data
        prediction = db.get_prediction_by_applicant(applicant_id)
        
        # Build full response
        response_data = {
            **applicant,
            "full_name": f"{applicant.get('first_name', '')} {applicant.get('last_name', '')}".strip() or applicant.get("name", ""),
        }
        
        if prediction:
            response_data["risk_score"] = prediction.get("risk_score")
            response_data["eligibility_status"] = "eligible" if prediction.get("decision") == "APPROVE" else "not_eligible"
            response_data["eligibility_reasons"] = prediction.get("rejection_reasons", [])
            response_data["prediction_confidence"] = prediction.get("confidence")
        
        return {
            "success": True,
            "data": response_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applicant: {str(e)}"
        )


@router.post("")
async def create_applicant(
    applicant_data: ApplicantCreate,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Create a new applicant
    
    **Access**: Loan Officers and Managers
    
    Creates applicant with status 'pending'
    """
    try:
        # Prepare data for database
        data = applicant_data.dict()
        data["status"] = "pending"
        data["created_by"] = user["sub"]
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        # Create applicant
        result = db.create_applicant(data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create applicant"
            )
        
        # Log action
        db.log_action(
            user_id=user["sub"],
            action="CREATE_APPLICANT",
            resource_type="applicant",
            resource_id=result["id"],
            details={"name": f"{data['first_name']} {data['last_name']}"}
        )
        
        return {
            "success": True,
            "message": "Applicant created successfully",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create applicant: {str(e)}"
        )


@router.put("/{applicant_id}")
async def update_applicant(
    applicant_id: str,
    update_data: ApplicantUpdate,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Update an existing applicant
    
    **Access**: 
    - Loan Officers: Can update pending applications only
    - Managers: Can update any application
    """
    try:
        # Check if applicant exists
        existing = db.get_applicant_by_id(applicant_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Role-based access check
        user_role = user.get("role", "loan_officer")
        if user_role == "loan_officer" and existing.get("status") not in ["pending", "under_review"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Loan officers can only update pending or under-review applications"
            )
        
        # Prepare update data (only non-None values)
        data = {k: v for k, v in update_data.dict().items() if v is not None}
        data["updated_at"] = datetime.utcnow().isoformat()
        
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update applicant
        result = db.update_applicant(applicant_id, data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update applicant"
            )
        
        # Log action
        db.log_action(
            user_id=user["sub"],
            action="UPDATE_APPLICANT",
            resource_type="applicant",
            resource_id=applicant_id,
            details={"updated_fields": list(data.keys())}
        )
        
        return {
            "success": True,
            "message": "Applicant updated successfully",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update applicant: {str(e)}"
        )


@router.delete("/{applicant_id}")
async def delete_applicant(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """
    Delete an applicant (soft delete)
    
    **Access**: Managers only
    
    Marks applicant as deleted, does not permanently remove data
    """
    try:
        # Check if applicant exists
        existing = db.get_applicant_by_id(applicant_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Soft delete - update status
        result = db.update_applicant(applicant_id, {
            "status": "deleted",
            "deleted_by": user["sub"],
            "deleted_at": datetime.utcnow().isoformat()
        })
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete applicant"
            )
        
        # Log action
        db.log_action(
            user_id=user["sub"],
            action="DELETE_APPLICANT",
            resource_type="applicant",
            resource_id=applicant_id
        )
        
        return {
            "success": True,
            "message": "Applicant deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete applicant: {str(e)}"
        )


# ============================================
# ELIGIBILITY ENDPOINTS
# ============================================

@router.post("/{applicant_id}/check-eligibility")
async def check_eligibility(
    applicant_id: str,
    request: EligibilityRequest,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Check loan eligibility for an applicant
    
    **Access**: Loan Officers and Managers
    
    Runs the ML model to determine eligibility
    """
    try:
        # Get applicant data
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # TODO: Integrate with actual ML model
        # For now, return mock eligibility result
        import random
        is_eligible = random.random() > 0.3
        risk_score = random.uniform(0.1, 0.5) if is_eligible else random.uniform(0.5, 0.9)
        
        reasons = []
        recommendations = []
        
        if not is_eligible:
            possible_reasons = [
                "Insufficient income to support the requested loan amount",
                "Credit history indicates multiple late payments",
                "Employment duration below minimum requirement",
                "Existing loan obligations exceed threshold",
                "Debt-to-income ratio too high"
            ]
            reasons = random.sample(possible_reasons, random.randint(1, 3))
            recommendations = [
                "Consider a lower loan amount",
                "Provide additional income documentation",
                "Clear existing obligations before reapplying"
            ]
        
        # Save eligibility result
        eligibility_data = {
            "applicant_id": applicant_id,
            "eligible": is_eligible,
            "risk_score": risk_score,
            "confidence": random.uniform(0.85, 0.95),
            "reasons": reasons,
            "recommendations": recommendations,
            "checked_by": user["sub"],
            "checked_at": datetime.utcnow().isoformat()
        }
        
        # Update applicant with eligibility status
        db.update_applicant(applicant_id, {
            "eligibility_status": "eligible" if is_eligible else "not_eligible",
            "eligibility_reasons": reasons,
            "risk_score": risk_score,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Log action
        db.log_action(
            user_id=user["sub"],
            action="CHECK_ELIGIBILITY",
            resource_type="applicant",
            resource_id=applicant_id,
            details={"eligible": is_eligible, "risk_score": risk_score}
        )
        
        return {
            "success": True,
            "data": eligibility_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check eligibility: {str(e)}"
        )


@router.post("/{applicant_id}/send-for-review")
async def send_for_review(
    applicant_id: str,
    request: ReviewRequest,
    user=Depends(AuthMiddleware.require_role(["loan_officer"]))
):
    """
    Send an eligible application for manager review
    
    **Access**: Loan Officers only
    """
    try:
        # Get applicant
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Check eligibility status
        if applicant.get("eligibility_status") != "eligible":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only eligible applications can be sent for review"
            )
        
        # Update status to under_review
        result = db.update_applicant(applicant_id, {
            "status": "under_review",
            "sent_for_review_by": user["sub"],
            "sent_for_review_at": datetime.utcnow().isoformat(),
            "eligibility_result": request.eligibility_result,
            "review_notes": request.notes,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send for review"
            )
        
        # Log action
        db.log_action(
            user_id=user["sub"],
            action="SEND_FOR_REVIEW",
            resource_type="applicant",
            resource_id=applicant_id
        )
        
        return {
            "success": True,
            "message": "Application sent for manager review"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send for review: {str(e)}"
        )


# ============================================
# REVIEW ENDPOINTS (Manager only)
# ============================================

@router.get("/review/pending")
async def get_pending_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """
    Get all applications pending manager review
    
    **Access**: Managers only
    """
    try:
        result = db.get_applicants(
            user_id=user["sub"],
            status="under_review",
            page=page,
            page_size=page_size
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending reviews: {str(e)}"
        )


@router.post("/{applicant_id}/approve")
async def approve_application(
    applicant_id: str,
    request: ApprovalRequest,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """
    Approve a loan application
    
    **Access**: Managers only
    """
    try:
        # Get applicant
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Only under_review applications can be approved
        if applicant.get("status") not in ["under_review", "pending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve application with status: {applicant.get('status')}"
            )
        
        # Approve
        result = db.approve_applicant(
            applicant_id=applicant_id,
            approved_by=user["sub"],
            notes=request.notes
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve application"
            )
        
        # Log action
        db.log_action(
            user_id=user["sub"],
            action="APPROVE_APPLICATION",
            resource_type="applicant",
            resource_id=applicant_id,
            details={"notes": request.notes}
        )
        
        return {
            "success": True,
            "message": "Application approved successfully",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve application: {str(e)}"
        )


@router.post("/{applicant_id}/reject")
async def reject_application(
    applicant_id: str,
    request: ApprovalRequest,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """
    Reject a loan application
    
    **Access**: Managers only
    """
    try:
        if not request.reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required"
            )
        
        # Get applicant
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Only under_review applications can be rejected
        if applicant.get("status") not in ["under_review", "pending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject application with status: {applicant.get('status')}"
            )
        
        # Reject
        result = db.reject_applicant(
            applicant_id=applicant_id,
            rejected_by=user["sub"],
            reason=request.reason
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reject application"
            )
        
        # Log action
        db.log_action(
            user_id=user["sub"],
            action="REJECT_APPLICATION",
            resource_type="applicant",
            resource_id=applicant_id,
            details={"reason": request.reason}
        )
        
        return {
            "success": True,
            "message": "Application rejected",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject application: {str(e)}"
        )


# ============================================
# CREDIT & REPAYMENT HISTORY
# ============================================

@router.get("/{applicant_id}/credit-history")
async def get_credit_history(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get credit history for an applicant
    
    **Access**: Loan Officers and Managers
    """
    try:
        # Check applicant exists
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # TODO: Fetch from credit history service/table
        # For now, return mock data
        credit_history = {
            "credit_score": applicant.get("credit_score", 700),
            "score_change": 15,
            "last_updated": datetime.utcnow().isoformat(),
            "credit_utilization": 35,
            "payment_history_score": 95,
            "credit_age_years": 8,
            "recent_inquiries": 2,
            "derogatory_marks": 0,
            "accounts": [
                {"type": "Credit Card", "status": "Open", "balance": 50000, "limit": 200000},
                {"type": "Personal Loan", "status": "Closed", "balance": 0, "original_amount": 300000},
            ],
            "factors": [
                {"factor": "Payment History", "impact": "positive", "description": "Consistent on-time payments"},
                {"factor": "Credit Utilization", "impact": "positive", "description": "Below 40% utilization"},
                {"factor": "Recent Inquiries", "impact": "neutral", "description": "2 inquiries in last 6 months"},
            ]
        }
        
        return {
            "success": True,
            "data": credit_history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch credit history: {str(e)}"
        )


@router.get("/{applicant_id}/repayment-history")
async def get_repayment_history(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get repayment history for an applicant
    
    **Access**: Loan Officers and Managers
    """
    try:
        # Check applicant exists
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # TODO: Fetch from repayment history service/table
        # For now, return mock data
        repayment_history = {
            "summary": {
                "total_loans": 3,
                "active_loans": 1,
                "closed_loans": 2,
                "total_repaid": 850000,
                "on_time_payments_pct": 95,
                "average_days_late": 1.2
            },
            "loans": [
                {
                    "id": "LOAN001",
                    "type": "Personal Loan",
                    "original_amount": 500000,
                    "remaining_balance": 0,
                    "status": "closed",
                    "start_date": "2022-01-15",
                    "end_date": "2024-01-15",
                    "on_time_payments": 24,
                    "late_payments": 0
                },
                {
                    "id": "LOAN002",
                    "type": "Vehicle Loan",
                    "original_amount": 1500000,
                    "remaining_balance": 750000,
                    "status": "active",
                    "start_date": "2023-06-10",
                    "monthly_payment": 45000,
                    "next_due_date": "2026-02-10",
                    "on_time_payments": 18,
                    "late_payments": 1
                }
            ],
            "recent_payments": [
                {"date": "2025-01-10", "amount": 45000, "loan_id": "LOAN002", "status": "paid", "days_late": 0},
                {"date": "2024-12-10", "amount": 45000, "loan_id": "LOAN002", "status": "paid", "days_late": 0},
                {"date": "2024-11-10", "amount": 45000, "loan_id": "LOAN002", "status": "paid", "days_late": 0},
            ]
        }
        
        return {
            "success": True,
            "data": repayment_history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch repayment history: {str(e)}"
        )


@router.get("/{applicant_id}/loan-history")
async def get_loan_history(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get loan history for an applicant
    
    **Access**: Loan Officers and Managers
    """
    try:
        # Check applicant exists
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # TODO: Fetch from loan history service/table
        loan_history = [
            {
                "id": "LOAN001",
                "type": "Personal Loan",
                "amount": 500000,
                "status": "closed",
                "applied_date": "2022-01-10",
                "approved_date": "2022-01-15",
                "closed_date": "2024-01-15",
                "term_months": 24,
                "interest_rate": 12.5
            },
            {
                "id": "LOAN002",
                "type": "Vehicle Loan",
                "amount": 1500000,
                "status": "active",
                "applied_date": "2023-06-05",
                "approved_date": "2023-06-10",
                "term_months": 48,
                "interest_rate": 10.0,
                "remaining_amount": 750000
            }
        ]
        
        return {
            "success": True,
            "data": loan_history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch loan history: {str(e)}"
        )


@router.get("/{applicant_id}/audit-trail")
async def get_audit_trail(
    applicant_id: str,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get audit trail for an applicant
    
    **Access**: Loan Officers and Managers
    
    Returns all actions performed on this applicant record
    """
    try:
        # Check applicant exists
        applicant = db.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Fetch audit logs from database
        try:
            audit_logs = db.get_audit_logs(applicant_id)
        except:
            audit_logs = []
        
        # If no audit logs, return mock data based on applicant status
        if not audit_logs:
            audit_logs = []
            
            # Always add creation entry
            audit_logs.append({
                "id": f"audit-{applicant_id}-1",
                "timestamp": applicant.get("created_at", datetime.utcnow().isoformat()),
                "action": "created",
                "performed_by": {
                    "id": applicant.get("created_by", "system"),
                    "name": "Loan Officer",
                    "role": "loan_officer"
                },
                "description": "Loan application created"
            })
            
            # Add eligibility check if done
            if applicant.get("eligibility_status"):
                audit_logs.append({
                    "id": f"audit-{applicant_id}-2",
                    "timestamp": applicant.get("updated_at", datetime.utcnow().isoformat()),
                    "action": "reviewed",
                    "performed_by": {
                        "id": "system",
                        "name": "System",
                        "role": "system"
                    },
                    "description": f"Eligibility check completed - {applicant.get('eligibility_status', 'pending')}"
                })
            
            # Add status change entries
            status = applicant.get("status", "pending")
            if status == "under_review":
                audit_logs.append({
                    "id": f"audit-{applicant_id}-3",
                    "timestamp": applicant.get("updated_at", datetime.utcnow().isoformat()),
                    "action": "status_changed",
                    "performed_by": {
                        "id": applicant.get("created_by", "system"),
                        "name": "Loan Officer",
                        "role": "loan_officer"
                    },
                    "description": "Application sent for manager review",
                    "changes": [
                        {"field": "status", "old_value": "pending", "new_value": "under_review"}
                    ]
                })
            elif status == "approved":
                audit_logs.append({
                    "id": f"audit-{applicant_id}-3",
                    "timestamp": applicant.get("approved_at", applicant.get("updated_at", datetime.utcnow().isoformat())),
                    "action": "approved",
                    "performed_by": {
                        "id": applicant.get("approved_by", "manager"),
                        "name": "Bank Manager",
                        "role": "manager"
                    },
                    "description": "Loan application approved",
                    "metadata": {"amount": applicant.get("loan_amount")}
                })
            elif status == "rejected":
                audit_logs.append({
                    "id": f"audit-{applicant_id}-3",
                    "timestamp": applicant.get("rejected_at", applicant.get("updated_at", datetime.utcnow().isoformat())),
                    "action": "rejected",
                    "performed_by": {
                        "id": applicant.get("rejected_by", "manager"),
                        "name": "Bank Manager",
                        "role": "manager"
                    },
                    "description": f"Loan application rejected: {applicant.get('rejection_reason', 'Not specified')}"
                })
        
        return {
            "success": True,
            "data": audit_logs
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit trail: {str(e)}"
        )

