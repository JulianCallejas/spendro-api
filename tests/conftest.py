import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.models import User, Budget, UserBudget, UserRole
from datetime import timedelta

# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from app.core.security import get_password_hash
    
    user = User(
        name="Test User",
        email="test@example.com",
        phone="+1234567890",
        password_hash=get_password_hash("testpassword123"),
        auth_method="email"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_budget(db_session, test_user):
    """Create a test budget."""
    budget = Budget(
        name="Test Budget",
        currency="USD"
    )
    db_session.add(budget)
    db_session.flush()
    
    # Add user as admin
    user_budget = UserBudget(
        user_id=test_user.id,
        budget_id=budget.id,
        role=UserRole.ADMIN
    )
    db_session.add(user_budget)
    db_session.commit()
    db_session.refresh(budget)
    return budget

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    access_token = create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "name": test_user.name,
            "roles": ["user"]
        },
        expires_delta=timedelta(hours=1)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def mock_cache():
    """Mock cache for testing."""
    class MockCache:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value):
            self.data[key] = value
            return True
        
        def delete(self, key):
            return self.data.pop(key, None) is not None
        
        def clear(self):
            self.data.clear()
    
    return MockCache()