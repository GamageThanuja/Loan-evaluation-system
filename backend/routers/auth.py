"""
Authentication Router
Handles user authentication (Login/Register)
Suitable for LoanWise v4.0
"""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Add parent directories to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from database.client import db
from middleware.auth import AuthMiddleware, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "loan_officer"

@router.post("/login")
async def login(request: LoginRequest):
    user = db.get_user_by_email(request.email)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    
    # Check password hash (handle legacy or missing password fields gracefully)
    password_hash = user.get("password_hash")
    if not password_hash or not verify_password(request.password, password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        
    # Check if the requested role matches the user's actual role in the database
    if request.role and request.role != user.get("role"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Cannot login as {request.role}. Your assigned role is {user.get('role')}.")
        
    token = AuthMiddleware.create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"]
    })
    
    # Remove sensitive data from response
    safe_user = {k: v for k, v in user.items() if k not in ["password_hash", "reset_token"]}
    
    return {
        "success": True,
        "token": token,
        "user": safe_user
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    if db.get_user_by_email(request.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists")
        
    user_data = {
        "email": request.email,
        "password_hash": hash_password(request.password),
        "name": request.name,
        "role": request.role,
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }
    
    user = db.create_user(user_data)
    if not user:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create user")
        
    token = AuthMiddleware.create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"]
    })
    
    return {
        "success": True,
        "token": token,
        "user": user
    }
    
@router.get("/verify-token")
async def verify_token(user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))):
    return {"success": True, "message": "Token is valid", "user": user}
