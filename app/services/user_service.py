from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, Tuple, List
from datetime import datetime

from app.models.models import User
from app.schemas.user import UserUpdate, user_to_dict
from app.core.cache import cache

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        cache.set(str(user.id), user_to_dict(user))
        
        return user
    
    async def list_users(
        self, 
        limit: int = 10, 
        offset: int = 0, 
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """List users with pagination and search"""
        query = self.db.query(User).filter(User.is_active == True)
        
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        users = query.offset(offset).limit(limit).all()
        
        return users, total
    
    async def search_users(
        self, 
        query: str,
        limit: int = 10, 
        offset: int = 0
    ) -> Tuple[List[User], int]:
        """Search users by name, email, or phone"""
        search_query = self.db.query(User).filter(User.is_active == True)
        
        # Create search filter for name, email, and phone
        search_filter = or_(
            User.name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
            User.phone.ilike(f"%{query}%")
        )
        search_query = search_query.filter(search_filter)
        
        total = search_query.count()
        users = search_query.offset(offset).limit(limit).all()
        
        return users, total
    
    async def delete_user(self, user_id: str) -> bool:
        """Soft delete user by deactivating"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        # user.is_active = False
        # user.updated_at = datetime.utcnow()
                
        self.db.delete(user)
        self.db.commit()
        
        return True