from typing import Dict, List, Any
from datetime import datetime, timedelta
import uuid

class MockSession:
    """Mock database session for when database is unavailable"""
    
    def __init__(self):
        self.users = self._generate_mock_users()
        self.budgets = self._generate_mock_budgets()
        self.transactions = self._generate_mock_transactions()
        self.user_budgets = self._generate_mock_user_budgets()
    
    def _generate_mock_users(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "auth_method": "email",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1234567891",
                "auth_method": "google",
                "created_at": datetime.utcnow()
            }
        ]
    
    def _generate_mock_budgets(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "Home Budget",
                "currency": "USD",
                "status": "active",
                "created_at": datetime.utcnow(),
                "archived_at": None
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Office Project",
                "currency": "USD",
                "status": "active",
                "created_at": datetime.utcnow(),
                "archived_at": None
            }
        ]
    
    def _generate_mock_transactions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": str(uuid.uuid4()),
                "budget_id": self.budgets[0]["id"],
                "user_id": self.users[0]["id"],
                "amount": 2500.00,
                "currency": "USD",
                "type": "income",
                "category": "salary",
                "subcategory": "monthly",
                "description": "Monthly salary",
                "exchange_rate": 1.0,
                "date": datetime.utcnow().date(),
                "details": {"source": "company"},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "deleted_at": None
            }
        ]
    
    def _generate_mock_user_budgets(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": str(uuid.uuid4()),
                "user_id": self.users[0]["id"],
                "budget_id": self.budgets[0]["id"],
                "role": "admin"
            }
        ]
    
    def query(self, model):
        """Mock query method"""
        if hasattr(model, '__tablename__'):
            table_name = model.__tablename__
            if table_name == 'users':
                return MockQuery(self.users)
            elif table_name == 'budgets':
                return MockQuery(self.budgets)
            elif table_name == 'transactions':
                return MockQuery(self.transactions)
            elif table_name == 'user_budgets':
                return MockQuery(self.user_budgets)
        return MockQuery([])
    
    def add(self, instance):
        """Mock add method"""
        pass
    
    def commit(self):
        """Mock commit method"""
        pass
    
    def close(self):
        """Mock close method"""
        pass

class MockQuery:
    """Mock query object"""
    
    def __init__(self, data):
        self.data = data
    
    def filter(self, *args):
        return self
    
    def offset(self, offset):
        self.data = self.data[offset:]
        return self
    
    def limit(self, limit):
        self.data = self.data[:limit]
        return self
    
    def all(self):
        return self.data
    
    def first(self):
        return self.data[0] if self.data else None
    
    def count(self):
        return len(self.data)

def get_mock_session():
    """Get mock database session"""
    return MockSession()