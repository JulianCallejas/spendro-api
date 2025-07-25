from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.models.models import User, Budget, Transaction, RecurringTransaction, SyncStatus
from app.schemas.sync import SyncPushRequest

class SyncService:
    def __init__(self, db: Session):
        self.db = db
    
    async def push_changes(self, user_id: str, sync_data: SyncPushRequest) -> Dict[str, Any]:
        """Push local changes to server"""
        processed = 0
        conflicts = []
        
        try:
            # Process users
            if sync_data.users:
                for user_data in sync_data.users:
                    result = await self._process_user_sync(user_id, user_data)
                    if result["status"] == "processed":
                        processed += 1
                    elif result["status"] == "conflict":
                        conflicts.append(result["conflict"])
            
            # Process budgets
            if sync_data.budgets:
                for budget_data in sync_data.budgets:
                    result = await self._process_budget_sync(user_id, budget_data)
                    if result["status"] == "processed":
                        processed += 1
                    elif result["status"] == "conflict":
                        conflicts.append(result["conflict"])
            
            # Process transactions
            if sync_data.transactions:
                for transaction_data in sync_data.transactions:
                    result = await self._process_transaction_sync(user_id, transaction_data)
                    if result["status"] == "processed":
                        processed += 1
                    elif result["status"] == "conflict":
                        conflicts.append(result["conflict"])
            
            # Process recurring transactions
            if sync_data.recurring_transactions:
                for recurring_data in sync_data.recurring_transactions:
                    result = await self._process_recurring_sync(user_id, recurring_data)
                    if result["status"] == "processed":
                        processed += 1
                    elif result["status"] == "conflict":
                        conflicts.append(result["conflict"])
            
            self.db.commit()
            
            return {
                "processed": processed,
                "conflicts": conflicts
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def pull_changes(self, user_id: str, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Pull changes since specified timestamp"""
        if since is None:
            since = datetime.min
        
        # Get user's accessible budgets for filtering
        from app.models.models import UserBudget
        user_budgets = self.db.query(UserBudget.budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .subquery()
        
        # Get updated users (only current user)
        users = []
        user = self.db.query(User)\
            .filter(User.id == user_id)\
            .filter(User.updated_at > since)\
            .first()
        
        if user:
            users.append(self._serialize_user(user))
        
        # Get updated budgets
        budgets = []
        budget_records = self.db.query(Budget)\
            .filter(Budget.id.in_(user_budgets))\
            .filter(Budget.updated_at > since)\
            .all()
        
        for budget in budget_records:
            budgets.append(self._serialize_budget(budget))
        
        # Get updated transactions
        transactions = []
        transaction_records = self.db.query(Transaction)\
            .filter(Transaction.budget_id.in_(user_budgets))\
            .filter(Transaction.updated_at > since)\
            .all()
        
        for transaction in transaction_records:
            transactions.append(self._serialize_transaction(transaction))
        
        # Get updated recurring transactions
        recurring_transactions = []
        recurring_records = self.db.query(RecurringTransaction)\
            .filter(RecurringTransaction.budget_id.in_(user_budgets))\
            .filter(RecurringTransaction.updated_at > since)\
            .all()
        
        for recurring in recurring_records:
            recurring_transactions.append(self._serialize_recurring_transaction(recurring))
        
        return {
            "users": users,
            "budgets": budgets,
            "transactions": transactions,
            "recurring_transactions": recurring_transactions
        }
    
    async def get_user_conflicts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get unresolved conflicts for user"""
        # This is a simplified implementation
        # In a real system, you'd have a conflicts table
        return []
    
    async def resolve_conflicts(self, user_id: str, resolutions: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve sync conflicts"""
        resolved_count = 0
        remaining_conflicts = 0
        
        # Implementation would depend on conflict storage mechanism
        # For now, return success
        
        return {
            "resolved_count": resolved_count,
            "remaining_conflicts": remaining_conflicts
        }
    
    async def get_sync_status(self, user_id: str) -> Dict[str, Any]:
        """Get sync status for user"""
        # Get last sync time (could be stored per user)
        last_sync = datetime.utcnow()
        
        # Count pending changes
        pending_changes = 0
        conflicts_count = 0
        
        return {
            "last_sync": last_sync,
            "pending_changes": pending_changes,
            "conflicts_count": conflicts_count,
            "sync_health": "healthy"
        }
    
    # Helper methods for processing sync data
    
    async def _process_user_sync(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user sync data"""
        # Simplified implementation
        return {"status": "processed"}
    
    async def _process_budget_sync(self, user_id: str, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process budget sync data"""
        # Simplified implementation
        return {"status": "processed"}
    
    async def _process_transaction_sync(self, user_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process transaction sync data"""
        # Simplified implementation
        return {"status": "processed"}
    
    async def _process_recurring_sync(self, user_id: str, recurring_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process recurring transaction sync data"""
        # Simplified implementation
        return {"status": "processed"}
    
    # Serialization methods
    
    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user for sync"""
        return {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "auth_method": user.auth_method.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "sync_status": user.sync_status.value
        }
    
    def _serialize_budget(self, budget: Budget) -> Dict[str, Any]:
        """Serialize budget for sync"""
        return {
            "id": str(budget.id),
            "name": budget.name,
            "currency": budget.currency,
            "status": budget.status.value,
            "created_at": budget.created_at.isoformat(),
            "updated_at": budget.updated_at.isoformat(),
            "archived_at": budget.archived_at.isoformat() if budget.archived_at else None,
            "sync_status": budget.sync_status.value
        }
    
    def _serialize_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """Serialize transaction for sync"""
        return {
            "id": str(transaction.id),
            "budget_id": str(transaction.budget_id),
            "user_id": str(transaction.user_id),
            "amount": transaction.amount,
            "currency": transaction.currency,
            "type": transaction.type.value,
            "category": transaction.category,
            "subcategory": transaction.subcategory,
            "description": transaction.description,
            "exchange_rate": transaction.exchange_rate,
            "date": transaction.date.isoformat(),
            "details": transaction.details,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat(),
            "deleted_at": transaction.deleted_at.isoformat() if transaction.deleted_at else None,
            "sync_status": transaction.sync_status.value
        }
    
    def _serialize_recurring_transaction(self, recurring: RecurringTransaction) -> Dict[str, Any]:
        """Serialize recurring transaction for sync"""
        return {
            "id": str(recurring.id),
            "budget_id": str(recurring.budget_id),
            "user_id": str(recurring.user_id),
            "schedule": recurring.schedule,
            "amount": recurring.amount,
            "currency": recurring.currency,
            "type": recurring.type.value,
            "category": recurring.category,
            "subcategory": recurring.subcategory,
            "description": recurring.description,
            "is_active": recurring.is_active,
            "next_execution": recurring.next_execution.isoformat(),
            "created_at": recurring.created_at.isoformat(),
            "updated_at": recurring.updated_at.isoformat(),
            "sync_status": recurring.sync_status.value
        }