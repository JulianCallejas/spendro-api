from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class AuthMethod(str, enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    GOOGLE = "google"
    BIOMETRIC = "biometric"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    INVESTMENT = "investment"

class BudgetStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class SyncStatus(str, enum.Enum):
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"

class RecurringType(str, enum.Enum):
    AUTOMATIC = "automatic"
    REMINDER = "reminder"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    auth_method = Column(SQLEnum(AuthMethod), nullable=False, default=AuthMethod.EMAIL)
    google_id = Column(String(255), unique=True, nullable=True)
    biometric_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.SYNCED)
    
    # Relationships with cascade deletion
    user_budgets = relationship("UserBudget", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    recurring_transactions = relationship("RecurringTransaction", back_populates="user", cascade="all, delete-orphan")

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(SQLEnum(BudgetStatus), nullable=False, default=BudgetStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)
    sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.SYNCED)
    
    # Relationships with cascade deletion
    user_budgets = relationship("UserBudget", back_populates="budget", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="budget", cascade="all, delete-orphan")
    recurring_transactions = relationship("RecurringTransaction", back_populates="budget", cascade="all, delete-orphan")

class UserBudget(Base):
    __tablename__ = "user_budgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_budgets")
    budget = relationship("Budget", back_populates="user_budgets")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    type = Column(SQLEnum(TransactionType), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    exchange_rate = Column(Float, nullable=False, default=1.0)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.SYNCED)
    
    # Relationships
    budget = relationship("Budget", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    schedule = Column(String(50), nullable=False)  # daily, weekly, monthly, yearly
    recurring_type = Column(SQLEnum(RecurringType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    type = Column(SQLEnum(TransactionType), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    next_execution = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.SYNCED)
    
    # Relationships
    budget = relationship("Budget", back_populates="recurring_transactions")
    user = relationship("User", back_populates="recurring_transactions")

class TransactionCategory(Base):
    __tablename__ = "transaction_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(SQLEnum(TransactionType), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships with cascade deletion
    subcategories = relationship("TransactionSubcategory", back_populates="category", cascade="all, delete-orphan")

class TransactionSubcategory(Base):
    __tablename__ = "transaction_subcategories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("transaction_categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("TransactionCategory", back_populates="subcategories")