"""
Authentication Router
Handles user authentication with role-based access (managers and loan officers)
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directories to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
import secrets
import hashlib
from dotenv import load_dotenv
import os

from middleware.auth import AuthMiddleware, hash_password, verify_password
from database.client import db

load_dotenv(project_root / ".env")

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ============================================
# MODELS
# ============================================

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=2, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role: manager or loan_officer")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "name": "John Doe",
                "phone": "+1234567890",
                "role": "loan_officer"
            }
        }

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123!"
            }
        }

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None

# ============================================
# HELPER FUNCTIONS
# ============================================

def validate_role(role: str) -> bool:
    """Validate user role"""
    allowed_roles = ["manager", "loan_officer"]
    return role.lower() in allowed_roles

def generate_reset_token() -> str:
    """Generate secure password reset token"""
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str) -> str:
    """Hash reset token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

# ============================================
# ENDPOINTS
# ============================================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new user (manager or loan officer)
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **name**: User's full name
    - **phone**: Optional phone number
    - **role**: Either 'manager' or 'loan_officer'
    """
    try:
        # Validate role
        if not validate_role(request.role):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'manager' or 'loan_officer'"
            )
        
        # Check if user already exists
        existing_user = db.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = hash_password(request.password)
        
        # Create user data
        user_data = {
            "email": request.email,
            "password_hash": hashed_password,
            "name": request.name,
            "phone": request.phone,
            "role": request.role.lower(),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Create user in database
        user = db.create_user(user_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Generate JWT token
        token = AuthMiddleware.create_access_token(
            data={
                "user_id": user["id"],
                "email": user["email"],
                "role": user["role"]
            }
        )
        
        # Remove sensitive data
        user.pop("password_hash", None)
        
        return AuthResponse(
            success=True,
            message="User registered successfully",
            token=token,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with email and password
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns JWT token and user information
    """
    try:
        # Get user from database
        user = db.get_user_by_email(request.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Please contact administrator."
            )
        
        # Verify password
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        db.update_user_last_login(user["id"])
        
        # Generate JWT token
        token = AuthMiddleware.create_access_token(
            data={
                "user_id": user["id"],
                "email": user["email"],
                "role": user["role"]
            }
        )
        
        # Remove sensitive data
        user.pop("password_hash", None)
        user.pop("reset_token", None)
        user.pop("reset_token_expires", None)
        
        return AuthResponse(
            success=True,
            message="Login successful",
            token=token,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout", response_model=AuthResponse)
async def logout(user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))):
    """
    Logout current user
    
    Requires valid JWT token in Authorization header
    """
    try:
        # In a JWT-based system, logout is typically handled client-side
        # by removing the token. For server-side tracking, you could:
        # - Add token to blacklist
        # - Update last_logout timestamp
        
        return AuthResponse(
            success=True,
            message="Logout successful"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset link
    
    - **email**: Registered email address
    
    Sends password reset token (in production, send via email)
    """
    try:
        # Get user from database
        user = db.get_user_by_email(request.email)
        
        if not user:
            # Don't reveal if email exists or not (security)
            return AuthResponse(
                success=True,
                message="If the email exists, a password reset link has been sent"
            )
        
        # Generate reset token
        reset_token = generate_reset_token()
        hashed_token = hash_reset_token(reset_token)
        
        # Set token expiration (1 hour)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Save hashed token to database
        db.update_user_reset_token(
            user["id"],
            hashed_token,
            expires_at.isoformat()
        )
        
        # TODO: In production, send email with reset link
        # For now, return token in response (NOT SECURE - for development only)
        
        return AuthResponse(
            success=True,
            message="If the email exists, a password reset link has been sent",
            token=reset_token  # REMOVE THIS IN PRODUCTION
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset request failed: {str(e)}"
        )


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using reset token
    
    - **token**: Password reset token from email
    - **new_password**: New password (min 8 characters)
    """
    try:
        # Hash the provided token
        hashed_token = hash_reset_token(request.token)
        
        # Find user with this reset token
        user = db.get_user_by_reset_token(hashed_token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Check token expiration
        if user.get("reset_token_expires"):
            expires_at = datetime.fromisoformat(user["reset_token_expires"])
            if datetime.utcnow() > expires_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reset token has expired"
                )
        
        # Hash new password
        new_password_hash = hash_password(request.new_password)
        
        # Update password and clear reset token
        db.update_user_password(user["id"], new_password_hash)
        
        return AuthResponse(
            success=True,
            message="Password reset successful. Please login with your new password."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )


@router.get("/verify-token")
async def verify_token(user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))):
    """
    Verify JWT token validity
    
    Requires valid JWT token in Authorization header
    """
    return AuthResponse(
        success=True,
        message="Token is valid",
        user=user
    )
