from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse, 
    GoogleAuthRequest, BiometricAuthRequest
)
from app.schemas.user import user_to_dict
from app.core.cache import SingletonCache, get_cache
from app.models.models import User, AuthMethod
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
    cache: SingletonCache = Depends(get_cache)
):
    """
    Register a new user with email/phone and password
    
    - **name**: User's full name
    - **email**: User's email address (optional if phone provided)
    - **phone**: User's phone number (optional if email provided)
    - **password**: User's password (minimum 8 characters)
    
    Returns JWT access token and user information
    """
    try:
        auth_service = AuthService(db)
        
        # Check if user already exists
        existing_user = auth_service.get_user_by_email_or_phone(
            user_data.email, user_data.phone
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or phone already exists"
            )
        
        # Create new user
        user = await auth_service.create_user(user_data)
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "phone": user.phone,
                "name": user.name,
                "roles": ["user"]
            },
            expires_delta=access_token_expires
        )
        
        new_user = user_to_dict(user)
        
        cache.set(str(user.id), new_user)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=new_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
    cache: SingletonCache = Depends(get_cache)
):
    """
    Login with email/phone and password
    
    - **email**: User's email address (optional if phone provided)
    - **phone**: User's phone number (optional if email provided)  
    - **password**: User's password
    
    Returns JWT access token and user information
    """
    try:
        auth_service = AuthService(db)
        
        # Authenticate user
        user = await auth_service.authenticate_user(
            credentials.email, credentials.phone, credentials.password
        )
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "phone": user.phone,
                "name": user.name,
                "roles": ["user"]
            },
            expires_delta=access_token_expires
        )
        
        logged_user = user_to_dict(user)
        
        cache.set(str(user.id), logged_user)
                
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=logged_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/google", response_model=TokenResponse)
async def google_auth(
    google_data: GoogleAuthRequest,
    db: Session = Depends(get_db),
    cache: SingletonCache = Depends(get_cache)
):
    """
    Authenticate with Google OAuth token
    
    - **google_token**: Google OAuth access token
    
    Returns JWT access token and user information
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_google_user(google_data.google_token)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google authentication failed"
            )
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "name": user.name,
                "roles": ["user"]
            },
            expires_delta=access_token_expires
        )
        
        logged_user =user_to_dict(user)
        
        logged_user = dict({
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "auth_method": user.auth_method.value
        })
        
        cache.set(str(user.id), logged_user)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=logged_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Google auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed"
        )

@router.post("/biometric", response_model=TokenResponse)
async def biometric_auth(
    biometric_data: BiometricAuthRequest,
    db: Session = Depends(get_db),
    cache: SingletonCache = Depends(get_cache)
):
    """
    Authenticate with biometric data (fingerprint)
    
    - **biometric_data**: Encrypted biometric data
    - **user_identifier**: User's email or phone number
    
    Returns JWT access token and user information
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_biometric_user(
            biometric_data.biometric_data,
            biometric_data.user_identifier
        )
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Biometric authentication failed"
            )
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "phone": user.phone,
                "name": user.name,
                "roles": ["user"]
            },
            expires_delta=access_token_expires
        )
        
        logged_user = user_to_dict(user)
        
        cache.set(str(user.id), logged_user)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=logged_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Biometric auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Biometric authentication failed"
        )