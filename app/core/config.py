from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # External services
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    
    # Application settings
    ENVIRONMENT: str
    DEBUG: bool
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int
        
    # Cache settings
    REDIS_HOST: str
    REDIS_DB: Optional[int]
    REDIS_PASSWORD: str
    REDIS_PORT: int
    REDIS_URL: str
    CACHE_TTL_MINUTES: int
    CACHE_MAX_SIZE_MB: int
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int
    MAX_PAGE_SIZE: int
    
    # Transcription settings
    WHISPER_MODEL: str
    MAX_AUDIO_DURATION_SECONDS: int
    MAX_AUDIO_FILE_SIZE_MB: int
    TRANSCRIPTION_LANGUAGE: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file

settings = Settings()