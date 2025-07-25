from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class SyncPushRequest(BaseModel):
    users: Optional[List[Dict[str, Any]]] = []
    budgets: Optional[List[Dict[str, Any]]] = []
    transactions: Optional[List[Dict[str, Any]]] = []
    recurring_transactions: Optional[List[Dict[str, Any]]] = []

class SyncPullResponse(BaseModel):
    users: List[Dict[str, Any]]
    budgets: List[Dict[str, Any]]
    transactions: List[Dict[str, Any]]
    recurring_transactions: List[Dict[str, Any]]
    timestamp: datetime

class SyncConflictResponse(BaseModel):
    conflicts: List[Dict[str, Any]]
    resolved: bool = False