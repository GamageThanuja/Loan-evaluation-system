"""
Status Management Router
Full CRUD operations for eligibility statuses, application statuses, and status colors
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Add parent directories to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field

# Import database client
from database.client import db
from middleware.auth import AuthMiddleware

router = APIRouter(prefix="/api/status-management", tags=["Status Management"])

# ============================================
# MODELS
# ============================================

class EligibilityStatusBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Unique code (e.g., 'eligible')")
    name: str = Field(..., min_length=1, max_length=100, description="Display name (e.g., 'Eligible')")
    description: Optional[str] = Field(None, description="Description of the status")
    is_active: bool = Field(True, description="Whether this status is active")
    display_order: int = Field(0, description="Display order for sorting")

class EligibilityStatusCreate(EligibilityStatusBase):
    pass

class EligibilityStatusUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

class EligibilityStatusResponse(EligibilityStatusBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class ApplicationStatusBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Unique code (e.g., 'pending')")
    name: str = Field(..., min_length=1, max_length=100, description="Display name (e.g., 'Pending')")
    description: Optional[str] = Field(None, description="Description of the status")
    color_code: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="HEX color code (e.g., '#4caf50')")
    color_name: Optional[str] = Field(None, max_length=50, description="Color name (e.g., 'success', 'error', 'warning', 'info')")
    is_active: bool = Field(True, description="Whether this status is active")
    display_order: int = Field(0, description="Display order for sorting")

class ApplicationStatusCreate(ApplicationStatusBase):
    pass

class ApplicationStatusUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color_code: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    color_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

class ApplicationStatusResponse(ApplicationStatusBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class StatusColorBase(BaseModel):
    status_id: int = Field(..., description="ID of the application status")
    color_code: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="HEX color code (e.g., '#4caf50')")
    color_name: Optional[str] = Field(None, max_length=50, description="Color name (e.g., 'success')")
    is_primary: bool = Field(True, description="Whether this is the primary color for the status")

class StatusColorCreate(StatusColorBase):
    pass

class StatusColorUpdate(BaseModel):
    color_code: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    color_name: Optional[str] = Field(None, max_length=50)
    is_primary: Optional[bool] = None

class StatusColorResponse(StatusColorBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class ApplicationStatusWithColor(ApplicationStatusResponse):
    # color_code and color_name are now part of ApplicationStatusResponse
    pass

# ============================================
# ELIGIBILITY STATUS ENDPOINTS
# ============================================

@router.get("/eligibility-statuses", response_model=List[EligibilityStatusResponse])
async def list_eligibility_statuses(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Get all eligibility statuses"""
    try:
        query = db.client.table("eligibility_statuses").select("*")
        
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        query = query.order("display_order").order("name")
        
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch eligibility statuses: {str(e)}"
        )

@router.get("/eligibility-statuses/{status_id}", response_model=EligibilityStatusResponse)
async def get_eligibility_status(
    status_id: int,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Get a specific eligibility status by ID"""
    try:
        response = db.client.table("eligibility_statuses").select("*").eq("id", status_id).single().execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Eligibility status not found"
            )
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch eligibility status: {str(e)}"
        )

@router.post("/eligibility-statuses", response_model=EligibilityStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_eligibility_status(
    status_data: EligibilityStatusCreate,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Create a new eligibility status (Manager only)"""
    try:
        # Check if code already exists
        existing = db.client.table("eligibility_statuses").select("id").eq("code", status_data.code).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Eligibility status with code '{status_data.code}' already exists"
            )
        
        result = db.client.table("eligibility_statuses").insert({
            "code": status_data.code,
            "name": status_data.name,
            "description": status_data.description,
            "is_active": status_data.is_active,
            "display_order": status_data.display_order
        }).execute()
        
        return {
            "success": True,
            "data": result.data[0] if result.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create eligibility status: {str(e)}"
        )

