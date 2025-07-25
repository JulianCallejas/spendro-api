from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    # phone: Optional[str] = Field(None, regex=r'^\+?1?\d{9,15}$')
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    password: str = Field(..., min_length=1)

class GoogleAuthRequest(BaseModel):
    google_token: str

class BiometricAuthRequest(BaseModel):
    biometric_data: str
    user_identifier: str  # email or phone

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)