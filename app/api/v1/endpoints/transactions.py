from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import logging


from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionListResponse, RecurringTransactionCreate,
    RecurringTransactionUpdate, RecurringTransactionResponse,
    transaction_to_dict
)
from app.services.transaction_service import TransactionService
from app.services.budget_service import BudgetService

router = APIRouter()

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new transaction
    
    - **budget_id**: Budget where transaction belongs
    - **amount**: Transaction amount (must be positive)
    - **currency**: Transaction currency (3-letter ISO code)
    - **type**: Transaction type (income, expense, investment)
    - **category**: Transaction category
    - **subcategory**: Transaction subcategory (optional)
    - **description**: Transaction description (optional)
    - **exchange_rate**: Exchange rate for currency conversion (default: 1.0)
    - **date**: Transaction date
    - **details**: Additional transaction metadata (optional)
    
    Returns created transaction information
    """
    try:
        # Check budget access
        budget_service = BudgetService(db)
        has_access = await budget_service.user_has_budget_access(
            current_user.id,
            transaction_data.budget_id
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this budget"
            )
            
        transaction_service = TransactionService(db)
        transaction = await transaction_service.create_transaction(
            transaction_data,
            current_user.id
        )
        
        
        return TransactionResponse.from_orm(transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to create transaction {transaction_data.budget_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transaction"
        )

@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    budget_id: Optional[str] = Query(None, description="Filter by budget ID"),
    transaction_type: Optional[str] = Query(None, pattern="^(income|expense|investment)$"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List transactions with filtering and pagination
    
    - **budget_id**: Filter by specific budget (optional)
    - **transaction_type**: Filter by transaction type (optional)
    - **category**: Filter by category (optional)
    - **start_date**: Filter transactions from this date (optional)
    - **end_date**: Filter transactions until this date (optional)
    - **limit**: Number of transactions to return (max 100)
    - **offset**: Number of transactions to skip
    
    Returns paginated list of transactions
    """
    try:
        transaction_service = TransactionService(db)
        transactions, total = await transaction_service.list_user_transactions(
            user_id=current_user.id,
            budget_id=budget_id,
            transaction_type=transaction_type,
            category=category,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return TransactionListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[TransactionResponse.from_orm(tx) for tx in transactions]
        )
        
    except Exception as e:
        logging.error(f"Failed to retrieve transactions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )

# Recurring Transactions
@router.post("/recurring", response_model=RecurringTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_transaction(
    recurring_data: RecurringTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new recurring transaction
    
    - **budget_id**: Budget where recurring transaction belongs
    - **schedule**: Recurrence schedule (daily, weekly, monthly, yearly)
    - **amount**: Transaction amount
    - **currency**: Transaction currency
    - **type**: Transaction type (income, expense, investment) 
    - **category**: Transaction category
    - **subcategory**: Transaction subcategory (optional)
    - **description**: Transaction description (optional)
    - **next_execution**: Next scheduled execution date
    
    Returns created recurring transaction information
    """
    try:
        # Check budget access
        budget_service = BudgetService(db)
        has_access = await budget_service.user_has_budget_access(
            current_user.id,
            recurring_data.budget_id
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this budget"
            )
        
        transaction_service = TransactionService(db)
        recurring_transaction = await transaction_service.create_recurring_transaction(
            recurring_data,
            current_user.id
        )
        
        return RecurringTransactionResponse.from_orm(recurring_transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recurring transaction"
        )

@router.get("/recurring", response_model=list[RecurringTransactionResponse])
async def list_recurring_transactions(
    budget_id: Optional[str] = Query(None, description="Filter by budget ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List recurring transactions
    
    - **budget_id**: Filter by specific budget (optional)
    - **is_active**: Filter by active status (optional)
    
    Returns list of recurring transactions
    """
    try:
        
        transaction_service = TransactionService(db)
        recurring_transactions = await transaction_service.list_user_recurring_transactions(
            user_id=current_user.id,
            budget_id=budget_id,
            is_active=is_active
        )
        
        return [RecurringTransactionResponse.from_orm(rt) for rt in recurring_transactions]
        
    except Exception as e:
        logging.error(f"Failed to retrieve recurring transactions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recurring transactions"
        )


@router.put("/recurring/{recurring_id}", response_model=RecurringTransactionResponse)
async def update_recurring_transaction(
    recurring_id: str,
    recurring_update: RecurringTransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update recurring transaction
    
    - **recurring_id**: Recurring transaction's unique identifier
    - **schedule**: Recurrence schedule (optional)
    - **amount**: Transaction amount (optional)
    - **currency**: Transaction currency (optional)
    - **type**: Transaction type (optional)
    - **category**: Transaction category (optional)
    - **subcategory**: Transaction subcategory (optional)
    - **description**: Transaction description (optional)
    - **is_active**: Active status (optional)
    - **next_execution**: Next execution date (optional)
    
    Returns updated recurring transaction information
    """
    try:
        
        transaction_service = TransactionService(db)
        recurring_transaction = await transaction_service.update_user_recurring_transaction(
            recurring_id,
            recurring_update,
            current_user.id
        )
        
        if not recurring_transaction:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to update recurring transaction"
            )
        
        return RecurringTransactionResponse.from_orm(recurring_transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to update recurring transaction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recurring transaction"
        )

@router.delete("/recurring/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_transaction(
    recurring_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete recurring transaction
    
    - **recurring_id**: Recurring transaction's unique identifier
    
    Permanently deletes the recurring transaction
    """
    try:
        transaction_service = TransactionService(db)
        success = await transaction_service.delete_user_recurring_transaction(
            recurring_id,
            current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to delete recurring transaction"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to delete recurring transaction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recurring transaction"
        )
        
        
        
@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction by ID
    
    - **transaction_id**: Transaction's unique identifier
    
    Returns transaction information
    """
    try:
        transaction_service = TransactionService(db)
        transaction = await transaction_service.get_user_transaction(
            transaction_id,
            current_user.id
        )
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return TransactionResponse.from_orm(transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to retrieve transaction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction"
        )

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update transaction information
    
    - **transaction_id**: Transaction's unique identifier
    - **amount**: Transaction amount (optional)
    - **currency**: Transaction currency (optional)
    - **type**: Transaction type (optional)
    - **category**: Transaction category (optional)
    - **subcategory**: Transaction subcategory (optional)
    - **description**: Transaction description (optional)
    - **exchange_rate**: Exchange rate (optional)
    - **date**: Transaction date (optional)
    - **details**: Additional metadata (optional)
    
    Returns updated transaction information
    """
    try:
        transaction_service = TransactionService(db)
        transaction = await transaction_service.update_user_transaction(
            transaction_id,
            transaction_update,
            current_user.id
        )
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return TransactionResponse.from_orm(transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update transaction"
        )

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete transaction (soft delete)
    
    - **transaction_id**: Transaction's unique identifier
    
    Marks transaction as deleted while preserving data for audit purposes
    """
    try:
        transaction_service = TransactionService(db)
        success = await transaction_service.delete_user_transaction(
            transaction_id,
            current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete transaction"
        )