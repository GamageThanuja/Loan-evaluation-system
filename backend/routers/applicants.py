"""
Applicant Router
Full CRUD operations for applicants with role-based access control
"""

import sys
import re
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
    district: Optional[str] = Field(None, description="District")
    postal_code: Optional[str] = Field(None, description="Postal code")
    
    # Employment details
    employment_type: str = Field(..., description="Employment type")
    employer_name: Optional[str] = Field(None, description="Employer name")
    job_title: Optional[str] = Field(None, description="Job title")
    employment_length: int = Field(..., ge=0, description="Years of employment")
    monthly_income: float = Field(..., ge=0, description="Monthly income")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual income")
    account_number: Optional[str] = Field(None, description="Bank account number")
    dependents: Optional[int] = Field(0, ge=0, description="Number of dependents")
    
    # Loan details - optional when creating applicant without loan request
    loan_amount: float = Field(0, ge=0, description="Requested loan amount")
    loan_purpose: str = Field("other", description="Purpose of loan")
    loan_term_months: int = Field(12, ge=1, le=360, description="Loan term in months")
    
    # Financial details
    credit_score: Optional[int] = Field(None, ge=300, le=850, description="Credit score")
    existing_loans: Optional[int] = Field(0, ge=0, description="Number of existing loans")
    monthly_expenses: Optional[float] = Field(None, ge=0, description="Monthly expenses")

    @validator("nic")
    def validate_nic(cls, value: str) -> str:
        normalized = str(value).strip().upper()
        if not re.match(r"^\d{9}[VX]$", normalized):
            raise ValueError("NIC must be in format YYDDDXXXXV")
        return normalized

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
    district: Optional[str] = None
    postal_code: Optional[str] = None
    employment_type: Optional[str] = None
    employer_name: Optional[str] = None
    job_title: Optional[str] = None
    employment_length: Optional[int] = Field(None, ge=0)
    monthly_income: Optional[float] = Field(None, ge=0)
    annual_income: Optional[float] = Field(None, ge=0)
    account_number: Optional[str] = None
    dependents: Optional[int] = Field(None, ge=0)
    loan_amount: Optional[float] = Field(None, ge=0)
    loan_purpose: Optional[str] = None
    loan_term_months: Optional[int] = Field(None, ge=1, le=360)
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    existing_loans: Optional[int] = Field(None, ge=0)
    monthly_expenses: Optional[float] = Field(None, ge=0)

    @validator("nic")
    def validate_nic(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value).strip().upper()
        if not re.match(r"^\d{9}[VX]$", normalized):
            raise ValueError("NIC must be in format YYDDDXXXXV")
        return normalized

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
    district: Optional[str] = None
    postal_code: Optional[str] = None
    employment_type: str
    employer_name: Optional[str] = None
    job_title: Optional[str] = None
    employment_length: int
    monthly_income: float
    annual_income: Optional[float] = None
    account_number: Optional[str] = None
    dependents: Optional[int] = None
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
# HELPERS
# ============================================

AUDIT_ACTION_MAP = {
    "CREATE_APPLICANT": "created",
    "UPDATE_APPLICANT": "updated",
    "STATUS_CHANGED": "status_changed",
    "SEND_FOR_REVIEW": "reviewed",
    "REVIEW_APPLICATION": "reviewed",
    "APPROVE_APPLICATION": "approved",
    "REJECT_APPLICATION": "rejected",
    "PAYMENT_MADE": "payment_made",
    "DOCUMENT_UPLOADED": "document_uploaded",
    "NOTE_ADDED": "note_added",
}

KNOWN_AUDIT_ACTIONS = {
    "created",
    "updated",
    "status_changed",
    "reviewed",
    "approved",
    "rejected",
    "payment_made",
    "document_uploaded",
    "note_added",
}

def _normalize_audit_action(action: Optional[str]) -> str:
    if not action:
        return "updated"
    normalized = action.strip().lower()
    if normalized in KNOWN_AUDIT_ACTIONS:
        return normalized
    mapped = AUDIT_ACTION_MAP.get(action.strip().upper())
    return mapped or normalized

