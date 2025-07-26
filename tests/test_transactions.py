import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta

def test_create_transaction(client, test_user, test_budget, auth_headers):
    """Test creating a new transaction."""
    response = client.post(
        "/api/v1/transactions/",
        headers=auth_headers,
        json={
            "budget_id": str(test_budget.id),
            "amount": 100.50,
            "currency": "USD",
            "type": "expense",
            "category": "Food & Dining",
            "subcategory": "Restaurant",
            "description": "Lunch at restaurant",
            "date": str(date.today()),
            "details": {"location": "Downtown"}
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 100.50
    assert data["type"] == "expense"
    assert data["category"] == "Food & Dining"
    assert data["description"] == "Lunch at restaurant"

def test_list_transactions(client, test_user, test_budget, auth_headers, db_session):
    """Test listing transactions with pagination."""
    # Create a test transaction first
    from app.models.models import Transaction, TransactionType
    
    transaction = Transaction(
        budget_id=test_budget.id,
        user_id=test_user.id,
        amount=50.00,
        type=TransactionType.INCOME,
        category="Salary",
        date=date.today()
    )
    db_session.add(transaction)
    db_session.commit()
    
    response = client.get("/api/v1/transactions/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data

def test_get_budget_categories(client, test_user, test_budget, auth_headers, db_session):
    """Test getting categories grouped by transaction type for a budget."""
    from app.models.models import Transaction, TransactionType
    
    # Create test transactions with different types and categories
    transactions = [
        Transaction(
            budget_id=test_budget.id,
            user_id=test_user.id,
            amount=100.00,
            type=TransactionType.EXPENSE,
            category="Food",
            date=date.today()
        ),
        Transaction(
            budget_id=test_budget.id,
            user_id=test_user.id,
            amount=50.00,
            type=TransactionType.EXPENSE,
            category="Transport",
            date=date.today()
        ),
        Transaction(
            budget_id=test_budget.id,
            user_id=test_user.id,
            amount=2000.00,
            type=TransactionType.INCOME,
            category="Salary",
            date=date.today()
        ),
        Transaction(
            budget_id=test_budget.id,
            user_id=test_user.id,
            amount=500.00,
            type=TransactionType.INVESTMENT,
            category="Stocks",
            date=date.today()
        )
    ]
    
    for transaction in transactions:
        db_session.add(transaction)
    db_session.commit()
    
    response = client.get(
        f"/api/v1/transactions/budget/{test_budget.id}/categories",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    
    categories = data["categories"]
    assert "expense" in categories
    assert "income" in categories
    assert "investment" in categories
    
    # Check that categories are properly grouped
    assert "Food" in categories["expense"]
    assert "Transport" in categories["expense"]
    assert "Salary" in categories["income"]
    assert "Stocks" in categories["investment"]
    assert "items" in data
    assert len(data["items"]) >= 1

def test_list_transactions_with_filters(client, test_user, test_budget, auth_headers, db_session):
    """Test listing transactions with filters."""
    # Create test transactions
    from app.models.models import Transaction, TransactionType
    
    transaction1 = Transaction(
        budget_id=test_budget.id,
        user_id=test_user.id,
        amount=100.00,
        type=TransactionType.EXPENSE,
        category="Food & Dining",
        date=date.today()
    )
    transaction2 = Transaction(
        budget_id=test_budget.id,
        user_id=test_user.id,
        amount=2000.00,
        type=TransactionType.INCOME,
        category="Salary",
        date=date.today()
    )
    db_session.add_all([transaction1, transaction2])
    db_session.commit()
    
    # Filter by type
    response = client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
        params={"transaction_type": "expense"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert all(item["type"] == "expense" for item in data["items"])

def test_get_transaction(client, test_user, test_budget, auth_headers, db_session):
    """Test getting specific transaction."""
    from app.models.models import Transaction, TransactionType
    
    transaction = Transaction(
        budget_id=test_budget.id,
        user_id=test_user.id,
        amount=75.25,
        type=TransactionType.EXPENSE,
        category="Transportation",
        date=date.today()
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    
    response = client.get(
        f"/api/v1/transactions/{transaction.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(transaction.id)
    assert data["amount"] == 75.25

def test_update_transaction(client, test_user, test_budget, auth_headers, db_session):
    """Test updating transaction."""
    from app.models.models import Transaction, TransactionType
    
    transaction = Transaction(
        budget_id=test_budget.id,
        user_id=test_user.id,
        amount=50.00,
        type=TransactionType.EXPENSE,
        category="Shopping",
        date=date.today()
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    
    response = client.put(
        f"/api/v1/transactions/{transaction.id}",
        headers=auth_headers,
        json={
            "amount": 60.00,
            "description": "Updated description"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 60.00
    assert data["description"] == "Updated description"

def test_delete_transaction(client, test_user, test_budget, auth_headers, db_session):
    """Test deleting transaction."""
    from app.models.models import Transaction, TransactionType
    
    transaction = Transaction(
        budget_id=test_budget.id,
        user_id=test_user.id,
        amount=25.00,
        type=TransactionType.EXPENSE,
        category="Entertainment",
        date=date.today()
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    
    response = client.delete(
        f"/api/v1/transactions/{transaction.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204

def test_create_recurring_transaction(client, test_user, test_budget, auth_headers):
    """Test creating recurring transaction."""
    next_month = date.today() + timedelta(days=30)
    
    response = client.post(
        "/api/v1/transactions/recurring",
        headers=auth_headers,
        json={
            "budget_id": str(test_budget.id),
            "schedule": "monthly",
            "recurring_type": "automatic",
            "amount": 2500.00,
            "currency": "USD",
            "type": "income",
            "category": "Salary",
            "description": "Monthly salary",
            "next_execution": str(next_month)
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["schedule"] == "monthly"
    assert data["amount"] == 2500.00
    assert data["type"] == "income"

def test_list_recurring_transactions(client, test_user, test_budget, auth_headers, db_session):
    """Test listing recurring transactions."""
    from app.models.models import RecurringTransaction, TransactionType, RecurringType
    
    recurring = RecurringTransaction(
        budget_id=test_budget.id,
        user_id=test_user.id,
        schedule="weekly",
        recurring_type=RecurringType.AUTOMATIC,
        amount=100.00,
        type=TransactionType.EXPENSE,
        category="Groceries",
        next_execution=date.today() + timedelta(days=7)
    )
    db_session.add(recurring)
    db_session.commit()
    
    response = client.get("/api/v1/transactions/recurring", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["schedule"] == "weekly"

def test_access_denied_to_other_budget_transaction(client, test_user, auth_headers):
    """Test access denied to transaction in budget user doesn't have access to."""
    fake_transaction_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"/api/v1/transactions/{fake_transaction_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404