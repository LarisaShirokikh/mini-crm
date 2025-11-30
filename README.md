# Mini-CRM Backend Service

Multi-tenant CRM backend service built with FastAPI and PostgreSQL.

## Features

- **Multi-tenant architecture**: Data isolation per organization
- **Role-based access control**: Owner, Admin, Manager, Member roles
- **RESTful API**: Full CRUD operations for all entities
- **JWT Authentication**: Access and refresh tokens
- **Sales Pipeline**: Deal stages with validation rules
- **Activity Tracking**: Automatic activity logging for deal changes
- **Analytics**: Deal summaries and sales funnel metrics

## Tech Stack

- **Framework**: FastAPI (async)
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Migrations**: Alembic
- **Authentication**: JWT (PyJWT)
- **Validation**: Pydantic v2
- **Testing**: pytest with pytest-asyncio
- **Linting**: ruff, mypy

## Project Structure
```
mini-crm/
├── src/app/
│   ├── api/v1/           # API endpoints and schemas
│   │   ├── endpoints/    # Route handlers
│   │   ├── schemas/      # Pydantic models
│   │   └── dependencies.py
│   ├── core/             # Configuration, security, exceptions
│   ├── db/               # Database session and base models
│   ├── models/           # SQLAlchemy ORM models
│   ├── repositories/     # Data access layer
│   ├── services/         # Business logic layer
│   └── main.py
├── migrations/           # Alembic migrations
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis (optional, for caching)
- Poetry

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mini-crm
```

2. Install dependencies:
```bash
poetry install
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Start PostgreSQL and Redis:
```bash
docker-compose up -d db redis
```

5. Run migrations:
```bash
poetry run alembic upgrade head
```

6. Start the server:
```bash
poetry run uvicorn app.main:app --reload
```

7. Open API docs: http://localhost:8000/docs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection URL | - |
| `DATABASE_URL_SYNC` | PostgreSQL sync URL (for Alembic) | - |
| `SECRET_KEY` | JWT signing key | - |
| `DEBUG` | Enable debug mode | `false` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user with organization |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |

### Organizations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/organizations/me` | List user's organizations |
| POST | `/api/v1/organizations/{id}/members` | Add member |
| PATCH | `/api/v1/organizations/{id}/members/{user_id}` | Update member role |
| DELETE | `/api/v1/organizations/{id}/members/{user_id}` | Remove member |

### Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/contacts` | List contacts |
| POST | `/api/v1/contacts` | Create contact |
| GET | `/api/v1/contacts/{id}` | Get contact |
| PATCH | `/api/v1/contacts/{id}` | Update contact |
| DELETE | `/api/v1/contacts/{id}` | Delete contact |

### Deals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/deals` | List deals |
| POST | `/api/v1/deals` | Create deal |
| GET | `/api/v1/deals/{id}` | Get deal |
| PATCH | `/api/v1/deals/{id}` | Update deal |
| DELETE | `/api/v1/deals/{id}` | Delete deal |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List tasks |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks/{id}` | Get task |
| PATCH | `/api/v1/tasks/{id}` | Update task |
| DELETE | `/api/v1/tasks/{id}` | Delete task |

### Activities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/deals/{deal_id}/activities` | List deal activities |
| POST | `/api/v1/deals/{deal_id}/activities` | Add comment |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/deals/summary` | Deals summary by status |
| GET | `/api/v1/analytics/deals/funnel` | Sales funnel data |

## Authentication

All endpoints (except auth) require:
- `Authorization: Bearer <access_token>` header
- `X-Organization-Id: <org_id>` header (for resource endpoints)

## Business Rules

### Roles and Permissions

| Role | Manage Org | Manage All Entities | Rollback Stage |
|------|------------|---------------------|----------------|
| Owner | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ |
| Manager | ❌ | ✅ | ❌ |
| Member | ❌ | Own only | ❌ |

### Deal Rules

- Cannot close deal as WON with amount ≤ 0
- Cannot delete contact with active deals
- Only Owner/Admin can rollback deal stage
- Status/stage changes create Activity records

### Deal Stages

1. Qualification → 2. Proposal → 3. Negotiation → 4. Closed

## Running Tests
```bash
# Create test database
createdb mini_crm_test

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run only unit tests
poetry run pytest tests/unit -v

# Run only integration tests
poetry run pytest tests/integration -v
```

## Code Quality
```bash
# Linting
poetry run ruff check .

# Type checking
poetry run mypy src/app

# Format code
poetry run ruff format .
```

## Database Migrations
```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# Show current revision
poetry run alembic current
```

## Docker
```bash
# Start all services
docker-compose up -d

# Start only database and redis
docker-compose up -d db redis

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down
```

## License

MIT