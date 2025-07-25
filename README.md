# Spendro - RESTful Expense Tracking API

A comprehensive FastAPI-based RESTful API backend for the Spendro collaborative expense tracking application. Built with modern Python technologies, this API provides multi-user budget management, real-time synchronization, and advanced financial transaction handling.

## 🚀 Key Features

### Core Functionality

- **RESTful API Design**: Full REST compliance with proper HTTP methods, status codes, and resource-based URLs
- **Multi-User Collaborative Budgets**: Share budgets with role-based access control (Admin, Editor, Viewer)
- **Advanced Transaction Management**: Support for income, expenses, investments with custom metadata and multi-currency
- **Recurring Transactions**: Automated scheduling for recurring income and expenses
- **Real-Time Synchronization**: Offline-first design with intelligent conflict resolution

### Authentication & Security

- **Multiple Authentication Methods**: Email/phone + password, Google OAuth, and biometric authentication
- **JWT Token-Based Security**: Secure stateless authentication with configurable expiration
- **Rate Limiting**: IP-based request throttling with configurable limits
- **Role-Based Access Control**: Granular permissions for budget management

### AI & Advanced Features

- **Audio Transcription**: Whisper AI integration for voice-to-expense conversion
- **Smart Caching**: Redis-based caching with configurable TTL for optimal performance
- **Database Migrations**: Alembic-powered schema versioning and migrations
- **Comprehensive Testing**: 80%+ test coverage with pytest and async support

### Developer Experience

- **Auto-Generated Documentation**: Interactive Swagger/OpenAPI documentation
- **Docker Support**: Complete containerization with Docker Compose
- **Environment Configuration**: Flexible configuration management with Pydantic Settings
- **Mock Data Support**: Development-friendly mock data system

## 📋 Requirements

- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Spendro-api
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file based on the template:

```bash
cp .envTemplate .env
```

Edit the `.env` file with your configuration. Here's the complete configuration based on `.envTemplate`:

```env
# Database Configuration
POSTGRES_USER=spendro_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=spendro-db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_URL="postgresql://spendro_user:your_secure_password@localhost:5432/spendro-db"

# JWT Security
SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Application Settings
ENVIRONMENT=development
DEBUG=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=50

# Redis Configuration
REDIS_HOST=localhost
REDIS_DB=0
REDIS_PASSWORD=your_redis_password
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379

# Caching Settings
CACHE_TTL_MINUTES=15
CACHE_MAX_SIZE_MB=100

# Pagination
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100

# AI Transcription (Whisper)
WHISPER_MODEL=base
MAX_AUDIO_DURATION_SECONDS=60
MAX_AUDIO_FILE_SIZE_MB=10
TRANSCRIPTION_LANGUAGE=es
```

### 5. Database Setup with Docker (Recommended)

The project includes a complete Docker Compose setup for PostgreSQL and Redis:

```bash
# Start PostgreSQL and Redis containers
docker compose up -d

# Verify containers are running
docker compose ps
```

#### Manual Database Setup (Alternative)

If you prefer manual installation:

**PostgreSQL:**

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# macOS (Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

#### Run Database Migrations

```bash
# Run migrations to create tables
alembic upgrade head

# Create new migration (when you modify models)
alembic revision --autogenerate -m "description"
```

### 6. Redis Setup (Optional)

**Ubuntu/Debian:**

```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

**macOS (using Homebrew):**

```bash
brew install redis
brew services start redis
```

**Windows:**
Download from [Redis official website](https://redis.io/download) or use Docker

### 7. Google OAuth Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add your client ID and secret to `.env` file

## 🚀 Running the Application

### Development Server

```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
# Install production server
pip install gunicorn

# Start production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker (Complete Setup)

The project includes a complete Docker Compose configuration for all services:

```bash
# Start all services (PostgreSQL + Redis)
docker compose up -d

# View running containers
docker compose ps

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove volumes (WARNING: This deletes all data)
docker compose down -v
```

#### Docker Compose Services

The `docker-compose.yml` includes:

