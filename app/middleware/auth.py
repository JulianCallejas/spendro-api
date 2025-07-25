from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from app.core.security import verify_token
from app.core.database import get_db

security = HTTPBearer(auto_error=False)

class AuthMiddleware(BaseHTTPMiddleware):
    """JWT Authentication middleware - Extracts user info from token when present"""
    
    # Routes that don't require authentication (public routes)
    PUBLIC_ROUTES = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
    ]
    
    # Auth routes that handle their own authentication
    AUTH_ROUTES = [
        "/api/v1/auth/register",
        "/api/v1/auth/login", 
        "/api/v1/auth/google",
        "/api/v1/auth/biometric",
    ]
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Skip processing for public routes
        
        if any(path == "/" or path == route or path.startswith(route) for route in self.PUBLIC_ROUTES):
            return await call_next(request)
        
        # Skip authentication enforcement for auth routes (they handle their own auth)
        if any(path.startswith(route) for route in self.AUTH_ROUTES):
            return await call_next(request)
        
        # For all other routes, try to extract user info from token if present
        # But don't enforce authentication here - let the dependencies handle that
        authorization = request.headers.get("Authorization")
        if authorization:
            try:
                # Extract token from "Bearer <token>"
                parts = authorization.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    token = parts[1]
                    
                    # Verify token and add user info to request state
                    payload = verify_token(token)
                    
                    request.state.user_id = payload.get("sub")
                    request.state.user_email = payload.get("email")
                    request.state.user_name = payload.get("name")
                    request.state.user_roles = payload.get("roles", [])
                    
            except Exception as e:
                # Don't fail here - let the dependencies handle authentication errors
                logging.warning(f"Token verification failed in middleware: {e}")
                # Clear any partial state
                if hasattr(request.state, 'user_id'):
                    delattr(request.state, 'user_id')
        
        return await call_next(request)