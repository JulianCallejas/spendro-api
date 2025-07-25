from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_token
from app.core.cache import SingletonCache, get_cache
from app.models.models import User
from app.schemas.user import user_from_dict, user_to_dict

# Create a security scheme that will be recognized by OpenAPI
security = HTTPBearer(
    scheme_name="BearerAuth",
    description="Enter your JWT token"
)

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    cache: SingletonCache = Depends(get_cache)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    try:
        user_id = request.state.user_id
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user from redis or database
        cached_user_data = cache.get(user_id)
        
        if cached_user_data is not None:
            # Convert cached dictionary back to User object
            user = user_from_dict(cached_user_data)
        else:
            user = db.query(User).filter(User.id == user_id).first()
            # Cache the user for future requests
            if user:
                user_dict = user_to_dict(user)
                cache.set(user_id, user_dict)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user (not disabled)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional dependency to get current user (returns None if not authenticated)
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
        
    except Exception:
        return None