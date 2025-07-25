#!/usr/bin/env python3
"""
Test script to demonstrate the budget admin deletion trigger functionality.
This script shows how the trigger automatically deletes a budget when the last admin is removed.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import User, Budget, UserBudget, UserRole
import uuid

def test_budget_admin_deletion_trigger():
    """Test the trigger that deletes budgets when the last admin is removed."""
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 Testing Budget Admin Deletion Trigger")
        print("=" * 50)
        
        # Create test user
        test_user = User(
            id=uuid.uuid4(),
            name="Test Admin User",
            email="test@example.com",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print(f"✅ Created test user: {test_user.name}")
        
        # Create test budget
        test_budget = Budget(
            id=uuid.uuid4(),
            name="Test Budget for Trigger",
            currency="USD"
        )
        db.add(test_budget)
        db.commit()
        print(f"✅ Created test budget: {test_budget.name}")
        
        # Create UserBudget with admin role
        user_budget = UserBudget(
            id=uuid.uuid4(),
            user_id=test_user.id,
            budget_id=test_budget.id,
            role=UserRole.ADMIN
        )
        db.add(user_budget)
        db.commit()
        print(f"✅ Created UserBudget with admin role")
        
        # Verify budget exists
        budget_count = db.execute(
            text("SELECT COUNT(*) FROM budgets WHERE id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        print(f"📊 Budgets before deletion: {budget_count}")
        
        # Delete the admin UserBudget (this should trigger budget deletion)
        print("\n🔥 Deleting the admin UserBudget...")
        db.delete(user_budget)
        db.commit()
        
        # Check if budget was automatically deleted by trigger
        budget_count_after = db.execute(
            text("SELECT COUNT(*) FROM budgets WHERE id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        print(f"📊 Budgets after deletion: {budget_count_after}")
        
        if budget_count_after == 0:
            print("🎉 SUCCESS: Trigger worked! Budget was automatically deleted when last admin was removed.")
        else:
            print("❌ FAILED: Budget still exists after admin removal.")
        
        # Cleanup test user
        db.delete(test_user)
        db.commit()
        print("🧹 Cleaned up test user")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        db.rollback()
    finally:
        db.close()

def test_trigger_with_multiple_admins():
    """Test that budget is NOT deleted when other admins exist."""
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("\n🧪 Testing Trigger with Multiple Admins")
        print("=" * 50)
        
        # Create test users
        admin1 = User(id=uuid.uuid4(), name="Admin 1", email="admin1@example.com", is_active=True)
        admin2 = User(id=uuid.uuid4(), name="Admin 2", email="admin2@example.com", is_active=True)
        db.add_all([admin1, admin2])
        db.commit()
        print("✅ Created two admin users")
        
        # Create test budget
        test_budget = Budget(id=uuid.uuid4(), name="Multi-Admin Budget", currency="USD")
        db.add(test_budget)
        db.commit()
        print("✅ Created test budget")
        
        # Create UserBudgets with admin roles for both users
        user_budget1 = UserBudget(id=uuid.uuid4(), user_id=admin1.id, budget_id=test_budget.id, role=UserRole.ADMIN)
        user_budget2 = UserBudget(id=uuid.uuid4(), user_id=admin2.id, budget_id=test_budget.id, role=UserRole.ADMIN)
        db.add_all([user_budget1, user_budget2])
        db.commit()
        print("✅ Created UserBudgets for both admins")
        
        # Delete one admin (budget should remain)
        print("\n🔥 Deleting one admin UserBudget...")
        db.delete(user_budget1)
        db.commit()
        
        # Check if budget still exists
        budget_count = db.execute(
            text("SELECT COUNT(*) FROM budgets WHERE id = :budget_id"),
            {"budget_id": str(test_budget.id)}
        ).scalar()
        
        if budget_count == 1:
            print("🎉 SUCCESS: Budget preserved when other admins exist.")
        else:
            print("❌ FAILED: Budget was deleted even though other admins exist.")
        
        # Cleanup
        db.delete(user_budget2)
        db.delete(admin1)
        db.delete(admin2)
        db.commit()
        print("🧹 Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_budget_admin_deletion_trigger()
    test_trigger_with_multiple_admins()