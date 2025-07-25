from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.core.database import engine
from app.models import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Spendro - Collaborative Expense Tracker API",
    description="""
    A comprehensive expense tracking API for managing personal and shared budgets with real-time collaboration features.
    
    ## Authentication
    
    This API uses JWT Bearer token authentication. To authenticate:
    
    1. **Register** a new account or **login** with existing credentials via `/api/v1/auth/register` or `/api/v1/auth/login`
    2. Copy the `access_token` from the response
    3. Click the **Authorize** button below and enter your token (without "Bearer" prefix)
    4. You can now access protected endpoints
    
    ## Supported Authentication Methods
    - Email/Password authentication
    - Google OAuth integration  
    - Biometric authentication (fingerprint)
    
    ## Key Features
    - Multi-user collaborative budgets with role-based access control
    - Real-time synchronization with offline-first design
    - Advanced transaction management and categorization
    - Audio transcription for expense entry via Whisper AI
    - Rate limiting and caching for optimal performance
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True
    }
)

# FastAPI will automatically detect security schemes from dependencies
# No need for custom OpenAPI configuration

# Add custom middleware (in reverse order of execution)
app.add_middleware(AuthMiddleware)  # Executes first
app.add_middleware(RateLimitMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

@app.get("/")
async def root():
    return {"message": "Collaborative Expense Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )