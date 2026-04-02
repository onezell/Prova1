# CLAUDE.md — Email AI Classifier

## Project Overview

Email AI Classifier is a POC for intelligent business email management: automatic reading via IMAP, AI-powered classification (OpenAI-compatible API), approval workflows, and reply sending via SMTP. Italian-language domain (wine business mock data).

## Architecture

```
frontend/          React 19 + Vite 8 SPA (Tailwind CSS v4, React Router v7)
backend/           FastAPI async API (Python 3.12, SQLAlchemy 2.0 async, SQLite via aiosqlite)
docker-compose.yml Orchestrates both services
```

- **No external infra**: SQLite for persistence, FastAPI background tasks for scheduling, no Redis/Celery/queues.
- Backend serves on port **8000**, frontend on port **3000** (nginx in Docker, Vite dev server on 5173).
- All API routes are under `/api/` prefix.

## Quick Start

```bash
# Docker (production-like)
cp backend/.env.example backend/.env   # edit with real credentials
docker-compose up --build              # backend:8000, frontend:3000

# Local development
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

## Backend Structure (`backend/app/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, all API endpoints, lifespan (DB init + scheduler) |
| `config.py` | `pydantic-settings` config from `.env` (Settings singleton) |
| `database.py` | Async SQLAlchemy engine + session factory |
| `db_models.py` | SQLAlchemy ORM models: `EmailDB`, `ReplyTemplateDB` |
| `models.py` | Pydantic request/response schemas |
| `auth.py` | JWT authentication (access + refresh tokens) |
| `classifier.py` | OpenAI-compatible API calls for classification + reply generation |
| `email_client.py` | IMAP fetch + SMTP send |
| `scheduler.py` | Async background polling scheduler |
| `seed.py` | Mock data generator (wine business emails in Italian) |

### Key Patterns

- **Async everywhere**: all DB operations use `async/await` with `AsyncSession`.
- **Dependency injection**: `get_db` and `get_current_user` via FastAPI `Depends()`.
- **Email status flow**: `new` → `classified` → `pending_approval` → `approved` → `replied`.
- **Deduplication**: emails are deduplicated by `message_id` (IMAP Message-ID header).
- **ID format**: UUIDs as strings (`str(uuid.uuid4())`).

### API Endpoints

- `POST /api/auth/login` — JWT login
- `POST /api/auth/refresh` — refresh token
- `GET /api/auth/me` — current user
- `GET /api/health` — health + scheduler status
- `GET /api/emails` — paginated list (filters: status, category, mailbox)
- `GET /api/emails/{id}` — single email
- `POST /api/emails/fetch` — fetch from IMAP
- `POST /api/emails/{id}/classify` — classify single email
- `POST /api/emails/classify-all` — classify all "new" emails
- `POST /api/emails/{id}/correct` — human category correction
- `POST /api/emails/{id}/submit-for-approval` — submit reply for approval
- `POST /api/emails/{id}/approve` — approve pending reply
- `POST /api/emails/{id}/reject` — reject pending reply
- `POST /api/emails/{id}/reply` — send reply via SMTP
- `POST /api/emails/{id}/generate-reply` — AI-generate reply
- `GET/POST/PUT/DELETE /api/templates` — reply template CRUD
- `GET/PUT /api/settings/email` — IMAP/SMTP settings
- `GET/PUT /api/settings/ai` — OpenAI settings
- `GET/PUT /api/settings/polling` — polling/auto-approve settings
- `GET /api/stats` — dashboard statistics
- `POST /api/seed` — load demo data

## Frontend Structure (`frontend/src/`)

| File/Dir | Purpose |
|----------|---------|
| `App.jsx` | Root component, routing, auth state |
| `api.js` | Axios instance with JWT interceptor |
| `pages/Login.jsx` | Login form |
| `pages/Dashboard.jsx` | Main dashboard with stats |
| `pages/EmailList.jsx` | Paginated email list with filters |
| `pages/EmailDetail.jsx` | Single email view + actions |
| `pages/Approvals.jsx` | Approval queue |
| `pages/Templates.jsx` | Reply template management |
| `pages/Stats.jsx` | Statistics/charts (Recharts) |
| `pages/SettingsPage.jsx` | Email/AI/polling configuration |
| `components/Sidebar.jsx` | Navigation sidebar |
| `components/CategoryBadge.jsx` | Category display chip |
| `components/StatusBadge.jsx` | Status display chip |

### Frontend Conventions

- **React 19** with hooks (no class components).
- **Tailwind CSS v4** for styling (utility-first, no CSS modules).
- **Axios** for API calls; JWT token stored in `localStorage`.
- **Recharts** for data visualization.
- **Lucide React** for icons.
- Pages are in `src/pages/`, reusable components in `src/components/`.

## Testing

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest                    # runs all tests
pytest tests/test_auth.py # run specific test file
```

### Test Structure (`backend/tests/`)

- `conftest.py` — shared fixtures: in-memory SQLite, async client, auth helpers
- `test_auth.py` — authentication endpoints
- `test_emails.py` — email CRUD and classification
- `test_approval.py` — approval workflow
- `test_templates.py` — template CRUD
- `test_settings.py` — settings endpoints
- `test_stats.py` — statistics endpoint
- `test_health.py` — health check
- `test_seed.py` — seed/mock data

### Test Conventions

- Tests use **in-memory SQLite** (override via `DATABASE_URL` env var in conftest).
- Use `httpx.AsyncClient` with `ASGITransport` for API tests (no real server needed).
- Auth fixtures: `auth_token` and `auth_headers` provide valid JWT for protected endpoints.
- All test functions are `async def` using `pytest-asyncio`.

## Environment Variables

See `backend/.env.example` for all available variables. Key ones:

| Variable | Purpose | Default |
|----------|---------|---------|
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Login credentials | admin / changeme |
| `JWT_SECRET` | Token signing key | change-this-secret-in-production |
| `DATABASE_URL` | SQLite connection string | sqlite+aiosqlite:///./data/emails.db |
| `IMAP_HOST/PORT/USER/PASSWORD` | Email reading | gmail defaults |
| `SMTP_HOST/PORT/USER/PASSWORD` | Email sending | gmail defaults |
| `OPENAI_API_KEY/BASE_URL/MODEL` | AI classification | gpt-4o-mini |
| `POLLING_ENABLED` | Background email polling | false |
| `AUTO_APPROVE_THRESHOLD` | Auto-approve confidence threshold | 0.0 (disabled) |

## Development Guidelines

- **Language**: Backend code and comments are in English. UI labels and mock data are in Italian.
- **Never commit `.env` files** — they contain secrets. Use `.env.example` as reference.
- **Add tests** for new backend endpoints in `backend/tests/`.
- **SQLite data** is stored in `backend/data/emails.db` (created automatically, gitignored via Docker volume).
- When adding new email fields, update both `db_models.py` (SQLAlchemy) and `models.py` (Pydantic).
- All endpoints except `/api/health` and `/api/auth/login` require JWT authentication.
