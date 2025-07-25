# Technology Stack

## Core Framework
- **FastAPI** - Modern Python web framework with automatic API documentation
- **Python 3.8+** - Primary programming language
- **Uvicorn** - ASGI server for development
- **Gunicorn** - Production WSGI server with Uvicorn workers

## Database & ORM
- **PostgreSQL 12+** - Primary database
- **SQLAlchemy 2.0** - ORM with declarative models
- **Alembic** - Database migration management
- **psycopg2-binary** - PostgreSQL adapter

## Authentication & Security
- **python-jose[cryptography]** - JWT token handling
- **passlib[bcrypt]** - Password hashing
- **Google Auth libraries** - OAuth integration

## Caching & Performance
- **Redis** - Caching and session storage
- **SlowAPI** - Rate limiting middleware

## AI/ML Features
- **OpenAI Whisper** - Audio transcription
- **torch/torchaudio** - ML model dependencies
- **librosa/soundfile/pydub** - Audio processing

## Configuration & Environment
- **pydantic-settings** - Configuration management
- **python-dotenv** - Environment variable loading

## Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **httpx** - HTTP client for testing

## Common Commands

### Development Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Database Operations
```bash
# Start PostgreSQL with Docker
docker compose up -d

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Running the Application
```bash
# Development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Testing
```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v

# Run tests matching pattern
pytest -k "test_auth" -v
```

### Docker Operations
```bash
# Build and run with Docker Compose
docker-compose up -d

# Build Docker image
docker build -t expense-tracker-api .
```

## Configuration Management
- Uses Pydantic Settings for type-safe configuration
- Environment variables loaded from `.env` file
- Separate settings for development/production environments
- Configuration includes database URLs, JWT secrets, rate limits, cache settings