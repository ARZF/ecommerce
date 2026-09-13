# Reference — Project Structure & Conventions

> For agents (and humans): how this codebase is laid out, how each service works, and the conventions to follow when extending it.

## Top-level layout

```
ecommerce/
├── common/                  # Shared code — empty stubs; only requirements.txt has content
├── user_service/            # FastAPI service — port 8001 (only service with auth)
├── product_service/         # FastAPI service — port 8002 (products CRUD on SQLite, seeded)
├── order_service/           # FastAPI service — port 8003 (orders CRUD on SQLite)
├── frontend.html            # Static single-file UI
├── docker-compose.yml       # RabbitMQ + the 3 services
├── CLAUDE.md                # Agent guide — rules that load without being asked for
├── README.md                # How to run
└── docs/                    # This documentation
```

## Service anatomy (all three services match it)

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

- **DB**: SQLite file per service (`<service>.db`), hardcoded in `db.py` — it is **not** actually read from the `DATABASE_URL` env var yet, despite the comment there saying otherwise (see [user_service/app/db.py](../user_service/app/db.py)). All three services now have a working `db.py`.
- **Tables**: created by `Base.metadata.create_all(bind=engine)` in `main.py` (no Alembic yet).
- **Docker**: build context is repo root (`context: .`). Each Dockerfile copies `common/requirements.txt` for pip, then `common/` (so `from common.x import ...` resolves at `/app`), then `COPY <service>/ .`.
- **Current status**: all three services implement the full layout, each with its own SQLite file. product_service seeds its 5 dummy products at startup (see below); user_service is the only one with auth.

## Ports & endpoints

| Service | Port | Base route | Notes |
|---|---|---|---|
| user_service | 8001 | `/users` | Full CRUD + `/users/login` (JWT) |
| product_service | 8002 | `/products` | Full CRUD on SQLite; seeded with 5 products on first start |
| order_service | 8003 | `/orders` | Full CRUD on SQLite + `GET /orders/user/{user_id}` |
| RabbitMQ | 5672 | — | Mgmt UI on 15672 |

All three services expose `GET /` returning `{"service": ..., "status": "running"}`.

## User service auth (current state)

- JWT via `python-jose`, HS256, 30-minute expiry — [user_routes.py](../user_service/app/routes/user_routes.py)
- Secret is hardcoded in the routes file (must move to env)
- Passwords are compared as plain text (passlib installed but unused)
- Token payload: `{"sub": "<user_id>", "email": ..., "exp": ...}` — no verification middleware anywhere yet

## Order service (current state)

- `orders` table: `id`, `user_id`, `product_id`, `quantity`, `total_price`, `status` (default `pending`), `created_at`.
- `total_price` is supplied by the client — nothing looks the product up, so it isn't validated against product_service.
- `quantity >= 1` and `total_price >= 0` are enforced by pydantic `Field` constraints (422, not 400).
- No auth on any route — `user_id` is trusted from the body.

## Product service (current state)

- `products` table: `id`, `name`, `price`, `description`, `stock` (default `0`), `created_at`.
- [app/seed.py](../product_service/app/seed.py) holds `DUMMY_PRODUCTS` (the 5 items the route used to hardcode) and `seed_products(db)`, which is a no-op unless the table is empty — so ids stay 1-5 on a fresh DB and the frontend keeps working. main.py calls it at startup after `create_all`.
- There is no uniqueness check on `name` (unlike `email` in user_routes) — product names aren't a natural key, so the routes only raise 404.
- No auth — anyone can create/update/delete products.

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