@router.put("/eligibility-statuses/{status_id}", response_model=EligibilityStatusResponse)
async def update_eligibility_status(
    status_id: int,
    status_data: EligibilityStatusUpdate,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Update an eligibility status (Manager only)"""
    try:
        # Check if status exists
        existing = db.client.table("eligibility_statuses").select("id").eq("id", status_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Eligibility status not found"
            )
        
        # Build update data
        update_data = {}
        if status_data.code is not None:
            # Check if new code conflicts
            conflict = db.client.table("eligibility_statuses").select("id").eq("code", status_data.code).neq("id", status_id).execute()
            if conflict.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Eligibility status with code '{status_data.code}' already exists"
                )
            update_data["code"] = status_data.code
        
        if status_data.name is not None:
            update_data["name"] = status_data.name
        if status_data.description is not None:
            update_data["description"] = status_data.description
        if status_data.color_code is not None:
            update_data["color_code"] = status_data.color_code
        if status_data.color_name is not None:
            update_data["color_name"] = status_data.color_name
        if status_data.is_active is not None:
            update_data["is_active"] = status_data.is_active
        if status_data.display_order is not None:
            update_data["display_order"] = status_data.display_order
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = db.client.table("eligibility_statuses").update(update_data).eq("id", status_id).execute()
        return {
            "success": True,
            "data": result.data[0] if result.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update eligibility status: {str(e)}"
        )

@router.delete("/eligibility-statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_eligibility_status(
    status_id: int,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Delete an eligibility status (Manager only)"""
    try:
        # Check if status is in use
        in_use = db.client.table("applicants").select("id", count="exact").eq("eligibility_status_id", status_id).execute()
        if in_use.count and in_use.count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete eligibility status that is in use by applicants"
            )
        
        result = db.client.table("eligibility_statuses").delete().eq("id", status_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Eligibility status not found"
            )
        
        return {"success": True, "message": "Eligibility status deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete eligibility status: {str(e)}"
        )

# ============================================
# APPLICATION STATUS ENDPOINTS
# ============================================

@router.get("/application-statuses", response_model=List[ApplicationStatusResponse])
async def list_application_statuses(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Get all application statuses"""
    try:
        query = db.client.table("application_statuses").select("*")
        
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        query = query.order("display_order").order("name")
        
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch application statuses: {str(e)}"
        )

@router.get("/application-statuses/{status_id}", response_model=ApplicationStatusResponse)
async def get_application_status(
    status_id: int,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Get a specific application status by ID"""
    try:
        response = db.client.table("application_statuses").select("*").eq("id", status_id).single().execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application status not found"
            )
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch application status: {str(e)}"
        )

@router.get("/application-statuses-with-colors", response_model=List[ApplicationStatusWithColor])
async def list_application_statuses_with_colors(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Get all application statuses with their color mappings"""
    try:
        query = db.client.table("application_statuses").select("*")
        
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        query = query.order("display_order").order("name")
        
        response = query.execute()
        # Color codes are now directly in application_statuses table
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch application statuses: {str(e)}"
        )

@router.post("/application-statuses", response_model=ApplicationStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_application_status(
    status_data: ApplicationStatusCreate,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Create a new application status (Manager only)"""
    try:
        # Check if code already exists
        existing = db.client.table("application_statuses").select("id").eq("code", status_data.code).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Application status with code '{status_data.code}' already exists"
            )
        
        result = db.client.table("application_statuses").insert({
            "code": status_data.code,
            "name": status_data.name,
            "description": status_data.description,
            "color_code": status_data.color_code,
            "color_name": status_data.color_name,
            "is_active": status_data.is_active,
            "display_order": status_data.display_order
        }).execute()
        
        return {
            "success": True,
            "data": result.data[0] if result.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application status: {str(e)}"
        )