- **PostgreSQL 15.3**: Primary database with persistent volume
- **Redis 7.0**: Caching and session storage with password protection
- **Health Checks**: Automatic service health monitoring
- **Environment Variables**: Configured from your `.env` file

## 🌐 RESTful API Design

This API follows REST architectural principles with proper resource-based URLs, HTTP methods, and status codes:

### API Endpoints Overview

| Resource            | Method | Endpoint                                        | Description                      |
| ------------------- | ------ | ----------------------------------------------- | -------------------------------- |
| **Authentication**  | POST   | `/api/v1/auth/register`                         | User registration                |
|                     | POST   | `/api/v1/auth/login`                            | Email/password login             |
|                     | POST   | `/api/v1/auth/google`                           | Google OAuth login               |
|                     | POST   | `/api/v1/auth/biometric`                        | Biometric authentication         |
| **Users**           | GET    | `/api/v1/users/me`                              | Get current user profile         |
|                     | PUT    | `/api/v1/users/me`                              | Update current user              |
|                     | DELETE | `/api/v1/users/me`                              | Delete current user              |
|                     | GET    | `/api/v1/users/search`                          | Search users                     |
|                     | GET    | `/api/v1/users/{user_id}`                       | Get user by ID                   |
| **Budgets**         | POST   | `/api/v1/budgets/`                              | Create budget                    |
|                     | GET    | `/api/v1/budgets/`                              | List user budgets                |
|                     | GET    | `/api/v1/budgets/{budget_id}`                   | Get budget details               |
|                     | PUT    | `/api/v1/budgets/{budget_id}`                   | Update budget                    |
|                     | DELETE | `/api/v1/budgets/{budget_id}`                   | Delete budget                    |
|                     | PATCH  | `/api/v1/budgets/archive/{budget_id}`           | Archive budget                   |
|                     | POST   | `/api/v1/budgets/{budget_id}/users/{user_id}`   | Add user to budget               |
|                     | DELETE | `/api/v1/budgets/{budget_id}/users/{user_id}`   | Remove user from budget          |
|                     | PATCH  | `/api/v1/budgets/{budget_id}/users/{user_id}`   | Update user role                 |
| **Transactions**    | POST   | `/api/v1/transactions/`                         | Create transaction               |
|                     | GET    | `/api/v1/transactions/`                         | List transactions                |
|                     | GET    | `/api/v1/transactions/{transaction_id}`         | Get transaction                  |
|                     | PUT    | `/api/v1/transactions/{transaction_id}`         | Update transaction               |
|                     | DELETE | `/api/v1/transactions/{transaction_id}`         | Delete transaction               |
|                     | POST   | `/api/v1/transactions/recurring`                | Create recurring transaction     |
|                     | GET    | `/api/v1/transactions/recurring`                | List recurring transactions      |
|                     | PUT    | `/api/v1/transactions/recurring/{recurring_id}` | Update recurring transaction     |
|                     | DELETE | `/api/v1/transactions/recurring/{recurring_id}` | Delete recurring transaction     |
| **Synchronization** | POST   | `/api/v1/sync/push`                             | Push local changes               |
|                     | GET    | `/api/v1/sync/pull`                             | Pull server changes              |
|                     | GET    | `/api/v1/sync/conflicts`                        | Get sync conflicts               |
|                     | POST   | `/api/v1/sync/conflicts/resolve`                | Resolve conflicts                |
|                     | GET    | `/api/v1/sync/status`                           | Get sync status                  |
| **Transcription**   | POST   | `/api/v1/transcription/transcribe`              | Transcribe audio to text         |
|                     | GET    | `/api/v1/transcription/supported-formats`       | Get supported audio formats      |
|                     | GET    | `/api/v1/transcription/service-status`          | Get transcription service status |

### REST Compliance Features

