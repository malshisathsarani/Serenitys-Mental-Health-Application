"""
Authentication Middleware
Extracts and validates JWT tokens from request headers
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Callable
import logging

from app.services.auth_service import get_auth_service

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract JWT token from Authorization header
    Attaches user_id to request state for protected routes
    """
    
    # Routes that don't require authentication
    PUBLIC_ROUTES = {
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/api/auth/register",
        "/api/auth/login",
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> any:
        """Process request and extract auth token"""
        
        # Skip middleware for public routes
        if any(request.url.path.startswith(route) for route in self.PUBLIC_ROUTES):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        try:
            if not auth_header:
                raise HTTPException(status_code=401, detail="Missing authorization header")
            
            # Parse Bearer token
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise HTTPException(status_code=401, detail="Invalid authorization header format")
            
            token = parts[1]
            
            # Verify token
            auth_service = get_auth_service()
            payload = auth_service.verify_token(token)
            
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Attach user_id to request state
            request.state.user_id = user_id
            request.state.token_payload = payload
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Auth middleware error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        return await call_next(request)


def get_user_id_from_request(request: Request) -> int:
    """
    Helper to get user_id from request state (set by middleware)
    For use in routes that need user context
    """
    if not hasattr(request.state, "user_id"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return request.state.user_id
