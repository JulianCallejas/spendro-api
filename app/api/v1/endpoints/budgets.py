from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.schemas.budget import (
    BudgetCreate, BudgetUpdate, BudgetResponse, 
    BudgetListResponse, UserRoleUpdate, budget_to_dict
)
from app.models.models import User
from app.services.budget_service import BudgetService

router = APIRouter()

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new budget
    
    - **name**: Budget name (e.g., "Home", "Office Project")
    - **currency**: Budget currency (3-letter ISO code, default: USD)
    
    Returns created budget information
    """
    try:
        budget_service = BudgetService(db)
        budget = await budget_service.create_budget(
            budget_data, 
            current_user.id
        )
        
        budget_dict = budget_to_dict(budget)
        return BudgetResponse.from_orm(budget_dict)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create budget"
        )


@router.get("/", response_model=BudgetListResponse)
async def list_user_budgets(
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search by budget name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List budgets for current user with pagination and search
    
    - **limit**: Number of budgets to return (max 100)
    - **offset**: Number of budgets to skip
    - **search**: Search query for budget name
    
    Returns paginated list of user's budgets
    """
    try:
        budget_service = BudgetService(db)
        budgets, total = await budget_service.list_user_budgets(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            search=search
        )
        
        return BudgetListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[BudgetResponse.from_orm(budget_to_dict(budget)) for budget in budgets]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve budgets"
        )


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get budget by ID with user access information
    
    - **budget_id**: Budget's unique identifier
    
    Returns budget information with associated users and their roles
    """
    try:
        budget_service = BudgetService(db)
        budget = await budget_service.get_budget_by_id(budget_id, current_user.id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        return budget_to_dict(budget)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get budget {budget_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve budget"
        )


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update budget information
    
    - **budget_id**: Budget's unique identifier
    - **name**: Budget name (optional)
    - **currency**: Budget currency (optional)
    - **status**: Budget status (optional)
    
    Returns updated budget information
    """
    try:
        budget_service = BudgetService(db)
        
        budget = await budget_service.update_budget(budget_id, budget_update, current_user.id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found into your accessible budgets"
            )
        
        return BudgetResponse.from_orm( budget_to_dict(budget))
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to save budget {budget_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update budget"
        )


@router.patch("/archive/{budget_id}", status_code=status.HTTP_200_OK)
async def archive_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive budget (archives it instead of permanent deletion)
    
    - **budget_id**: Budget's unique identifier
    
    Archives the budget to preserve transaction history
    """
    try:
        budget_service = BudgetService(db)
        
        # Check if user has admin access to this budget
        
        success = await budget_service.archive_budget(budget_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found into your accessible budgets"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to delete budget {budget_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete budget"
        )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete budget (Permanent deletion)
    
    - **budget_id**: Budget's unique identifier
    
    Deletes the budget and its transactions permanently and cannot be recovered
    """
    try:
        budget_service = BudgetService(db)
        
        # Check if user has admin access to this budget
        
        success = await budget_service.delete_budget(budget_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found into your accessible budgets"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to delete budget {budget_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete budget"
        )


@router.post("/{budget_id}/users/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_user_to_budget(
    budget_id: str,
    user_id: str,
    request: Request,
    role_data: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add user to budget with specified role
    
    - **budget_id**: Budget's unique identifier
    - **user_id**: User's unique identifier
    - **role**: User's role in the budget (admin, editor, viewer)
    
    Adds user to budget with specified permissions
    """
    try:
        budget_service = BudgetService(db)
        
        
        success = await budget_service.add_user_to_budget(
            budget_id, 
            user_id, 
            role_data.role.value,
            current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add user to budget"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to add user to budget {budget_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add user to budget"
        )


@router.delete("/{budget_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_budget(
    budget_id: str,
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove user from budget
    
    - **budget_id**: Budget's unique identifier
    - **user_id**: User's unique identifier
    
    Removes user's access to the specified budget
    """
    try:
        budget_service = BudgetService(db)
        
        success = await budget_service.remove_user_from_budget(budget_id, user_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in budget"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove user from budget"
        )


@router.patch("/{budget_id}/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_role(
    budget_id: str,
    user_id: str,
    role_update: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's role in budget
    
    - **budget_id**: Budget's unique identifier
    - **user_id**: User's unique identifier
    - **role**: New role for the user (admin, editor, viewer)
    
    Updates the user's role in the specified budget. Only admins can update roles.
    """
    try:
        budget_service = BudgetService(db)
        
        success = await budget_service.update_user_role(
            budget_id, 
            user_id, 
            role_update.role.value,
            current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user role"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to update user role in budget {budget_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )