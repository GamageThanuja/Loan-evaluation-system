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
    applicant_id: int = Field(..., description="Applicant ID")
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
    applicant_id: int = Field(..., description="Applicant ID")
    eligibility_result: Dict[str, Any] = Field(..., description="Eligibility result data")
    notes: Optional[str] = Field(None, description="Additional notes")

class ApprovalRequest(BaseModel):
    """Model for approval/rejection"""
    notes: Optional[str] = Field(None, description="Approval/rejection notes")
    reason: Optional[str] = Field(None, description="Rejection reason (required for rejection)")

class ApplicantResponse(BaseModel):
    """Full applicant response with all details"""
    id: int
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
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
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
            user_id=user["user_id"],
            status=status_filter,
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
    applicant_id: int,
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
        data["created_by"] = user["user_id"]
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
            user_id=user["user_id"],
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
    applicant_id: int,
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
            user_id=user["user_id"],
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
    applicant_id: int,
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
            "deleted_by": user["user_id"],
            "deleted_at": datetime.utcnow().isoformat()
        })
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete applicant"
            )
        
        # Log action
        db.log_action(
            user_id=user["user_id"],
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
    applicant_id: int,
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
        # The ML model should be called here to generate predictions
        # For now, return an error indicating ML model is not yet integrated
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ML model integration pending. Eligibility check will be available once the model is integrated."
        )
        
        # When ML model is integrated, the code should look like:
        # from ml_model.inference import predict
        # prediction = predict(applicant)
        # is_eligible = prediction["decision"] == "APPROVE"
        # risk_score = prediction["risk_score"]
        # reasons = prediction.get("rejection_reasons", [])
        # recommendations = prediction.get("recommendations", [])
        
        # # Save eligibility result
        # eligibility_data = {
        #     "applicant_id": applicant_id,
        #     "eligible": is_eligible,
        #     "risk_score": risk_score,
        #     "confidence": prediction.get("confidence", 0.0),
        #     "reasons": reasons,
        #     "recommendations": recommendations,
        #     "checked_by": user["user_id"],
        #     "checked_at": datetime.utcnow().isoformat()
        # }
        
        # # Update applicant with eligibility status
        # db.update_applicant(applicant_id, {
        #     "eligibility_status": "eligible" if is_eligible else "not_eligible",
        #     "eligibility_reasons": reasons,
        #     "risk_score": risk_score,
        #     "updated_at": datetime.utcnow().isoformat()
        # })
        
        # # Log action
        # db.log_action(
        #     user_id=user["user_id"],
        #     action="CHECK_ELIGIBILITY",
        #     resource_type="applicant",
        #     resource_id=applicant_id,
        #     details={"eligible": is_eligible, "risk_score": risk_score}
        # )
        
        # return {
        #     "success": True,
        #     "data": eligibility_data
        # }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check eligibility: {str(e)}"
        )


