"""
Authentication Middleware
Handles JWT token validation and user authentication
"""

import os
import jwt
from typing import Optional, Dict
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Get secret key from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except (jwt.PyJWTError, jwt.InvalidTokenError, Exception) as e:
            logger.warning(f"JWT validation error: {e}")
            return None
    
    @staticmethod
    async def get_current_user(credentials: HTTPAuthorizationCredentials) -> Dict:
        """Get current user from token"""
        token = credentials.credentials
        payload = AuthMiddleware.verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    
    @staticmethod
    def require_role(allowed_roles: list):
        """Dependency to require specific roles"""
        from fastapi import Depends
        
        async def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            token = credentials.credentials
            payload = AuthMiddleware.verify_token(token)
            
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_role = payload.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            
            return payload
        
        return role_checker


async def auth_middleware(request: Request, call_next):
    """FastAPI middleware to add user info to request"""
    # Skip auth for public endpoints
    public_paths = ["/docs", "/redoc", "/openapi.json", "/api/auth/login", "/health"]
    
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Extract token from header
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = AuthMiddleware.verify_token(token)
        
        if payload:
            # Attach user info to request state
            request.state.user = payload
            logger.info(f"Authenticated user: {payload.get('email')}")
        else:
            logger.warning("Invalid or expired token")
    
    response = await call_next(request)
    return response


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    import bcrypt
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
