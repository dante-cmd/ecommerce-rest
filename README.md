# Ecommerce REST API

Production-ready, modular e-commerce REST API built with FastAPI, SQLAlchemy, Microsoft SQL Server 2022, and Docker.  
Designed with clean architecture principles, security-first defaults, observability, and testability.

## Project Overview
This project delivers a complete ecommerce backend that includes:
- Authentication (JWT access + refresh tokens)
- Role-based authorization (customer / seller / admin)
- Full catalog management with search, filtering, pagination, and tags
- Shopping cart and guest-cart merge flow
- Order lifecycle management with stock updates
- Simulated payments and webhooks
- Reviews and rating aggregation
- Admin dashboard stats and management endpoints
- Structured logging, rate limiting, health and metrics endpoints
- Robust data seeding (basic + MCMC behavioral simulator)

## Architecture (Clean & Modular)
The project follows a layered structure:
- `core/`: configuration, database, security, logging, exceptions
- `models/`: SQLAlchemy ORM models
- `schemas/`: Pydantic v2 request/response DTOs
- `crud/`: repositories (DB access only)
- `services/`: business rules and orchestration
- `routers/`: FastAPI route definitions
- `tasks/`: Celery background tasks
- `utils/`: helpers (pagination, filters)

## Tech Stack
- **API**: FastAPI + Uvicorn/Gunicorn
- **Language**: Python 3.12
- **Database**: SQL Server 2022
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Auth**: JWT (python-jose + PyJWT), bcrypt hashing
- **Cache / Broker**: Redis
- **Background Tasks**: Celery
- **Observability**: structlog, Prometheus metrics
- **Dev Tools**: Poetry, Black, Ruff, mypy, pytest

## Key Features
- **Auth**: Register, login, refresh, logout, profile, password change
- **Catalog**: CRUD products, categories, tags, images, inventory
- **Search**: price/category/rating filters + sorting + pagination
- **Cart**: add/update/remove, merge guest cart on login
- **Orders**: create from cart, cancel with stock restore, status flow
- **Payments**: simulated payment endpoint + webhook
- **Reviews**: only after delivery, updates rating averages
- **Admin**: dashboard stats + list users/products/orders
- **Operational**: CORS, trusted hosts, rate limiting, health, metrics

## Project Structure
```
ecommerce-api/
├── app/
│   ├── main.py
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── crud/
│   ├── routers/
│   ├── dependencies/
│   ├── services/
│   ├── utils/
│   └── tasks/
├── alembic/
├── tests/
├── docker/
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── README.md
├── USAGE.md
├── seed_data.py
└── mcmc_seed.py
```

## API Versioning
All endpoints are served under `/api/v1/`.

## Security Notes
- Passwords are hashed with bcrypt (via Passlib).
- JWT access and refresh tokens with expiration.
- Refresh token blacklist for logout simulation.
- Strict Pydantic validation (extra fields forbidden).

## Observability
- Structured logs via `structlog`.
- `/metrics` endpoint for Prometheus-style metrics.
- `/health` endpoint for uptime checks.

## Data Seeding
Two seed scripts are provided:
- `seed_data.py`: quick deterministic fake data
- `mcmc_seed.py`: behavioral simulation using Markov chains (MCMC)

The MCMC seed simulates realistic sessions (browse → view → cart → checkout → purchase/abandon) using different personas (impulse, researcher, window-shopper) and calibrated transition probabilities.

## Quickstart (Docker)
1. Copy `.env.example` to `.env` and adjust values if needed.
2. Build and run:
```bash
docker compose up --build
```
3. Run migrations:
```bash
docker compose exec api alembic upgrade head
```
4. Seed data:
```bash
docker compose exec api python seed_data.py --force
```
5. MCMC behavioral seed:
```bash
docker compose exec api python mcmc_seed.py --force --sessions 5000
```

Open API docs at:
```
http://localhost:8000/api/v1/docs
```

## Usage Examples
See `USAGE.md` for request examples with curl for auth, products, cart, orders, payments, reviews, and admin endpoints.

## Local Development
```bash
poetry install
poetry run uvicorn app.main:app --reload
```

## Environment Variables
- `ENV` = development|staging|production|test
- `DATABASE_URL` = MSSQL connection string
- `REDIS_URL` = Redis connection
- `SECRET_KEY` = JWT secret
- `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_MINUTES`
- `RATE_LIMIT_PER_MINUTE`

## Tests
```bash
pytest --cov=app --cov-report=term-missing
```

For MSSQL-backed tests, set:
```bash
TEST_DATABASE_URL=mssql+pyodbc://...
```

## Seed Data
```bash
python seed_data.py --force
```

## Scheduler (MCMC)
Run the behavioral seed on a schedule:
```bash
python mcmc_seed.py --interval-minutes 60
```

## MCMC Behavioral Seed (New)
Generate realistic user-session data using a Markov Chain Monte Carlo simulator:
```bash
python mcmc_seed.py --force --sessions 5000
```

Run on a schedule (e.g., every 60 minutes):
```bash
python mcmc_seed.py --interval-minutes 60
```
