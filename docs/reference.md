# Reference — Project Structure & Conventions

> For agents (and humans): how this codebase is laid out, how each service works, and the conventions to follow when extending it.

## Top-level layout

```
ecommerce/
├── common/                  # Shared code — config.py (JWT/env settings), events.py (RabbitMQ helpers)
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
- Secret and expiry come from [common/config.py](../common/config.py): `JWT_SECRET` / `JWT_EXPIRE_MINUTES` env vars, with a dev fallback baked in. The fallback is a real secret in the repo — set the env var outside development.
- Passwords are bcrypt-hashed via passlib `CryptContext` on create and update, and verified on login. A row still holding a pre-hashing plaintext password gets a 401, not a 500 (the `UnknownHashError` is caught) — but it can never log in, so re-set it.
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

## Events (RabbitMQ)

- [common/events.py](../common/events.py) is the only place that touches aio-pika: `publish(exchange, routing_key, payload)` and `consume(queue, callback, exchange=None, routing_key=None)`. Payloads are JSON; `consume` hands the callback a decoded `dict`.
- `RABBITMQ_URL` comes from the environment, defaulting to `amqp://guest:guest@localhost/`. compose sets it to the `rabbitmq` service name for user_service and order_service.
- The wiring depends on two shared constants in that module, `USER_EVENTS_EXCHANGE` (`"user_events"`, a durable topic exchange) and `USER_CREATED` (`"user.created"`). Both sides import them — a typo'd string literal here would silently drop every event, so don't inline the names.
- Publisher: [user_events.py](../user_service/app/events/user_events.py) `publish_user_created(user)`, called at the end of `create_user`. It is **best-effort** — a broker outage logs a warning and the user is still created (verified: 201 with the broker stopped). It opens one connection per event.
- Consumer: [order_events.py](../order_service/app/events/order_events.py) owns the queue `order_service.user_created`, bound to the exchange with routing key `user.created`. main.py starts it as an `asyncio` task in the FastAPI lifespan and cancels it on shutdown. It only logs — it is not a saga.
- `publish` uses `aio_pika.connect` (fails fast); `consume` uses `connect_robust` (retries until the broker is up, which covers ordering against the compose healthcheck).
- Nothing is durable across a broker wipe beyond the declared queue: user_service declares the exchange but no queue, so events published before the consumer has ever run are dropped.
- End-to-end check: `docker compose up -d rabbitmq && python check_events.py`.

## Stack & versions

See [common/requirements.txt](../common/requirements.txt) — FastAPI 0.104, SQLAlchemy 2.0, pydantic 2.5, python-jose, passlib + bcrypt, pika/aio-pika (RabbitMQ), alembic, loguru. One shared requirements file for all services. `bcrypt` is pinned to 4.3.0 on purpose — passlib 1.7.4 raises `ValueError` on bcrypt 5.x's 72-byte password check, which breaks hashing entirely.

## Conventions to follow

- New code goes in the existing service layout — no new abstractions or packages unless a second service needs the same thing (then it moves to `common/` — and each Dockerfile must be updated to copy it first, or the image won't have it; see the Docker note above).
- Routes: `APIRouter(prefix="/<resource>", tags=["<resource>"])`, dependency-injected `db: Session = Depends(get_db)`.
- Errors: raise `HTTPException` with the specific status code + `detail` message (see user_routes for 400/401/404 patterns).
- Model → schema separation: SQLAlchemy models never appear directly in responses; declare `response_model`.
- Imports inside a service are `from app.xxx import ...` (Dockerfile runs uvicorn from the service dir).
- Shared code is imported as `from common.xxx import ...`. That only resolves when the **repo root** is importable: in Docker `WORKDIR` is `/app`, which holds both `common/` and `app/`, but a local `cd <service> && uvicorn ...` has the service dir as cwd and raises `ModuleNotFoundError: No module named 'common'` — set `PYTHONPATH` to the repo root (see How to run).
- Commits: Conventional Commits, `<type>(<scope>): <description>` — types and scopes in [CLAUDE.md](../CLAUDE.md).

## How to run

```bash
docker compose up --build
# dev, per service (PYTHONPATH is required for `from common.x import ...`):
cd user_service && PYTHONPATH=.. uvicorn app.main:app --port 8001 --reload
```

On PowerShell: `$env:PYTHONPATH=".."; uvicorn app.main:app --port 8001 --reload`

FastAPI auto-docs: `http://localhost:8001/docs` etc.
