from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.models import BudgetStatus, SyncStatus, Budget, UserRole

class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    currency: str = Field("USD", pattern=r'^[A-Z]{3}$')

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    currency: Optional[str] = Field(None, pattern=r'^[A-Z]{3}$')
    status: Optional[BudgetStatus] = None

class UserRoleUpdate(BaseModel):
    role: UserRole = Field(..., description="New role for the user (admin, editor, viewer)")

class BudgetUserButgetResponse(BaseModel):
    user: str
    role: UserRole
    
    class Config:
        from_attributes = True

class BudgetResponse(BudgetBase):
    id: str
    status: BudgetStatus
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    sync_status: SyncStatus
    user_budgets: Optional[List[BudgetUserButgetResponse]]  # Will contain user info with roles 

    class Config:
        from_attributes = True

class BudgetListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[BudgetResponse]

def budget_to_dict(budget: Budget) -> dict:
    try:
        
        user_budgets = [
            {
                "user": user_budget.user.name,
                "role": user_budget.role
            }
            for user_budget in getattr(budget, 'user_budgets', [])
            if hasattr(user_budget, 'user') and user_budget.user is not None
        ]
                
        return dict({
            "id": str(budget.id),
            "name": budget.name,
            "currency": budget.currency,
            "status": budget.status,
            "created_at": budget.created_at,
            "updated_at": budget.updated_at,
            "archived_at": budget.archived_at,
            "sync_status": budget.sync_status,
            "user_budgets": user_budgets
        })
        
    except Exception as e:
        print("budget_to_dict error")
        print(e)
        return {}