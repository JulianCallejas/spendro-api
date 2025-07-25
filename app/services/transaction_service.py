from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.sql import exists
from typing import Optional, Tuple, List
from datetime import datetime, date

from app.models.models import Transaction, RecurringTransaction, UserBudget, UserRole
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate,
    RecurringTransactionCreate, RecurringTransactionUpdate
)

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_transaction(self, transaction_data: TransactionCreate, user_id: str) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(
            budget_id=transaction_data.budget_id,
            user_id=user_id,
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            type=transaction_data.type,
            category=transaction_data.category,
            subcategory=transaction_data.subcategory,
            description=transaction_data.description,
            exchange_rate=transaction_data.exchange_rate,
            date=transaction_data.date,
            details=transaction_data.details
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    async def list_user_transactions(
        self,
        user_id: str,
        budget_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[Transaction], int]:
        """List transactions for user with filtering"""
        # Get user's accessible budgets
        user_budgets = self.db.query(UserBudget.budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .subquery()
        
        query = self.db.query(Transaction)\
            .filter(Transaction.budget_id.in_(user_budgets))
        
        # Apply filters
        if budget_id:
            query = query.filter(Transaction.budget_id == budget_id)
        
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        
        if category:
            query = query.filter(Transaction.category == category)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        
        # Order by date descending
        query = query.order_by(Transaction.budget_id.asc(), Transaction.date.desc())
        
        total = query.count()
        transactions = query.offset(offset).limit(limit).all()
        
        return transactions, total
    
    async def get_user_transaction(self, transaction_id: str, user_id: str) -> Optional[Transaction]:
        """Get specific transaction if user has access"""

        # user_budgets = self.db.query(UserBudget.budget_id)\
        #     .filter(UserBudget.user_id == user_id)\
        #     .subquery()
            
            # .filter(Transaction.budget_id.in_(user_budgets))\
        return self.db.query(Transaction)\
            .filter(Transaction.id == transaction_id)\
            .filter(
                exists().where(
                    (UserBudget.budget_id == Transaction.budget_id) &
                    (UserBudget.user_id == user_id)
                )
            )\
            .filter(Transaction.deleted_at.is_(None))\
            .first()
    
    async def update_user_transaction(
        self, 
        transaction_id: str, 
        transaction_update: TransactionUpdate, 
        user_id: str
    ) -> Optional[Transaction]:
        """Update transaction if user has access"""
        transaction = await self.get_user_transaction(transaction_id, user_id)
        
        if not transaction:
            return None
        
        update_data = transaction_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(transaction, field, value)
        
        transaction.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    async def delete_user_transaction(self, transaction_id: str, user_id: str) -> bool:
        """Soft delete transaction if user has access"""
        transaction = await self.get_user_transaction(transaction_id, user_id)
        
        if not transaction:
            return False
        
        self.db.delete(transaction)
        self.db.commit()
        
        return True
    
    # Recurring Transactions
    
    async def create_recurring_transaction(
        self, 
        recurring_data: RecurringTransactionCreate, 
        user_id: str
    ) -> RecurringTransaction:
        """Create a new recurring transaction"""
        recurring_transaction = RecurringTransaction(
            budget_id=recurring_data.budget_id,
            user_id=user_id,
            schedule=recurring_data.schedule,
            amount=recurring_data.amount,
            currency=recurring_data.currency,
            type=recurring_data.type,
            category=recurring_data.category,
            subcategory=recurring_data.subcategory,
            description=recurring_data.description,
            next_execution=recurring_data.next_execution
        )
        
        self.db.add(recurring_transaction)
        self.db.commit()
        self.db.refresh(recurring_transaction)
        
        return recurring_transaction
    
    async def list_user_recurring_transactions(
        self,
        user_id: str,
        budget_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[RecurringTransaction]:
        """List recurring transactions for user"""
        
       
        query = self.db.query(RecurringTransaction).filter(
                exists().where(
                    (UserBudget.budget_id == Transaction.budget_id) &
                    (UserBudget.user_id == user_id)
                )
            )
        
        if budget_id:
            query = query.filter(RecurringTransaction.budget_id == budget_id)
        
        if is_active is not None:
            query = query.filter(RecurringTransaction.is_active == is_active)
        
        return query.all()
    
    async def update_user_recurring_transaction(
        self,
        recurring_id: str,
        recurring_update: RecurringTransactionUpdate,
        user_id: str
    ) -> Optional[RecurringTransaction]:
        """Update recurring transaction if user has access"""
        
        user_can_edit_filter = or_(
            UserBudget.role == UserRole.ADMIN,
            UserBudget.role == UserRole.EDITOR,
        )
        
        user_budgets = self.db.query(UserBudget.budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .filter(user_can_edit_filter)\
            .subquery()
        
        recurring_transaction = self.db.query(RecurringTransaction)\
            .filter(RecurringTransaction.id == recurring_id)\
            .filter(RecurringTransaction.budget_id.in_(user_budgets))\
            .first()
        
        if not recurring_transaction:
            return None
        
        update_data = recurring_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(recurring_transaction, field, value)
        
        recurring_transaction.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(recurring_transaction)
        
        return recurring_transaction
    
    async def delete_user_recurring_transaction(self, recurring_id: str, user_id: str) -> bool:
        """Delete recurring transaction if user has access"""
        user_can_edit_filter = or_(
            UserBudget.role == UserRole.ADMIN,
            UserBudget.role == UserRole.EDITOR,
        )
        
        user_budgets = self.db.query(UserBudget.budget_id)\
            .filter(UserBudget.user_id == user_id)\
            .filter(user_can_edit_filter)\
            .subquery()
        
        recurring_transaction = self.db.query(RecurringTransaction)\
            .filter(RecurringTransaction.id == recurring_id)\
            .filter(RecurringTransaction.budget_id.in_(user_budgets))\
            .first()
        
        if not recurring_transaction:
            return False
        
        self.db.delete(recurring_transaction)
        self.db.commit()
        
        return True