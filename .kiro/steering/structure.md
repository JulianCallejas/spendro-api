# Project Structure & Architecture

## Directory Organization

```
app/
├── main.py                 # FastAPI application entry point
├── core/                   # Core configuration and utilities
│   ├── config.py          # Pydantic settings configuration
│   ├── database.py        # Database connection and session management
│   ├── security.py        # JWT authentication and password hashing
│   └── mock_data.py       # Mock data for development/testing
├── models/
│   └── models.py          # SQLAlchemy database models
├── schemas/               # Pydantic request/response schemas
│   ├── auth.py           # Authentication schemas
│   ├── user.py           # User-related schemas
│   ├── budget.py         # Budget schemas
│   ├── transaction.py    # Transaction schemas
│   └── sync.py           # Synchronization schemas
├── api/
│   └── v1/
│       ├── api.py        # Main API router
│       └── endpoints/    # Individual endpoint modules
├── services/             # Business logic layer
│   ├── auth_service.py
│   ├── user_service.py
│   ├── budget_service.py
│   ├── transaction_service.py
│   └── sync_service.py
└── middleware/           # Custom middleware
    ├── auth.py          # Authentication middleware
    ├── rate_limit.py    # Rate limiting
    └── cache.py         # Caching middleware
```

## Architecture Patterns

### Layered Architecture
- **API Layer** (`api/`): FastAPI routers and endpoint definitions
- **Service Layer** (`services/`): Business logic and data processing
- **Data Layer** (`models/`): SQLAlchemy ORM models
- **Schema Layer** (`schemas/`): Pydantic models for validation

### Configuration Management
- Centralized settings in `core/config.py` using Pydantic Settings
- Environment-specific configuration via `.env` files
- Type-safe configuration with validation

### Database Architecture
- SQLAlchemy 2.0 with declarative models
- Alembic for database migrations
- Connection pooling and session management in `core/database.py`

### Middleware Stack
- CORS middleware for cross-origin requests
- Custom rate limiting middleware
- Caching middleware for performance
- Authentication middleware for protected routes

## Code Organization Conventions

### File Naming
- Snake_case for Python files and directories
- Descriptive names reflecting functionality
- Service files suffixed with `_service.py`
- Test files prefixed with `test_`

### Import Organization
- Standard library imports first
- Third-party imports second
- Local application imports last
- Relative imports within modules

### Error Handling
- Global exception handler in `main.py`
- Consistent HTTP status codes
- Structured error responses with detail and error fields

### Testing Structure
- Test files mirror application structure
- Fixtures in `conftest.py` for common test setup
- Separate database session for testing
- Mock objects for external dependencies

## Key Architectural Decisions

### Authentication Flow
- JWT-based authentication with configurable expiration
- Multiple auth methods supported (email, OAuth, biometric)
- Role-based access control for budget permissions

### Data Synchronization
- Offline-first design with conflict resolution
- Sync endpoints for push/pull operations
- Timestamp-based conflict detection

### Performance Optimization
- Redis caching with configurable TTL
- Rate limiting per IP address
- Database query optimization with SQLAlchemy

### API Versioning
- Version prefix in URL (`/api/v1/`)
- Backward compatibility considerations
- Structured endpoint organization