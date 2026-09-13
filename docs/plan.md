# Plan / Roadmap

> What's next, in priority order. Agents: check off items in [status.md](status.md) when done and move them to [changelog.md](changelog.md).

## 1. Finish order_service (highest priority) — done 2026-09-14

- [x] `db.py` — copy user_service pattern (SQLite + SQLAlchemy)
- [x] `order_model.py` — Order (id, user_id, product_id, quantity, total_price, status, created_at)
- [x] `order_schema.py` — OrderCreate / OrderOut
- [x] `order_routes.py` — CRUD + `GET /orders/user/{user_id}`
- [x] `main.py` — same FastAPI setup as user_service

## 2. Make product_service real — done 2026-09-14

- [x] Product model + SQLite persistence (mirror user_service)
- [x] Full CRUD (create / update / delete, admin-style)
- [x] Seed script for the current dummy products

## 3. RabbitMQ event bus

- [ ] Implement `common/events.py` — shared publish/subscribe helpers (aio-pika is already in requirements)
- [ ] Events: `user.created`, `order.created`, `product.updated`
- [ ] order_service consumes `user.created` / product data instead of sync HTTP where sensible

## 4. Security hardening

- [ ] Hash passwords with passlib bcrypt (create, update, login verify)
- [ ] JWT secret + expiry from env vars (shared `common/config.py`)
- [ ] Token-verification dependency on protected routes
- [ ] Restrict CORS origins

## 5. Quality / ops

- [ ] Alembic migrations instead of `create_all` at startup
- [ ] Tests (pytest + httpx against the FastAPI test client, one test file per service)
- [ ] Logging via loguru (already in requirements)
- [ ] Health checks in docker-compose

## Decisions / notes

- Stack: FastAPI + SQLAlchemy + SQLite (dev) — Postgres driver already in requirements if we outgrow SQLite.
- Pattern: each service is self-contained (own db.py, models, routes); `common/` is for genuinely shared code only.
- Auth: per-service JWT with a shared secret (single user_service issues tokens for now).
