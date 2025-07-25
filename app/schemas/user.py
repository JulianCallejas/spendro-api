from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union
from datetime import datetime
from app.models.models import AuthMethod, SyncStatus, User

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')

class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=8)
    auth_method: AuthMethod = AuthMethod.EMAIL
    google_id: Optional[str] = None
    biometric_hash: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    auth_method: AuthMethod
    
    class Config:
        from_attributes = True

class PublicUserResponse(UserBase):
    id: str
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[PublicUserResponse]
    

def user_to_dict(user: User) -> dict:
    try:
        return dict({
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "auth_method": user.auth_method
        })
    except Exception as e:
        return {}
    
def user_from_dict(user_dict: dict) -> Union[UserResponse, None]:
    try:
        return User(**user_dict)
    except Exception as e:
        return None