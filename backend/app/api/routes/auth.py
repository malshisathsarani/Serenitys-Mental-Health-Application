"""
Authentication API Routes
User registration, login, and account management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.core.database import get_db
from app.models.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    UserUpdate,
    PasswordChange,
)
from app.services.auth_service import get_auth_service, AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """
    Extract user_id from JWT token in Authorization header
    Used as FastAPI dependency for protected routes
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        # Format: "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        auth_service = get_auth_service()
        payload = auth_service.verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id
        
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except Exception as e:
        logger.error(f"Token extraction error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# ============================================================================
# REGISTRATION & LOGIN
# ============================================================================

@router.post("/register", response_model=TokenResponse)
async def register(
    request: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account
    
    Returns JWT token and user information
    """
    try:
        logger.info(f"[API] Register endpoint called:")
        logger.info(f"[API]   username={request.username} (type={type(request.username).__name__}, len={len(request.username)})")
        logger.info(f"[API]   email={request.email} (type={type(request.email).__name__})")
        logger.info(f"[API]   password={request.password} (type={type(request.password).__name__}, len={len(request.password)}, bytes={len(request.password.encode())})")
        logger.info(f"[API]   full_name={request.full_name}")
        
        result = await auth_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            db=db
        )
        
        if result.get("status") == "error":
            logger.error(f"[API] Registration failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        logger.info(f"[API] Registration successful for {request.username}")
        return TokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            user=result["user"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Unexpected error in register: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and generate JWT token
    
    Returns JWT token and user information
    """
    result = await auth_service.login_user(
        email=request.email,
        password=request.password,
        db=db
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=401, detail=result.get("error"))
    
    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"],
        user=result["user"]
    )


# ============================================================================
# ACCOUNT MANAGEMENT (Protected Routes)
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user information
    
    Requires: Authorization header with Bearer token
    """
    user = await auth_service.get_user_by_id(user_id, db)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_orm(user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    request: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user profile information
    
    Requires: Authorization header with Bearer token
    """
    try:
        user = await auth_service.get_user_by_id(user_id, db)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed fields
        if request.full_name is not None:
            user.full_name = request.full_name
        
        if request.email is not None and request.email != user.email:
            # Check if new email is already in use
            existing = await auth_service.get_user_by_email(request.email, db)
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use")
            user.email = request.email.lower()
        
        await db.commit()
        logger.info(f"Profile updated for user_id={user_id}")
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.post("/change-password")
async def change_password(
    request: PasswordChange,
    user_id: int = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password
    
    Requires: Authorization header with Bearer token
    """
    result = await auth_service.change_password(
        user_id=user_id,
        old_password=request.old_password,
        new_password=request.new_password,
        db=db
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return {"status": "success", "message": result.get("message")}