- **Resource-Based URLs**: Clear, hierarchical resource identification
- **HTTP Methods**: Proper use of GET, POST, PUT, DELETE, PATCH
- **Status Codes**: Appropriate HTTP status codes (200, 201, 204, 400, 401, 403, 404, 422, 429, 500)
- **Stateless**: JWT-based authentication without server-side sessions
- **JSON Communication**: Consistent JSON request/response format
- **Pagination**: Limit/offset pagination for list endpoints
- **Filtering**: Query parameters for resource filtering
- **Versioning**: API versioning with `/api/v1/` prefix

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v

# Run tests with specific pattern
pytest -k "test_auth" -v
```

### Test Coverage Report

After running tests with coverage, open `htmlcov/index.html` in your browser to view the detailed coverage report.

## 🏗️ Project Structure

```
expense-tracker-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── security.py        # Authentication & security
│   │   └── mock_data.py       # Mock data for testing
│   ├── models/
│   │   └── models.py          # SQLAlchemy models
│   ├── schemas/
│   │   ├── auth.py           # Authentication schemas
│   │   ├── user.py           # User schemas
│   │   ├── budget.py         # Budget schemas
│   │   ├── transaction.py    # Transaction schemas
│   │   └── sync.py           # Synchronization schemas
│   ├── api/
│   │   └── v1/
│   │       ├── api.py        # API router
│   │       └── endpoints/    # API endpoints
│   ├── services/             # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── budget_service.py
│   │   ├── transaction_service.py
│   │   └── sync_service.py
│   └── middleware/           # Custom middleware
│       ├── auth.py
│       ├── rate_limit.py
│       └── cache.py
├── alembic/                  # Database migrations
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

| Variable                       | Description                                       | Default                |
| ------------------------------ | ------------------------------------------------- | ---------------------- |
| **Database Configuration**     |                                                   |                        |
| `POSTGRES_USER`                | PostgreSQL username                               | Required               |
| `POSTGRES_PASSWORD`            | PostgreSQL password                               | Required               |
| `POSTGRES_DB`                  | PostgreSQL database name                          | spendro-db             |
| `DATABASE_HOST`                | Database host                                     | localhost              |
| `DATABASE_PORT`                | Database port                                     | 5432                   |
| `DATABASE_URL`                 | Complete PostgreSQL connection string             | Required               |
| **Security & Authentication**  |                                                   |                        |
| `SECRET_KEY`                   | JWT secret key (use long random string)           | Required               |
| `ALGORITHM`                    | JWT algorithm                                     | HS256                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | Token expiration time in minutes                  | 60                     |
| `GOOGLE_CLIENT_ID`             | Google OAuth client ID                            | Optional               |
| `GOOGLE_CLIENT_SECRET`         | Google OAuth client secret                        | Optional               |
| **Application Settings**       |                                                   |                        |
| `ENVIRONMENT`                  | Environment (development/production)              | development            |
| `DEBUG`                        | Debug mode                                        | true                   |
| `RATE_LIMIT_PER_MINUTE`        | Rate limiting per IP                              | 50                     |
| **Redis Configuration**        |                                                   |                        |
| `REDIS_HOST`                   | Redis server host                                 | localhost              |
| `REDIS_DB`                     | Redis database number                             | 0                      |
| `REDIS_PASSWORD`               | Redis password                                    | Optional               |
| `REDIS_PORT`                   | Redis port                                        | 6379                   |
| `REDIS_URL`                    | Complete Redis connection string                  | redis://localhost:6379 |
| **Caching Settings**           |                                                   |                        |
| `CACHE_TTL_MINUTES`            | Cache time-to-live in minutes                     | 15                     |
| `CACHE_MAX_SIZE_MB`            | Maximum cache size in MB                          | 100                    |
| **Pagination**                 |                                                   |                        |
| `DEFAULT_PAGE_SIZE`            | Default items per page                            | 10                     |
| `MAX_PAGE_SIZE`                | Maximum items per page                            | 100                    |
| **AI Transcription (Whisper)** |                                                   |                        |
| `WHISPER_MODEL`                | Whisper model size (tiny/base/small/medium/large) | base                   |
| `MAX_AUDIO_DURATION_SECONDS`   | Maximum audio duration                            | 60                     |
| `MAX_AUDIO_FILE_SIZE_MB`       | Maximum audio file size in MB                     | 10                     |
| `TRANSCRIPTION_LANGUAGE`       | Default transcription language                    | es                     |