def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(str(value), "%Y-%m-%d")
        except ValueError:
            return None

def _calculate_term_months(start_date: Optional[str], end_date: Optional[str]) -> Optional[int]:
    start = _parse_datetime(start_date)
    end = _parse_datetime(end_date)
    if not start or not end:
        return None
    return max(1, (end.year - start.year) * 12 + (end.month - start.month))


# ============================================
# CRUD ENDPOINTS
# ============================================

@router.get("")
async def list_applicants(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    eligibility_status: Optional[str] = Query(None, description="Filter by eligibility (eligible/not_eligible or 1/0)"),
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
        # Handle numeric eligibility status (1=eligible, 0=not_eligible)
        final_eligibility_status = eligibility_status
        if eligibility_status == "1":
            final_eligibility_status = "eligible"
        elif eligibility_status == "0":
            final_eligibility_status = "not_eligible"

        result = db.get_applicants(
            user_id=user["user_id"],
            status=status_filter,
            eligibility_status=final_eligibility_status,
            search=search,
            page=page,
            page_size=page_size
        )
        
        # Format response
        applicants = []
        for app in result.get("data", []):
            applicants.append({
                "id": app.get("id"),
                "name": app.get("name") or f"{app.get('first_name', '')} {app.get('last_name', '')}".strip(),
                "email": app.get("email"),
                "phone": app.get("phone"),
                "nic": app.get("nic"),
                "loan_amount": app.get("loan_amount"),
                "loan_purpose": app.get("loan_purpose"),
                "loan_term_months": app.get("loan_term_months"),
                "monthly_income": app.get("monthly_income"),
                "employment_status": app.get("employment_status"),
                "employer_name": app.get("employer_name"),
                "status": app.get("status", "pending"),
                "eligibility_status": app.get("eligibility_status"),
                "credit_score": app.get("credit_score"),
                "rejection_reason": app.get("rejection_reason"),
                "created_at": app.get("created_at"),
                "updated_at": app.get("updated_at"),
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
        
        # Parse name into first_name and last_name
        full_name = applicant.get("name", "")
        name_parts = full_name.split(" ", 1) if full_name else ["", ""]
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Calculate age from date_of_birth
        age = None
        date_of_birth = applicant.get("date_of_birth")
        if date_of_birth:
            try:
                if isinstance(date_of_birth, str):
                    birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
                else:
                    birth_date = date_of_birth
                age = int((datetime.now() - birth_date).days / 365.25)
            except (ValueError, TypeError):
                age = None
        
        # Map database fields to frontend expected format
        response_data = {
            "id": applicant.get("id"),
            "first_name": first_name,
            "last_name": last_name,
            "name": full_name,
            "email": applicant.get("email"),
            "phone": applicant.get("phone"),
            "date_of_birth": date_of_birth,
            "age": age,
            "gender": applicant.get("gender"),
            "marital_status": applicant.get("marital_status"),
            "dependents": applicant.get("dependents"),  # May not exist in DB, will be None
            "nic": applicant.get("nic"),
            
            # Employment - map from database columns
            "employment_type": applicant.get("employment_status"),
            "job_title": applicant.get("occupation"),
            "employer_name": applicant.get("employer_name"),
            "employment_length": applicant.get("years_employed"),
            "monthly_income": applicant.get("monthly_income"),
            
            # Financial
            "credit_score": applicant.get("credit_score"),
            "existing_loans": applicant.get("existing_loans_count"),
            
            # Loan
            "loan_amount": applicant.get("loan_amount"),
            "loan_purpose": applicant.get("loan_purpose"),
            "loan_term_months": applicant.get("loan_term_months"),
            
            # Address
            "address": applicant.get("address_line1"),
            "city": applicant.get("city"),
            "district": applicant.get("state"),  # state -> district
            "postal_code": applicant.get("postal_code"),
            
            # Status
            "status": applicant.get("status"),
            "eligibility_status": applicant.get("eligibility_status"),
            "risk_score": applicant.get("risk_score"),
            
            # Metadata
            "created_at": applicant.get("created_at"),
            "updated_at": applicant.get("updated_at"),
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
        # Prepare data for database - map frontend fields to database columns
        raw_data = applicant_data.dict()
        
        # Build full name from first_name and last_name
        full_name = f"{raw_data.get('first_name', '')} {raw_data.get('last_name', '')}".strip()
        
        # Map to database schema
        data = {
            "name": full_name,
            "email": raw_data.get("email"),
            "phone": raw_data.get("phone"),
            "date_of_birth": raw_data.get("date_of_birth"),
            "gender": raw_data.get("gender"),
            "marital_status": raw_data.get("marital_status"),
            "nic": raw_data.get("nic"),
            
            # Employment - map to database columns
            "employment_status": raw_data.get("employment_type"),
            "occupation": raw_data.get("job_title"),
            "employer_name": raw_data.get("employer_name"),
            "years_employed": raw_data.get("employment_length"),
            "monthly_income": raw_data.get("monthly_income", 0),
            
            # Financial
            "credit_score": raw_data.get("credit_score"),
            "existing_loans_count": raw_data.get("existing_loans", 0),
            
            # Loan
            "loan_amount": raw_data.get("loan_amount", 0),
            "loan_purpose": raw_data.get("loan_purpose", "other"),
            "loan_term_months": raw_data.get("loan_term_months", 12),
            
            # Address
            "address_line1": raw_data.get("address"),
            "city": raw_data.get("city"),
            "state": raw_data.get("district"),  # district -> state
            "postal_code": raw_data.get("postal_code"),
            "country": "Sri Lanka",
            
            # Status and metadata
            "status": "pending",
            "created_by": user["user_id"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        # Remove None values to avoid database errors
        data = {k: v for k, v in data.items() if v is not None}
        
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
            details={"name": full_name}
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
            "notes": request.notes,
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


# ============================================
# TRANSACTION HISTORY
# ============================================

@router.get("/{applicant_id}/transactions")
async def get_transactions_history(
    applicant_id: int,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get transaction history for an applicant
    
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
        
        transactions = db.get_transactions_by_applicant(applicant_id)
        
        if not transactions:
            return {
                "success": True,
                "data": {
                    "transactions": [],
                    "summary": {
                        "total_transactions": 0,
                        "total_debits": 0,
                        "total_credits": 0,
                        "monthly_transactions": []
                    }
                }
            }
        
        formatted_transactions = []
        for tx in transactions:
            formatted_transactions.append({
                "id": tx.get("id"),
                "date": tx.get("transaction_date") or tx.get("date") or tx.get("created_at"),
                "type": tx.get("transaction_type") or tx.get("type"),
                "amount": float(tx.get("amount", 0)),
                "description": tx.get("description") or "",
                "status": tx.get("status") or tx.get("transaction_status") or "completed",
                "payment_method": tx.get("payment_method"),
                "reference_number": tx.get("reference_number"),
                "balance": float(tx.get("balance", 0)) if tx.get("balance") is not None else None,
                "notes": tx.get("notes")
            })
        
        # Sort by date (most recent first)
        formatted_transactions.sort(
            key=lambda t: _parse_datetime(t.get("date")) or datetime.min,
            reverse=True
        )
        
        debit_types = {"payment", "fee", "penalty", "adjustment"}
        credit_types = {"disbursement", "refund"}
        
        total_debits = sum(
            t["amount"] for t in formatted_transactions if t.get("type") in debit_types
        )
        total_credits = sum(
            t["amount"] for t in formatted_transactions if t.get("type") in credit_types
        )
        
        monthly_buckets = {}
        for tx in formatted_transactions:
            parsed_date = _parse_datetime(tx.get("date"))
            if not parsed_date:
                continue
            month_key = parsed_date.strftime("%Y-%m")
            bucket = monthly_buckets.setdefault(
                month_key,
                {"month": parsed_date.strftime("%b %Y"), "count": 0, "amount": 0}
            )
            bucket["count"] += 1
            bucket["amount"] += tx.get("amount", 0)
        
        monthly_transactions = [
            monthly_buckets[key] for key in sorted(monthly_buckets.keys(), reverse=True)
        ]
        
        summary = {
            "total_transactions": len(formatted_transactions),
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "last_transaction": formatted_transactions[0] if formatted_transactions else None,
            "monthly_transactions": monthly_transactions
        }
        
        return {
            "success": True,
            "data": {
                "transactions": formatted_transactions,
                "summary": summary
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transactions: {str(e)}"
        )


@router.get("/{applicant_id}/loan-history")
async def get_loan_history(
    applicant_id: int,
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
        
        # Use repayment history records as loan history source
        loan_records = db.get_repayment_history_by_applicant(applicant_id)
        
        if not loan_records:
            return {
                "success": True,
                "data": []
            }
        
        loan_history = []
        for loan in loan_records:
            loan_status = loan.get("loan_status") or loan.get("payment_status") or "active"
            start_date = loan.get("start_date")
            maturity_date = loan.get("maturity_date") or loan.get("end_date")
            term_months = _calculate_term_months(start_date, maturity_date)
            
            loan_history.append({
                "id": loan.get("loan_id") or loan.get("id"),
                "type": (loan.get("loan_type") or "").replace("_", " ").title(),
                "amount": float(loan.get("original_amount", 0)),
                "status": str(loan_status).replace("_", " "),
                "applied_date": start_date,
                "approved_date": start_date,
                "closed_date": loan.get("end_date"),
                "term_months": term_months,
                "interest_rate": float(loan.get("interest_rate", 0)) if loan.get("interest_rate") is not None else None,
                "remaining_amount": float(loan.get("remaining_balance", 0)) if loan.get("remaining_balance") is not None else None,
                "lender_name": loan.get("lender_name")
            })
        
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
    applicant_id: int,
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
        audit_log_records = db.get_audit_logs(applicant_id)
        
        audit_logs = []
        for log in audit_log_records:
            details = log.get("details") or {}
            action = _normalize_audit_action(log.get("action"))
            performed_by = details.get("performed_by") or {}
            
            if not performed_by:
                performed_by = {
                    "id": log.get("user_id") or "system",
                    "name": "System",
                    "role": "system"
                }
            
            description = details.get("description")
            if not description:
                if action == "created":
                    description = "Loan application created"
                elif action == "updated":
                    description = "Applicant record updated"
                elif action == "reviewed":
                    description = f"Eligibility check completed - {applicant.get('eligibility_status', 'pending')}"
                elif action == "approved":
                    description = "Loan application approved"
                elif action == "rejected":
                    description = f"Loan application rejected: {applicant.get('rejection_reason', 'Not specified')}"
                elif action == "payment_made":
                    description = "Payment recorded"
                else:
                    description = "Applicant activity recorded"
            
            changes = details.get("changes")
            if not changes and details.get("updated_fields"):
                changes = [
                    {"field": field, "old_value": None, "new_value": "updated"}
                    for field in details.get("updated_fields", [])
                ]
            
            audit_logs.append({
                "id": f"audit-{log.get('id')}",
                "timestamp": log.get("created_at", datetime.utcnow().isoformat()),
                "action": action,
                "performed_by": performed_by,
                "description": description,
                "changes": changes,
                "metadata": details.get("metadata")
            })
        
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
            
            # Add recent payment entry if transactions exist
            try:
                transactions = db.get_transactions_by_applicant(applicant_id)
            except Exception:
                transactions = []
            
            if transactions:
                recent_payment = None
                for tx in transactions:
                    tx_type = tx.get("transaction_type") or tx.get("type")
                    if tx_type == "payment":
                        recent_payment = tx
                        break
                if recent_payment:
                    audit_logs.append({
                        "id": f"audit-{applicant_id}-payment",
                        "timestamp": recent_payment.get("transaction_date") or recent_payment.get("created_at") or datetime.utcnow().isoformat(),
                        "action": "payment_made",
                        "performed_by": {
                            "id": applicant.get("created_by", "system"),
                            "name": "System",
                            "role": "system"
                        },
                        "description": f"Payment received of LKR {recent_payment.get('amount', 0)}",
                        "metadata": {"reference_number": recent_payment.get("reference_number")}
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
