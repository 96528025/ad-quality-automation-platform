# Ad Quality Automation Platform

A testing-focused mini ad platform that simulates campaign creation, ad delivery, event tracking, conversion attribution, quality alerts, synthetic traffic, and automated regression testing.

This is a portfolio project for quality engineering and backend testing roles. It is not intended to be a production ad server. The goal is to model realistic quality risks in advertising systems and validate them through API, integration, and performance tests.

## Tech Stack

- Backend: FastAPI, SQLAlchemy
- Database: SQLite by default, PostgreSQL-compatible SQLAlchemy setup
- Testing: Pytest, FastAPI TestClient
- Performance: Locust
- Data: Synthetic seed and traffic generation scripts
- CI: GitHub Actions

## Core Workflow

1. Create a campaign with budget, bid, status, and targeting rules.
2. Create an ad under the campaign.
3. Create synthetic users.
4. Request an ad for a user.
5. Store an impression when an ad is delivered.
6. Record clicks against impressions and deduct CPC budget.
7. Record conversions against clicks within a 7-day attribution window.
8. Calculate CTR, CVR, spend, and remaining budget.
9. Run quality checks for abnormal CTR/CVR and repeated click patterns.

## Run Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

The guided demo dashboard is available at:

```text
http://127.0.0.1:8000/
```

If file watching is restricted on your machine, run without reload:

```bash
uvicorn app.main:app
```

## Run with Docker and PostgreSQL

```bash
docker compose up --build
```

The dashboard will be available at:

```text
http://127.0.0.1:8000/
```

## Run Tests

```bash
cd backend
pytest
```

The test command also generates a coverage report through `pytest-cov`.

## Code Quality Gates

```bash
cd backend
ruff check .
mypy app
pytest
```

Current local validation covers linting, type checking, 16 automated tests, and coverage reporting.

## Database Migrations

Alembic manages schema migrations for PostgreSQL and SQLite-compatible local development.

```bash
cd backend
alembic upgrade head
```

When using Docker Compose, migrations run automatically before the API starts.

## Generate Synthetic Data

From the project root:

```bash
python scripts/seed_data.py
python scripts/generate_traffic.py
python scripts/inject_anomalies.py
```

Reset the local SQLite database:

```bash
python scripts/reset_data.py
```

## Run One-Command Demo Flow

With the API running:

```bash
python scripts/demo_workflow.py --base-url http://127.0.0.1:8000
```

## Run Performance Test

Start the API first, then run:

```bash
locust -f performance/locustfile.py --host http://127.0.0.1:8000
```

Or run the headless baseline:

```bash
cd backend
.venv/bin/locust -f ../performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 100 -r 10 -t 1m --html ../performance/report.html --csv ../performance/results
```

See [docs/performance_report.md](docs/performance_report.md) for the latest recorded local results.

## Production-Readiness Features

- PostgreSQL-ready database configuration with Alembic migrations
- Ruff linting, mypy type checking, and pytest coverage reporting
- `/health` and `/ready` endpoints for service and database readiness checks
- Structured JSON request logs with request IDs and latency
- Alert lifecycle fields: `open`, `acknowledged`, `investigating`, `resolved`, `false_positive`
- Hourly campaign metrics aggregation table for scalable metrics reads

## Project Structure

```text
backend/
  app/
    routers/
    services/
    main.py
    models.py
    schemas.py
  tests/
    unit/
    api/
    integration/
scripts/
performance/
docs/
.github/workflows/
```

## Resume Positioning

Built a testing-focused ad quality automation platform with FastAPI, SQLAlchemy, Pytest, and Locust to validate campaign creation, ad delivery, impression/click/conversion tracking, attribution rules, and abnormal CTR/CVR quality alerts using synthetic traffic data.
