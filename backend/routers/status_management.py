"""
Status Management Router
Simple CRUD for eligibility/application statuses
Suitable for LoanWise v4.0
"""

from fastapi import APIRouter, HTTPException, status, Depends
from database.client import db
from middleware.auth import AuthMiddleware

router = APIRouter(prefix="/api/status-management", tags=["Status Management"])

@router.get("/eligibility-statuses")
async def list_statuses(user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))):
    try:
        response = db.client.table("eligibility_statuses").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        # If table doesn't exist, return empty list gracefully
        return []

@router.get("/eligibility-statuses/{status_id}")
async def get_status(status_id: int, user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))):
    try:
        response = db.client.table("eligibility_statuses").select("*").eq("id", status_id).single().execute()
        if not response.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Status not found")
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