@router.put("/application-statuses/{status_id}", response_model=ApplicationStatusResponse)
async def update_application_status(
    status_id: int,
    status_data: ApplicationStatusUpdate,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Update an application status (Manager only)"""
    try:
        # Check if status exists
        existing = db.client.table("application_statuses").select("id").eq("id", status_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application status not found"
            )
        
        # Build update data
        update_data = {}
        if status_data.code is not None:
            # Check if new code conflicts
            conflict = db.client.table("application_statuses").select("id").eq("code", status_data.code).neq("id", status_id).execute()
            if conflict.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Application status with code '{status_data.code}' already exists"
                )
            update_data["code"] = status_data.code
        
        if status_data.name is not None:
            update_data["name"] = status_data.name
        if status_data.description is not None:
            update_data["description"] = status_data.description
        if status_data.color_code is not None:
            update_data["color_code"] = status_data.color_code
        if status_data.color_name is not None:
            update_data["color_name"] = status_data.color_name
        if status_data.is_active is not None:
            update_data["is_active"] = status_data.is_active
        if status_data.display_order is not None:
            update_data["display_order"] = status_data.display_order
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = db.client.table("application_statuses").update(update_data).eq("id", status_id).execute()
        return {
            "success": True,
            "data": result.data[0] if result.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application status: {str(e)}"
        )

@router.delete("/application-statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application_status(
    status_id: int,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Delete an application status (Manager only)"""
    try:
        # Check if status is in use
        in_use = db.client.table("applicants").select("id", count="exact").eq("application_status_id", status_id).execute()
        if in_use.count and in_use.count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete application status that is in use by applicants"
            )
        
        result = db.client.table("application_statuses").delete().eq("id", status_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application status not found"
            )
        
        return {"success": True, "message": "Application status deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete application status: {str(e)}"
        )

# ============================================
# STATUS COLOR ENDPOINTS
# ============================================

@router.get("/status-colors", response_model=List[StatusColorResponse])
async def list_status_colors(
    status_id: Optional[int] = Query(None, description="Filter by status ID"),
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Get all status colors"""
    try:
        query = db.client.table("status_colors").select("*")
        
        if status_id is not None:
            query = query.eq("status_id", status_id)
        
        query = query.order("status_id").order("is_primary", desc=True)
        
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch status colors: {str(e)}"
        )

@router.get("/status-colors/{color_id}", response_model=StatusColorResponse)
async def get_status_color(
    color_id: int,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Get a specific status color by ID"""
    try:
        response = db.client.table("status_colors").select("*").eq("id", color_id).single().execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Status color not found"
            )
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch status color: {str(e)}"
        )

@router.post("/status-colors", response_model=StatusColorResponse, status_code=status.HTTP_201_CREATED)
async def create_status_color(
    color_data: StatusColorCreate,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Create a new status color (Manager only)"""
    try:
        # Check if status exists
        status_exists = db.client.table("application_statuses").select("id").eq("id", color_data.status_id).execute()
        if not status_exists.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application status not found"
            )
        
        # If this is primary, unset other primary colors for this status
        if color_data.is_primary:
            db.client.table("status_colors").update({"is_primary": False}).eq("status_id", color_data.status_id).execute()
        
        result = db.client.table("status_colors").insert({
            "status_id": color_data.status_id,
            "color_code": color_data.color_code,
            "color_name": color_data.color_name,
            "is_primary": color_data.is_primary
        }).execute()
        
        return {
            "success": True,
            "data": result.data[0] if result.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create status color: {str(e)}"
        )

@router.put("/status-colors/{color_id}", response_model=StatusColorResponse)
async def update_status_color(
    color_id: int,
    color_data: StatusColorUpdate,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Update a status color (Manager only)"""
    try:
        # Check if color exists
        existing = db.client.table("status_colors").select("status_id").eq("id", color_id).single().execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Status color not found"
            )
        
        status_id = existing.data["status_id"]
        
        # If setting as primary, unset other primary colors
        if color_data.is_primary is True:
            db.client.table("status_colors").update({"is_primary": False}).eq("status_id", status_id).neq("id", color_id).execute()
        
        # Build update data
        update_data = {}
        if color_data.color_code is not None:
            update_data["color_code"] = color_data.color_code
        if color_data.color_name is not None:
            update_data["color_name"] = color_data.color_name
        if color_data.is_primary is not None:
            update_data["is_primary"] = color_data.is_primary
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = db.client.table("status_colors").update(update_data).eq("id", color_id).execute()
        return {
            "success": True,
            "data": result.data[0] if result.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update status color: {str(e)}"
        )

@router.delete("/status-colors/{color_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status_color(
    color_id: int,
    user=Depends(AuthMiddleware.require_role(["manager"]))
):
    """Delete a status color (Manager only)"""
    try:
        result = db.client.table("status_colors").delete().eq("id", color_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Status color not found"
            )
        
        return {"success": True, "message": "Status color deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete status color: {str(e)}"
        )
