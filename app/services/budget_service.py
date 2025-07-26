from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
import uuid

from app.models.models import Budget, UserBudget, User, BudgetStatus, UserRole
from app.schemas.budget import BudgetCreate, BudgetUpdate

class BudgetService:
    def __init__(self, db: Session):
        self.db = db
    
    
    async def create_budget(self, budget_data: BudgetCreate, user_id: str) -> Budget:
        """Create a new budget and add creator as admin"""
        
        budget = Budget(
            name=budget_data.name,
            currency=budget_data.currency
        )
        
        self.db.add(budget)
        self.db.flush()  # Get the budget ID
        
        # Add creator as admin
        user_budget = UserBudget(
            user_id=user_id,
            budget_id=budget.id,
            role=UserRole.ADMIN
        )
        
        self.db.add(user_budget)
        self.db.commit()
        self.db.refresh(budget)
        
        return budget
    
    async def list_user_budgets(
        self, 
        user_id: str, 
        limit: int = 10, 
        offset: int = 0, 
        search: Optional[str] = None
    ) -> Tuple[List[Budget], int]:
        """List budgets for a specific user with pagination and search"""
        
        query = self.db.query(Budget)\
            .join(UserBudget, Budget.id == UserBudget.budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .filter(Budget.status == BudgetStatus.ACTIVE)
        
        if search:
            query = query.filter(Budget.name.ilike(f"%{search}%"))
        
        total = query.count()
        budgets = query.offset(offset).limit(limit).all()
        
        return budgets, total
    
    
    async def get_budget_by_id(self, budget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        budget = self.db.query(Budget)\
            .join(UserBudget, Budget.id == UserBudget.budget_id)\
            .filter(Budget.id == budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .filter(Budget.status == BudgetStatus.ACTIVE)\
            .first()

        return budget
    
   
    async def update_budget(self, budget_id: str, budget_update: BudgetUpdate, user_id: str) -> Optional[Budget]:
        """Update budget information"""
        
        if not self.isValidUUID(budget_id):
            return None
        
        user_can_edit_filter = or_(
            UserBudget.role == UserRole.ADMIN,
            UserBudget.role == UserRole.EDITOR,
        )
        
        budget = self.db.query(Budget)\
            .join(UserBudget, Budget.id == UserBudget.budget_id)\
            .filter(Budget.id == budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .filter(user_can_edit_filter)\
            .filter(Budget.status == BudgetStatus.ACTIVE)\
            .first()
        
        if not budget:
            return None
        
        update_data = budget_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(budget, field, value)
        
        budget.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(budget)
        
        return budget
   
    
    async def archive_budget(self, budget_id: str, user_id: str) -> bool:
        """Archive budget (soft delete)"""
        
        budget = await self.budget_owned_by_user(user_id, budget_id)
        
        if not budget:
            return False
        
        budget.status = BudgetStatus.ARCHIVED
        budget.archived_at = datetime.utcnow()
        budget.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    
    async def delete_budget(self, budget_id: str, user_id: str) -> bool:
        """Archive budget (soft delete)"""
        
        budget = budget = await self.budget_owned_by_user(user_id, budget_id)
        
        if not budget:
            return False
        
        self.db.delete(budget)
        self.db.commit()
        
        return True

    
    async def user_has_budget_access(self, user_id: str, budget_id: str) -> bool:
        """Check if user has access to budget"""
        
        if not self.isValidUUID(budget_id):
            return False
        
        user_can_edit_filter = or_(
            UserBudget.role == UserRole.ADMIN,
            UserBudget.role == UserRole.EDITOR,
        )
        
        budget = self.db.query(Budget)\
            .join(UserBudget, Budget.id == UserBudget.budget_id)\
            .filter(Budget.id == budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .filter(user_can_edit_filter)\
            .filter(Budget.status == BudgetStatus.ACTIVE)\
            .first()
        
        return budget is not None
    
    
    async def user_has_budget_admin_access(self, user_id: str, budget_id: str) -> bool:
        """Check if user has admin access to budget"""
        user_budget = self.db.query(UserBudget)\
            .filter(
                and_(
                    UserBudget.user_id == user_id,
                    UserBudget.budget_id == budget_id,
                    UserBudget.role == UserRole.ADMIN
                )
            )\
            .first()
        
        return user_budget is not None
    
    
    async def add_user_to_budget(self, budget_id: str, user_id: str, role: str, admin_id: str) -> bool:
        """Add user to budget with specified role"""
        
        budget = self.db.query(Budget)\
            .join(UserBudget, Budget.id == UserBudget.budget_id)\
            .filter(Budget.id == budget_id)\
            .filter(UserBudget.user_id == admin_id)\
            .filter(UserBudget.role == UserRole.ADMIN)\
            .filter(Budget.status == BudgetStatus.ACTIVE)\
            .first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found into your accessible budgets"
            )
            return False
        
        existing = self.db.query(UserBudget)\
            .filter(
                and_(
                    UserBudget.user_id == user_id,
                    UserBudget.budget_id == budget_id
                )
            )\
            .first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has access to budget"
            )
            return False
        
        user_budget = UserBudget(
            user_id=user_id,
            budget_id=budget_id,
            role=UserRole(role)
        )
        
        self.db.add(user_budget)
        self.db.commit()
        
        return True
    
    
    async def remove_user_from_budget(self, budget_id: str, user_id: str, admin_id: str) -> bool:
        """Remove user from budget"""
        
        budget = await self.budget_owned_by_user(admin_id, budget_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found or you don't have admin access"
            )
                
        user_budget = self.db.query(UserBudget)\
            .filter(
                and_(
                    UserBudget.user_id == user_id,
                    UserBudget.budget_id == budget_id
                )
            )\
            .first()
        
        if not user_budget:
            return False
        
        # Check if trying to remove the last admin
        if user_budget.role == UserRole.ADMIN:
            admin_count = await self.count_admin_users(budget_id)
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last admin from budget. Budget must have at least one admin user."
                )
        
        self.db.delete(user_budget)
        self.db.commit()
        
        return True
    
    
    async def count_admin_users(self, budget_id: str) -> int:
        """Count the number of admin users in a budget"""
        admin_count = self.db.query(UserBudget)\
            .filter(
                and_(
                    UserBudget.budget_id == budget_id,
                    UserBudget.role == UserRole.ADMIN
                )
            )\
            .count()
        
        return admin_count
    
    
    async def update_user_role(self, budget_id: str, user_id: str, new_role: str, admin_id: str) -> bool:
        """Update user's role in budget"""
        
        # Check if admin has admin access to budget
        budget = await self.budget_owned_by_user(admin_id, budget_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found or you don't have admin access"
            )
        
        # Find the user's budget relationship
        user_budget = self.db.query(UserBudget)\
            .filter(
                and_(
                    UserBudget.user_id == user_id,
                    UserBudget.budget_id == budget_id
                )
            )\
            .first()
        
        if not user_budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in budget"
            )
        
        # Check if trying to remove the last admin
        if user_budget.role == UserRole.ADMIN and new_role != UserRole.ADMIN.value:
            admin_count = await self.count_admin_users(budget_id)
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last admin from budget. Budget must have at least one admin user."
                )
        
        # Update the role
        user_budget.role = UserRole(new_role)
        self.db.commit()
        
        return True
    
    
    async def budget_owned_by_user(self, user_id: str, budget_id: str) -> Budget:
        budget = self.db.query(Budget)\
            .join(UserBudget, Budget.id == UserBudget.budget_id)\
            .filter(Budget.id == budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .filter(UserBudget.role == UserRole.ADMIN)\
            .filter(Budget.status == BudgetStatus.ACTIVE)\
            .first()
            
        return budget
    
    
    def isValidUUID(self, uuid_string: str) -> bool:
        try:
            uuid_object = uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False