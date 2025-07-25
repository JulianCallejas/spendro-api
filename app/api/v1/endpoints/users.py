from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.models import User
from app.schemas.user import UserResponse, UserListResponse, UserUpdate, user_to_dict
from app.services.user_service import UserService

security = HTTPBearer()

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user's information
    
    Returns the current user's profile information
    """
    try:
        return user_to_dict(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current authenticated user's information
    
    - **name**: User's full name (optional)
    - **email**: User's email address (optional)
    - **phone**: User's phone number (optional)
    - **is_active**: User's active status (optional)
    
    Returns updated user information
    """
    try:
        user_service = UserService(db)
        user = await user_service.update_user(str(current_user.id), user_update)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_to_dict(user)
        
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information"
        )


@router.get("/search", response_model=UserListResponse)
async def search_users(
    query: str = Query(..., description="Search query for name, email, or phone"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search users by name, email, or phone
    
    - **query**: Search string to match against name, email, or phone
    - **limit**: Number of users to return (max 100)
    - **offset**: Number of users to skip
    
    Returns paginated list of matching users
    """
    try:
        user_service = UserService(db)
        users, total = await user_service.search_users(
            query=query,
            limit=limit,
            offset=offset
        )
        
        return UserListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[UserResponse(**user_to_dict(user)) for user in users]
        )
        
    except Exception as e:
        logging.error(f"Failed to search users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    
    - **user_id**: User's unique identifier
    
    Returns user information
    """
    try:
        
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot access another user's information",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_to_dict(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

        
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current authenticated user's account
    
    This action is irreversible and will permanently delete the user's account
    """
    try:
        user_service = UserService(db)
        
        # current_user.is_active = False
        # remove_user =UserUpdate(**user_to_dict(current_user))
        # success = await user_service.update_user(str(current_user.id), remove_user)
        
        success = await user_service.delete_user(str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )
