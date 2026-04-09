# Ecommerce REST API

Production-ready ecommerce REST API built with FastAPI, SQLAlchemy, MSSQL 2022, and Docker.

**Key features**
- JWT auth + refresh tokens + role-based access
- Products, categories, cart, orders, reviews, payments (simulated)
- Admin dashboard endpoints
- Structured logging, rate limiting, health/metrics
- Alembic migrations, seed data generator

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

Open API docs at `http://localhost:8000/api/v1/docs`.

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

## MCMC Behavioral Seed (New)
Generate realistic user-session data using a Markov Chain Monte Carlo simulator:
```bash
python mcmc_seed.py --force --sessions 5000
```

Run on a schedule (e.g., every 60 minutes):
```bash
python mcmc_seed.py --interval-minutes 60
```
