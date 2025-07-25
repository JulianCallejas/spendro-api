#!/usr/bin/env python3
"""
Test script to verify cascade deletion functionality.
This script demonstrates how cascade deletion works across all related tables.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import (
    User, Budget, UserBudget, Transaction, RecurringTransaction, 
    TransactionCategory, TransactionSubcategory, UserRole, TransactionType
)
import uuid
from datetime import datetime, date

def test_user_cascade_deletion():
    """Test that deleting a user cascades to all related records."""
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 Testing User Cascade Deletion")
        print("=" * 50)
        
        # Create test user
        test_user = User(
            id=uuid.uuid4(),
            name="Test User for Cascade",
            email="cascade@example.com",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print(f"✅ Created user: {test_user.name}")
        
        # Create test budget
        test_budget = Budget(
            id=uuid.uuid4(),
            name="Test Budget for Cascade",
            currency="USD"
        )
        db.add(test_budget)
        db.commit()
        print(f"✅ Created budget: {test_budget.name}")
        
        # Create UserBudget
        user_budget = UserBudget(
            id=uuid.uuid4(),
            user_id=test_user.id,
            budget_id=test_budget.id,
            role=UserRole.ADMIN
        )
        db.add(user_budget)
        db.commit()
        print("✅ Created UserBudget relationship")
        
        # Create Transaction
        transaction = Transaction(
            id=uuid.uuid4(),
            budget_id=test_budget.id,
            user_id=test_user.id,
            amount=100.0,
            type=TransactionType.EXPENSE,
            category="Food",
            date=date.today()
        )
        db.add(transaction)
        db.commit()
        print("✅ Created Transaction")
        
        # Create RecurringTransaction
        recurring_transaction = RecurringTransaction(
            id=uuid.uuid4(),
            budget_id=test_budget.id,
            user_id=test_user.id,
            schedule="monthly",
            amount=50.0,
            type=TransactionType.EXPENSE,
            category="Utilities",
            next_execution=date.today()
        )
        db.add(recurring_transaction)
        db.commit()
        print("✅ Created RecurringTransaction")
        
        # Count records before deletion
        user_budget_count = db.execute(
            text("SELECT COUNT(*) FROM user_budgets WHERE user_id = :user_id"),
            {"user_id": str(test_user.id)}
        ).scalar()
        
        transaction_count = db.execute(
            text("SELECT COUNT(*) FROM transactions WHERE user_id = :user_id"),
            {"user_id": str(test_user.id)}
        ).scalar()
        
        recurring_count = db.execute(
            text("SELECT COUNT(*) FROM recurring_transactions WHERE user_id = :user_id"),
            {"user_id": str(test_user.id)}
        ).scalar()
        
        print(f"\n📊 Before deletion:")
        print(f"   UserBudgets: {user_budget_count}")
        print(f"   Transactions: {transaction_count}")
        print(f"   RecurringTransactions: {recurring_count}")
        
        # Delete the user (should cascade to all related records)
        print("\n🔥 Deleting user...")
        db.delete(test_user)
        db.commit()
        
        # Count records after deletion
        user_budget_count_after = db.execute(
            text("SELECT COUNT(*) FROM user_budgets WHERE user_id = :user_id"),
            {"user_id": str(test_user.id)}
        ).scalar()
        
        transaction_count_after = db.execute(
            text("SELECT COUNT(*) FROM transactions WHERE user_id = :user_id"),
            {"user_id": str(test_user.id)}
        ).scalar()
        
        recurring_count_after = db.execute(
            text("SELECT COUNT(*) FROM recurring_transactions WHERE user_id = :user_id"),
            {"user_id": str(test_user.id)}
        ).scalar()
        
        print(f"\n📊 After deletion:")
        print(f"   UserBudgets: {user_budget_count_after}")
        print(f"   Transactions: {transaction_count_after}")
        print(f"   RecurringTransactions: {recurring_count_after}")
        
        if (user_budget_count_after == 0 and 
            transaction_count_after == 0 and 
            recurring_count_after == 0):
            print("🎉 SUCCESS: User cascade deletion worked perfectly!")
        else:
            print("❌ FAILED: Some related records were not deleted.")
        
        # Cleanup remaining budget
        db.delete(test_budget)
        db.commit()
        print("🧹 Cleaned up test budget")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        db.rollback()
    finally:
        db.close()

def test_budget_cascade_deletion():
    """Test that deleting a budget cascades to all related records."""
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("\n🧪 Testing Budget Cascade Deletion")
        print("=" * 50)
        
        # Create test user
        test_user = User(
            id=uuid.uuid4(),
            name="Test User for Budget Cascade",
            email="budget_cascade@example.com",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print(f"✅ Created user: {test_user.name}")
        
        # Create test budget
        test_budget = Budget(
            id=uuid.uuid4(),
            name="Budget for Cascade Test",
            currency="USD"
        )
        db.add(test_budget)
        db.commit()
        print(f"✅ Created budget: {test_budget.name}")
        
        # Create related records
        user_budget = UserBudget(
            id=uuid.uuid4(),
            user_id=test_user.id,
            budget_id=test_budget.id,
            role=UserRole.EDITOR
        )
        
        transaction = Transaction(
            id=uuid.uuid4(),
            budget_id=test_budget.id,
            user_id=test_user.id,
            amount=200.0,
            type=TransactionType.INCOME,
            category="Salary",
            date=date.today()
        )
        
        recurring_transaction = RecurringTransaction(
            id=uuid.uuid4(),
            budget_id=test_budget.id,
            user_id=test_user.id,
            schedule="weekly",
            amount=25.0,
            type=TransactionType.EXPENSE,
            category="Coffee",
            next_execution=date.today()
        )
        
        db.add_all([user_budget, transaction, recurring_transaction])
        db.commit()
        print("✅ Created related records")
        
        # Count records before deletion
        user_budget_count = db.execute(
            text("SELECT COUNT(*) FROM user_budgets WHERE budget_id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        
        transaction_count = db.execute(
            text("SELECT COUNT(*) FROM transactions WHERE budget_id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        
        recurring_count = db.execute(
            text("SELECT COUNT(*) FROM recurring_transactions WHERE budget_id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        
        print(f"\n📊 Before budget deletion:")
        print(f"   UserBudgets: {user_budget_count}")
        print(f"   Transactions: {transaction_count}")
        print(f"   RecurringTransactions: {recurring_count}")
        
        # Delete the budget (should cascade to all related records)
        print("\n🔥 Deleting budget...")
        db.delete(test_budget)
        db.commit()
        
        # Count records after deletion
        user_budget_count_after = db.execute(
            text("SELECT COUNT(*) FROM user_budgets WHERE budget_id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        
        transaction_count_after = db.execute(
            text("SELECT COUNT(*) FROM transactions WHERE budget_id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        
        recurring_count_after = db.execute(
            text("SELECT COUNT(*) FROM recurring_transactions WHERE budget_id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        
        print(f"\n📊 After budget deletion:")
        print(f"   UserBudgets: {user_budget_count_after}")
        print(f"   Transactions: {transaction_count_after}")
        print(f"   RecurringTransactions: {recurring_count_after}")
        
        if (user_budget_count_after == 0 and 
            transaction_count_after == 0 and 
            recurring_count_after == 0):
            print("🎉 SUCCESS: Budget cascade deletion worked perfectly!")
        else:
            print("❌ FAILED: Some related records were not deleted.")
        
        # Cleanup user
        db.delete(test_user)
        db.commit()
        print("🧹 Cleaned up test user")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        db.rollback()
    finally:
        db.close()

def test_category_cascade_deletion():
    """Test that deleting a category cascades to subcategories."""
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("\n🧪 Testing Category Cascade Deletion")
        print("=" * 50)
        
        # Create test category
        test_category = TransactionCategory(
            id=uuid.uuid4(),
            name="Test Category for Cascade",
            type=TransactionType.EXPENSE
        )
        db.add(test_category)
        db.commit()
        print(f"✅ Created category: {test_category.name}")
        
        # Create subcategories
        subcategory1 = TransactionSubcategory(
            id=uuid.uuid4(),
            category_id=test_category.id,
            name="Subcategory 1"
        )
        
        subcategory2 = TransactionSubcategory(
            id=uuid.uuid4(),
            category_id=test_category.id,
            name="Subcategory 2"
        )
        
        db.add_all([subcategory1, subcategory2])
        db.commit()
        print("✅ Created 2 subcategories")
        
        # Count subcategories before deletion
        subcategory_count = db.execute(
            text("SELECT COUNT(*) FROM transaction_subcategories WHERE category_id = :category_id"),
            {"category_id": str(test_category.id)}
        ).scalar()
        
        print(f"\n📊 Before category deletion:")
        print(f"   Subcategories: {subcategory_count}")
        
        # Delete the category (should cascade to subcategories)
        print("\n🔥 Deleting category...")
        db.delete(test_category)
        db.commit()
        
        # Count subcategories after deletion
        subcategory_count_after = db.execute(
            text("SELECT COUNT(*) FROM transaction_subcategories WHERE category_id = :category_id"),
            {"category_id": str(test_category.id)}
        ).scalar()
        
        print(f"\n📊 After category deletion:")
        print(f"   Subcategories: {subcategory_count_after}")
        
        if subcategory_count_after == 0:
            print("🎉 SUCCESS: Category cascade deletion worked perfectly!")
        else:
            print("❌ FAILED: Subcategories were not deleted.")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_user_cascade_deletion()
    test_budget_cascade_deletion()
    test_category_cascade_deletion()
    print("\n🎯 All cascade deletion tests completed!")