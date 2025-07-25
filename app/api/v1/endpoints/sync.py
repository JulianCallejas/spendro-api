from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User
from app.schemas.sync import SyncPushRequest, SyncPullResponse, SyncConflictResponse
from app.services.sync_service import SyncService

router = APIRouter()

@router.post("/push", response_model=dict)
async def sync_push(
    sync_data: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Push local changes to server
    
    - **users**: Updated user data (optional)
    - **budgets**: Updated budget data (optional)
    - **transactions**: Updated transaction data (optional)
    - **recurring_transactions**: Updated recurring transaction data (optional)
    
    Returns sync results with any conflicts
    """
    try:
        sync_service = SyncService(db)
        result = await sync_service.push_changes(
            user_id=current_user.id,
            sync_data=sync_data
        )
        
        return {
            "status": "success",
            "processed": result["processed"],
            "conflicts": result["conflicts"],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync push failed: {str(e)}"
        )

@router.get("/pull", response_model=SyncPullResponse)
async def sync_pull(
    since: Optional[datetime] = Query(None, description="Pull changes since this timestamp"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pull updated entities from server since last sync
    
    - **since**: Timestamp to pull changes from (optional, defaults to all data)
    
    Returns all updated entities since the specified timestamp
    """
    try:
        sync_service = SyncService(db)
        result = await sync_service.pull_changes(
            user_id=current_user.id,
            since=since
        )
        
        return SyncPullResponse(
            users=result["users"],
            budgets=result["budgets"],
            transactions=result["transactions"],
            recurring_transactions=result["recurring_transactions"],
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync pull failed: {str(e)}"
        )

@router.get("/conflicts", response_model=SyncConflictResponse)
async def get_sync_conflicts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unresolved sync conflicts for current user
    
    Returns list of data conflicts that need manual resolution
    """
    try:
        sync_service = SyncService(db)
        conflicts = await sync_service.get_user_conflicts(current_user.id)
        
        return SyncConflictResponse(
            conflicts=conflicts,
            resolved=len(conflicts) == 0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conflicts: {str(e)}"
        )

@router.post("/conflicts/resolve", response_model=dict)
async def resolve_sync_conflicts(
    conflict_resolutions: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resolve sync conflicts with user choices
    
    - **conflict_resolutions**: Dictionary of conflict IDs and chosen resolutions
    
    Returns result of conflict resolution
    """
    try:
        sync_service = SyncService(db)
        result = await sync_service.resolve_conflicts(
            user_id=current_user.id,
            resolutions=conflict_resolutions
        )
        
        return {
            "status": "success",
            "resolved_count": result["resolved_count"],
            "remaining_conflicts": result["remaining_conflicts"],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conflict resolution failed: {str(e)}"
        )

@router.get("/status", response_model=dict)
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current sync status for user
    
    Returns sync statistics and status information
    """
    try:
        sync_service = SyncService(db)
        status_info = await sync_service.get_sync_status(current_user.id)
        
        return {
            "user_id": current_user.id,
            "last_sync": status_info["last_sync"],
            "pending_changes": status_info["pending_changes"],
            "conflicts_count": status_info["conflicts_count"],
            "sync_health": status_info["sync_health"],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync status: {str(e)}"
        )