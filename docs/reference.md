# Reference — Project Structure & Conventions

> For agents (and humans): how this codebase is laid out, how each service works, and the conventions to follow when extending it.

## Top-level layout

```
ecommerce/
├── common/                  # Shared code — empty stubs; only requirements.txt has content
├── user_service/            # FastAPI service — port 8001 (only fully implemented service)
├── product_service/         # FastAPI service — port 8002 (routes + hardcoded data; no DB)
├── order_service/           # FastAPI service — port 8003 (empty skeleton files)
├── frontend.html            # Static single-file UI
├── docker-compose.yml       # RabbitMQ + the 3 services
├── CLAUDE.md                # Agent guide — rules that load without being asked for
├── README.md                # How to run
└── docs/                    # This documentation
```

## Service anatomy (target layout — only user_service fully matches it)

```
<service>/
├── Dockerfile
└── app/
    ├── main.py              # FastAPI app, CORS, create_all, router include
    ├── db.py                # SQLAlchemy engine/session/Base + get_db dependency
    ├── models/              # SQLAlchemy models
    ├── schemas/             # Pydantic request/response models
    ├── routes/              # APIRouter per resource (prefix="/<resource>")
    └── events/              # RabbitMQ publishers/consumers (stub)
```

- **DB**: SQLite file per service (`<service>.db`), hardcoded in `db.py` — it is **not** actually read from the `DATABASE_URL` env var yet, despite the comment there saying otherwise (see [user_service/app/db.py](../user_service/app/db.py)). Only user_service has a working `db.py`; the other two are empty files.
- **Tables**: created by `Base.metadata.create_all(bind=engine)` in `main.py` (no Alembic yet).
- **Docker**: build context is repo root (`context: .`), but each Dockerfile copies only `common/requirements.txt`, then `COPY <service>/ .`. The `common/` package itself is **not** in the image, so `from common.x import ...` fails in Docker *and* locally (cwd is the service dir). A Dockerfile has to copy `common/` before any shared module can be imported.
- **Current status**: only user_service implements the full layout. product_service has `main.py` + `routes/` with a hardcoded list in the route — its `db.py`, `models/` and `schemas/` exist but are empty. order_service is empty files throughout.

## Ports & endpoints

| Service | Port | Base route | Notes |
|---|---|---|---|
| user_service | 8001 | `/users` | Full CRUD + `/users/login` (JWT) |
| product_service | 8002 | `/products` | Hardcoded list in the route — no DB, no models |
| order_service | 8003 | — | Empty files — no app, no routes |
| RabbitMQ | 5672 | — | Mgmt UI on 15672 |

user_service and product_service also expose `GET /` returning `{"service": ..., "status": "running"}`; order_service has no app to serve it.

## User service auth (current state)

- JWT via `python-jose`, HS256, 30-minute expiry — [user_routes.py](../user_service/app/routes/user_routes.py)
- Secret is hardcoded in the routes file (must move to env)
- Passwords are compared as plain text (passlib installed but unused)
- Token payload: `{"sub": "<user_id>", "email": ..., "exp": ...}` — no verification middleware anywhere yet

## Stack & versions

See [common/requirements.txt](../common/requirements.txt) — FastAPI 0.104, SQLAlchemy 2.0, pydantic 2.5, python-jose, passlib, pika/aio-pika (RabbitMQ), alembic, loguru. One shared requirements file for all services.

## Conventions to follow

- New code goes in the existing service layout — no new abstractions or packages unless a second service needs the same thing (then it moves to `common/` — and each Dockerfile must be updated to copy it first, or the image won't have it; see the Docker note above).
- Routes: `APIRouter(prefix="/<resource>", tags=["<resource>"])`, dependency-injected `db: Session = Depends(get_db)`.
- Errors: raise `HTTPException` with the specific status code + `detail` message (see user_routes for 400/401/404 patterns).
- Model → schema separation: SQLAlchemy models never appear directly in responses; declare `response_model`.
- Imports inside a service are `from app.xxx import ...` (Dockerfile runs uvicorn from the service dir).
- Commits: Conventional Commits, `<type>(<scope>): <description>` — types and scopes in [CLAUDE.md](../CLAUDE.md).

## How to run

```bash
docker compose up --build
# dev, per service:
cd user_service && uvicorn app.main:app --port 8001 --reload
```

FastAPI auto-docs: `http://localhost:8001/docs` etc.
