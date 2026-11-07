# HEAT-EWS

## Occupational Heat & Environmental Early Warning System

HEAT-EWS is a prototype for monitoring occupational heat risk, combining environmental data, workplace shift aggregates, explainable analytics, and operational alert workflows in one web application.

> **Prototype notice:** HEAT-EWS is a decision-support prototype, not a validated clinical diagnostic service. Always apply qualified professional judgment and local health and safety procedures.

## Highlights

- FastAPI backend with OpenAPI documentation and health monitoring.
- React/Vite dashboard for site overview, alerts, forecasts, analytics, data quality, and model evaluation.
- Live or cached weather and air-quality integration through Open-Meteo.
- Heat-index, anomaly, fusion, and supervised ML analytics.
- Workplace CSV upload and shift-level history/analytics.
- Privacy-preserving small-cell suppression for outward-facing workplace statistics.
- JWT authentication with role-aware API access.
- Validation scenarios and safety/privacy regression tests.

## Architecture

```text
React + Vite frontend
        │  /api requests
        ▼
FastAPI application
  ├── Authentication and authorization
  ├── Sites, environment, alerts, workplace, validation APIs
  ├── Analytics and alert services
  └── SQLAlchemy persistence
        │
        ├── PostgreSQL
        └── Open-Meteo Weather / Air Quality APIs
```

### Repository layout

```text
backend/
  app/
    analytics/       Heat-index, anomaly, fusion, and ML logic
    api/             FastAPI route modules
    core/            Settings, security, and privacy controls
    db/              SQLAlchemy models, sessions, initialization, seeders
    services/        Alerts, CSV, and weather integrations
  tests/             Privacy, safety, and anti-leakage tests
datasets/            Small synthetic workplace dataset and generator
docs/                Product requirements reference material
frontend/
  src/
    components/      Shared dashboard components
    pages/           Dashboard screens
    api.js           Frontend API client
run.py               Root development launcher for the backend
```

## Requirements

- Python 3.10+ (Python 3.11+ recommended)
- Node.js 18+ and npm
- PostgreSQL 14+ for persistent application data
- Network access to Open-Meteo when live environmental synchronization is enabled

## Quick start

### 1. Configure the backend

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item backend\.env.example backend\.env
```

Edit `backend\.env` and set a real PostgreSQL connection string and a long random `SECRET_KEY`. Never commit `.env` files or credentials.

Initialize the database if required by your environment:

```powershell
python -m backend.app.db.init_db
```

### 2. Run the API

From the repository root:

```powershell
python run.py
```

The API is available at `http://127.0.0.1:8000`.

- Health check: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/api/docs`
- ReDoc: `http://127.0.0.1:8000/api/redoc`

### 3. Run the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The development frontend uses the `/api` path and should be run alongside the backend.

## API surface

All application routes are prefixed with `/api`.

| Area | Routes |
| --- | --- |
| Authentication | `POST /auth/login`, `POST /auth/register`, `GET /auth/me`, `GET /auth/demo-accounts` |
| Sites | `GET /sites`, `GET /sites/{site_id}` |
| Environment | `GET /environment/{site_id}/current`, `GET /environment/{site_id}/forecast`, `POST /environment/{site_id}/sync` |
| Alerts | `GET /alerts`, `GET /alerts/{alert_id}`, `POST /alerts/{alert_id}/acknowledge`, `POST /alerts/{alert_id}/action` |
| Workplace | `POST /workplace/upload`, `GET /workplace/{site_id}/history`, `GET /workplace/{site_id}/analytics` |
| Validation | `GET /validation/scenarios`, `GET /validation/metrics`, `POST /validation/train-ml` |

Use the generated Swagger UI for request schemas, authentication requirements, and response examples.

## Workplace CSV format

Workplace uploads are aggregate shift feeds. The service validates the schema and rejects individual worker or patient identifiers. The synthetic sample in `datasets/workplace_daily.csv` can be used as a starting point.

Expected fields include:

```text
site_id, shift_date, workers_on_shift, worker_hours,
heat_incidents, near_misses, sickness_absence_count
```

Small-cell protection masks counts from 1 through 10 in public or export views. Do not add names, worker IDs, medical records, or other individual-level data.

## Testing and quality checks

Run backend tests from the repository root:

```powershell
python -m pytest backend\tests
```

Build the frontend:

```powershell
cd frontend
npm run build
```

The test suite covers privacy suppression, rejection of individual identifiers, safety invariants, and anti-leakage behavior.

## Configuration

The backend reads environment variables from `backend\.env`. Common settings include:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key; use a unique production secret |
| `OPEN_METEO_WEATHER_URL` | Weather API endpoint |
| `OPEN_METEO_AIR_QUALITY_URL` | Air-quality API endpoint |

Application defaults and operational thresholds are defined in `backend/app/core/config.py`. Review them before deploying outside a local prototype environment.

## Security and privacy

- Keep all `.env` files, credentials, signing keys, and private certificates out of version control.
- Use a managed secret store and separate keys per environment in production.
- Restrict CORS origins before production deployment; the local prototype currently permits broad origins for demo integration.
- Use TLS, database access controls, backups, audit logging, and dependency updates in deployed environments.
- Upload only aggregate workplace data and preserve the small-cell suppression policy.

## Data sources and scope

- Environmental observations and forecasts: Open-Meteo Weather and Air Quality APIs.
- Workplace data: synthetic aggregate shift feeds for the prototype.
- Geographic and operational scope: Abu Dhabi, UAE; configured timezone: `Asia/Dubai`.

## License

No license has been declared yet. Add an appropriate license before distributing or accepting external contributions.