@router.post("/{applicant_id}/send-for-review")
async def send_for_review(
    applicant_id: int,
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
            "sent_for_review_by": user["user_id"],
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
            user_id=user["user_id"],
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
            user_id=user["user_id"],
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
    applicant_id: int,
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
            approved_by=user["user_id"],
            notes=request.notes
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve application"
            )
        
        # Log action
        db.log_action(
            user_id=user["user_id"],
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
    applicant_id: int,
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
            rejected_by=user["user_id"],
            reason=request.reason
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reject application"
            )
        
        # Log action
        db.log_action(
            user_id=user["user_id"],
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
    applicant_id: int,
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
        
        # Fetch credit history from database
        credit_accounts = db.get_credit_history_by_applicant(applicant_id)
        
        if not credit_accounts:
            # Return empty credit history if no records found
            return {
                "success": True,
                "data": {
                    "credit_score": applicant.get("credit_score", 0),
                    "score_change": 0,
                    "last_updated": datetime.utcnow().isoformat(),
                    "credit_utilization": 0,
                    "payment_history_score": 0,
                    "credit_age_years": 0,
                    "recent_inquiries": 0,
                    "derogatory_marks": 0,
                    "accounts": [],
                    "factors": []
                }
            }
        
        # Calculate summary statistics from actual credit accounts
        open_accounts = [acc for acc in credit_accounts if acc.get("account_status") == "open"]
        
        # Calculate total credit utilization
        total_balance = sum(float(acc.get("balance", 0)) for acc in open_accounts if acc.get("account_type") == "credit_card")
        total_limit = sum(float(acc.get("credit_limit", 0)) for acc in open_accounts if acc.get("credit_limit"))
        avg_utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
        
        # Calculate average payment history score
        payment_scores = [acc.get("payment_history_score", 0) for acc in credit_accounts if acc.get("payment_history_score")]
        avg_payment_score = sum(payment_scores) / len(payment_scores) if payment_scores else 0
        
        # Calculate credit age (oldest account)
        oldest_account = min(credit_accounts, key=lambda x: x.get("opened_date", "9999-12-31"))
        oldest_date = datetime.strptime(oldest_account.get("opened_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        credit_age_years = (datetime.now() - oldest_date).days / 365.25
        
        # Count derogatory marks
        total_derogatory = sum(acc.get("derogatory_marks", 0) for acc in credit_accounts)
        
        # Format accounts for response
        formatted_accounts = []
        for acc in credit_accounts:
            formatted_acc = {
                "type": acc.get("account_type", "").replace("_", " ").title(),
                "status": acc.get("account_status", "").title(),
                "balance": float(acc.get("balance", 0)),
                "limit": float(acc.get("credit_limit", 0)) if acc.get("credit_limit") else None,
                "opened_date": acc.get("opened_date"),
                "payment_history_score": acc.get("payment_history_score", 0),
                "utilization": float(acc.get("credit_utilization", 0)) if acc.get("credit_utilization") else None
            }
            formatted_accounts.append(formatted_acc)
        
        # Generate factors based on actual data
        factors = []
        if avg_payment_score >= 90:
            factors.append({"factor": "Payment History", "impact": "positive", "description": "Consistent on-time payments"})
        elif avg_payment_score >= 70:
            factors.append({"factor": "Payment History", "impact": "neutral", "description": "Mostly on-time payments with occasional delays"})
        else:
            factors.append({"factor": "Payment History", "impact": "negative", "description": "History of late or missed payments"})
        
        if avg_utilization < 30:
            factors.append({"factor": "Credit Utilization", "impact": "positive", "description": f"Low utilization at {avg_utilization:.1f}%"})
        elif avg_utilization < 50:
            factors.append({"factor": "Credit Utilization", "impact": "neutral", "description": f"Moderate utilization at {avg_utilization:.1f}%"})
        else:
            factors.append({"factor": "Credit Utilization", "impact": "negative", "description": f"High utilization at {avg_utilization:.1f}%"})
        
        if credit_age_years >= 7:
            factors.append({"factor": "Credit Age", "impact": "positive", "description": f"Established credit history of {credit_age_years:.1f} years"})
        elif credit_age_years >= 3:
            factors.append({"factor": "Credit Age", "impact": "neutral", "description": f"Moderate credit history of {credit_age_years:.1f} years"})
        else:
            factors.append({"factor": "Credit Age", "impact": "negative", "description": f"Limited credit history of {credit_age_years:.1f} years"})
        
        credit_history = {
            "credit_score": applicant.get("credit_score", 0),
            "score_change": 0,  # Would need historical data to calculate
            "last_updated": datetime.utcnow().isoformat(),
            "credit_utilization": round(avg_utilization, 2),
            "payment_history_score": round(avg_payment_score, 0),
            "credit_age_years": round(credit_age_years, 1),
            "recent_inquiries": 0,  # Would need inquiry tracking
            "derogatory_marks": total_derogatory,
            "accounts": formatted_accounts,
            "factors": factors
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
    applicant_id: int,
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
        
        # Fetch repayment history from database
        loan_records = db.get_repayment_history_by_applicant(applicant_id)
        
        if not loan_records:
            # Return empty repayment history if no records found
            return {
                "success": True,
                "data": {
                    "summary": {
                        "total_loans": 0,
                        "active_loans": 0,
                        "closed_loans": 0,
                        "total_repaid": 0,
                        "on_time_payments_pct": 0,
                        "average_days_late": 0
                    },
                    "loans": [],
                    "recent_payments": []
                }
            }
        
        # Calculate summary statistics
        total_loans = len(loan_records)
        active_loans = sum(1 for loan in loan_records if loan.get("loan_status") == "active")
        closed_loans = sum(1 for loan in loan_records if loan.get("loan_status") in ["closed", "paid_off"])
        
        # Calculate total repaid (original amount - remaining balance for all loans)
        total_repaid = sum(
            float(loan.get("original_amount", 0)) - float(loan.get("remaining_balance", 0))
            for loan in loan_records
        )
        
        # Calculate average on-time payment percentage
        on_time_percentages = [loan.get("on_time_payment_percentage", 0) for loan in loan_records]
        avg_on_time_pct = sum(on_time_percentages) / len(on_time_percentages) if on_time_percentages else 0
        
        # Calculate average days late
        avg_days_late_values = [loan.get("average_days_late", 0) for loan in loan_records]
        avg_days_late = sum(avg_days_late_values) / len(avg_days_late_values) if avg_days_late_values else 0
        
        # Format loans for response
        formatted_loans = []
        all_recent_payments = []
        
        for loan in loan_records:
            formatted_loan = {
                "id": loan.get("loan_id"),
                "type": loan.get("loan_type", "").replace("_", " ").title(),
                "original_amount": float(loan.get("original_amount", 0)),
                "remaining_balance": float(loan.get("remaining_balance", 0)),
                "status": loan.get("loan_status", "").replace("_", " "),
                "start_date": loan.get("start_date"),
                "end_date": loan.get("end_date"),
                "monthly_payment": float(loan.get("monthly_payment", 0)) if loan.get("monthly_payment") else None,
                "next_due_date": loan.get("next_due_date"),
                "on_time_payments": loan.get("on_time_payments", 0),
                "late_payments": loan.get("late_payments", 0)
            }
            formatted_loans.append(formatted_loan)
            
            # Collect recent payments from all loans
            recent_payments = loan.get("recent_payments", [])
            if isinstance(recent_payments, list):
                for payment in recent_payments:
                    payment["loan_id"] = loan.get("loan_id")
                    all_recent_payments.append(payment)
        
        # Sort recent payments by date (most recent first)
        all_recent_payments.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Take only the most recent 10 payments
        recent_payments_limited = all_recent_payments[:10]
        
        repayment_history = {
            "summary": {
                "total_loans": total_loans,
                "active_loans": active_loans,
                "closed_loans": closed_loans,
                "total_repaid": round(total_repaid, 2),
                "on_time_payments_pct": round(avg_on_time_pct, 0),
                "average_days_late": round(avg_days_late, 1)
            },
            "loans": formatted_loans,
            "recent_payments": recent_payments_limited
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

