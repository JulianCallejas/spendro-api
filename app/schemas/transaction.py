from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from app.models.models import TransactionType, SyncStatus
import uuid

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field("USD", pattern=r'^[A-Z]{3}$')
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    exchange_rate: float = Field(1.0, gt=0)
    date: date
    details: Optional[Dict[str, Any]] = None

class TransactionCreate(TransactionBase):
    budget_id: str

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, pattern=r'^[A-Z]{3}$')
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    exchange_rate: Optional[float] = Field(None, gt=0)
    date: Union[str, date, None] = None
    details: Optional[Dict[str, Any]] = None
    
    

class TransactionResponse(TransactionBase):
    id: str
    budget_id: str
    user_id: str
    
    @field_validator('id', 'budget_id', 'user_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, value):
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
    
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    sync_status: SyncStatus

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[TransactionResponse]

class RecurringTransactionBase(BaseModel):
    schedule: str = Field(..., pattern=r'^(daily|weekly|monthly|yearly)$')
    amount: float = Field(..., gt=0)
    currency: str = Field("USD", pattern=r'^[A-Z]{3}$')
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    next_execution: date

class RecurringTransactionCreate(RecurringTransactionBase):
    budget_id: str

class RecurringTransactionUpdate(BaseModel):
    schedule: Optional[str] = Field(None, pattern=r'^(daily|weekly|monthly|yearly)$')
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, pattern=r'^[A-Z]{3}$')
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    next_execution: Optional[date] = None

class RecurringTransactionResponse(RecurringTransactionBase):
    id: str
    budget_id: str
    user_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    sync_status: SyncStatus
    
    @field_validator('id', 'budget_id', 'user_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, value):
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    class Config:
        from_attributes = True
        
        
def transaction_to_dict(transaction: TransactionResponse) -> Dict[str, Any]:
    return dict(**transaction)