### Rate Limiting

- Default: 50 requests per minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE` environment variable

### Caching

- TTL: 15 minutes from last request
- Max size: 100MB
- Configurable via environment variables

## 🔐 Authentication

### Supported Methods

1. **Email/Phone + Password**: Traditional authentication
2. **Google OAuth**: Social authentication (requires setup)
3. **Biometric**: Fingerprint authentication (mobile apps)

### JWT Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "phone": "+1234567890",
  "name": "User Name",
  "roles": ["user"],
  "iat": 1234567890,
  "exp": 1234567890
}
```

## 📊 Database Schema

### Core Tables

- **users**: User account information
- **budgets**: Budget containers
- **user_budgets**: User-budget relationships with roles
- **transactions**: Financial transactions
- **recurring_transactions**: Scheduled recurring transactions
- **transaction_categories**: Predefined categories
- **transaction_subcategories**: Category subdivisions

### Roles

- **Admin**: Full budget management access
- **Editor**: Can add/edit transactions
- **Viewer**: Read-only access

## 🔄 Synchronization

### Endpoints

- `POST /api/v1/sync/push`: Push local changes
- `GET /api/v1/sync/pull`: Pull server changes
- `GET /api/v1/sync/conflicts`: Get unresolved conflicts
- `POST /api/v1/sync/conflicts/resolve`: Resolve conflicts
- `GET /api/v1/sync/status`: Get sync status

### Conflict Resolution

The API supports automatic and manual conflict resolution:

- **Automatic**: Last-write-wins for simple conflicts
- **Manual**: User chooses resolution for complex conflicts

## 🎤 AI Audio Transcription

### Whisper Integration

The API includes OpenAI Whisper integration for converting audio recordings to expense descriptions:

### Supported Features

- **Multiple Audio Formats**: WAV, MP3, M4A, FLAC, OGG
- **Language Support**: Configurable transcription language (default: Spanish)
- **File Size Limits**: Maximum 10MB per audio file
- **Duration Limits**: Maximum 60 seconds per recording
- **Model Selection**: Configurable Whisper model (tiny/base/small/medium/large)

### Transcription Endpoints

```bash
# Transcribe audio file
POST /api/v1/transcription/transcribe
Content-Type: multipart/form-data

# Get supported audio formats
GET /api/v1/transcription/supported-formats

# Check transcription service status
GET /api/v1/transcription/service-status
```

### Usage Example

```python
import requests

# Transcribe audio file
with open('expense_recording.wav', 'rb') as audio_file:
    files = {'audio': audio_file}
    headers = {'Authorization': 'Bearer your_jwt_token'}

    response = requests.post(
        'http://localhost:8000/api/v1/transcription/transcribe',
        files=files,
        headers=headers
    )

    result = response.json()
    transcribed_text = result['transcription']
```

## 🚨 Error Handling

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Too Many Requests
- `500`: Internal Server Error

### Error Response Format

```json
{
  "detail": "Error description",
  "error": "Additional error information"
}
```

## 🔍 Monitoring & Logging

### Health Check

```bash
curl http://localhost:8000/health
```

### Cache Statistics

Access cache statistics through the middleware (available in request context).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Maintain test coverage above 80%
- Update documentation for API changes
- Use type hints throughout the codebase

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env file
   - Ensure database exists and user has permissions

2. **Import Errors**

   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

3. **Authentication Issues**

   - Check SECRET_KEY is set in .env
   - Verify token expiration settings
   - Ensure proper Authorization header format

4. **Rate Limiting**
   - Check if you're exceeding 50 requests per minute
   - Wait for rate limit reset or adjust limits

### Mock Data Mode

If database connection fails, the application automatically switches to mock data mode for development and testing purposes.

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

---

**Built with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL**
