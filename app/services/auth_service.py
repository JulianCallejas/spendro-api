from sqlalchemy.orm import Session
from typing import Optional
import hashlib
import logging

from app.core.security import verify_password, get_password_hash
from app.models.models import User, AuthMethod
from app.schemas.auth import RegisterRequest

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_data: RegisterRequest) -> User:
        """Create a new user"""
        password_hash = get_password_hash(user_data.password) if user_data.password else None
        
        user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=password_hash,
            auth_method=AuthMethod.EMAIL if user_data.email else AuthMethod.PHONE
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, email: Optional[str], phone: Optional[str], password: str) -> Optional[User]:
        """Authenticate user with email/phone and password"""
        user = self.get_user_by_email_or_phone(email, phone)
        
        if not user or not user.password_hash:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def authenticate_google_user(self, google_token: str) -> Optional[User]:
        """Authenticate user with Google OAuth token"""
        # In a real implementation, you would verify the Google token
        # and extract user information from Google's API
        # For now, we'll return None to indicate authentication failure
        logging.warning("Google authentication not fully implemented")
        return None
    
    async def authenticate_biometric_user(self, biometric_data: str, user_identifier: str) -> Optional[User]:
        """Authenticate user with biometric data"""
        user = self.get_user_by_email_or_phone(
            user_identifier if "@" in user_identifier else None,
            user_identifier if "@" not in user_identifier else None
        )
        
        if not user or not user.biometric_hash:
            return None
        
        # Hash the biometric data and compare
        biometric_hash = hashlib.sha256(biometric_data.encode()).hexdigest()
        
        if biometric_hash != user.biometric_hash:
            return None
        
        return user
    
    def get_user_by_email_or_phone(self, email: Optional[str], phone: Optional[str]) -> Optional[User]:
        """Get user by email or phone"""
        if email:
            return self.db.query(User).filter(User.email == email).first()
        elif phone:
            return self.db.query(User).filter(User.phone == phone).first()
        return None