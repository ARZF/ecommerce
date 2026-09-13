# Changelog

> Append-only log of meaningful changes. Newest first.
> Agents: add one entry per completed task. Keep it short — details belong in git history.

Format: `YYYY-MM-DD — <what changed> — <files/services touched>`

## 2026-09-14 — minimal RabbitMQ event flow (plan §3) — `common/events.py`, `user_service/app/*`, `order_service/app/*`, `docker-compose.yml`, `check_events.py`, `docs/*`

- `common/events.py` — shared `publish(exchange, routing_key, payload)` and `consume(queue, callback, ...)` over aio-pika, with `RABBITMQ_URL` from the environment and a localhost fallback
- user_service publishes `user.created` from `create_user` via `app/events/user_events.py` — best-effort, so a broker outage warns and still returns 201 (verified with the broker stopped)
- order_service consumes it in `app/events/order_events.py`, started as a background task in the FastAPI lifespan; it only logs
- compose: broker healthcheck, `condition: service_healthy` on `depends_on`, and `RABBITMQ_URL` for user_service and order_service
- `check_events.py` — round-trips an event through a real broker (ran green against rabbitmq:3-management)
- `check_orders.py` / `check_products.py` now put the repo root on `sys.path` — order_service imports `common/`, so the old single-dir path broke it

## 2026-09-14 — security hardening: bcrypt passwords + env-backed JWT config (plan §4.1-4.2) — `common/config.py`, `common/requirements.txt`, `user_service/app/routes/user_routes.py`, `user_service/check_auth.py`, `docs/*`

- Passwords are bcrypt-hashed via a passlib `CryptContext` on create and update, verified on login — no response or endpoint changes
- JWT secret and expiry moved out of user_routes into `common/config.py`, read from `JWT_SECRET` / `JWT_EXPIRE_MINUTES` with a dev fallback
- `bcrypt==4.3.0` pinned in requirements — passlib 1.7.4 raises `ValueError` on bcrypt 5.x's 72-byte password check, so an unpinned install would break hashing on the next build
- Rows still holding a pre-hashing plaintext password get a clean 401 instead of a 500 (`UnknownHashError` caught); they can't log in, so the password must be re-set
- `check_auth.py` — assertion pass covering hash-at-rest, re-hash on update, wrong/unknown credentials, legacy rows, and the env-secret wiring (ran green)
- First real consumer of `common/`: a local `cd <service> && uvicorn app.main:app` now needs `PYTHONPATH=..` (Docker is unaffected). Documented in reference.md.

## 2026-09-14 — give product_service real persistence (plan §2) — `product_service/app/*`, `product_service/check_products.py`, `docs/*`

- `Product` model (`name`, `price`, `description`, `stock`, `created_at`) + `ProductCreate`/`ProductUpdate`/`ProductOut`; `db.py` and `main.py` mirror user_service
- Replaced the hardcoded `DUMMY_PRODUCTS` list with DB-backed CRUD on `/products` — 404s only, no `name` uniqueness check (unlike `email` in user_routes)
- `app/seed.py` inserts the 5 original dummy products only when the table is empty, so the frontend still gets data and ids stay 1-5
- `check_products.py` — assertion pass over the routes, incl. seed idempotency and the frontend-visible fields (ran green)
- Same pydantic `Field` validation (422) as order_service

## 2026-09-14 — implement order_service (plan §1) — `order_service/app/*`, `order_service/check_orders.py`, `docs/*`

- `db.py`, `main.py` mirror user_service; `Order` model + `OrderCreate`/`OrderUpdate`/`OrderOut` schemas
- `/orders` full CRUD + `GET /orders/user/{user_id}`; `status` defaults to `pending`
- Added `models/__init__.py`, `schemas/__init__.py` to match user_service layout
- `check_orders.py` — framework-free assertion pass over the routes (ran green)
- Deliberate deviation from user_routes style: input validation (`quantity >= 1`, `total_price >= 0`) uses pydantic `Field` constraints → 422, not a manual `HTTPException` 400
- Docs: plan §1 checked off, status/reference updated (order_service no longer empty; stale Docker note corrected)

## 2026-09-14 — copy `common/` into all three images — `user_service/Dockerfile`, `product_service/Dockerfile`, `order_service/Dockerfile`

- Each Dockerfile now does `COPY common/ ./common/` before the service code, so `from common.x import ...` resolves at `/app`

## 2026-09-12 — correct reference.md against the actual code — `docs/reference.md`

- Dockerfiles copy only `common/requirements.txt`, not `common/` — imports of it fail in the image
- `DATABASE_URL` is hardcoded in `db.py`, not read from env as the note claimed
- Per-service status: only user_service is complete; product has no DB/models; order is empty files

## 2026-09-12 — document Conventional Commits for commit messages — `CLAUDE.md`

- Types, scopes (`user_service`/`product_service`/`order_service`/`common`/`docker`/`docs`), breaking-change form, examples

## 2026-09-11 — add root CLAUDE.md for agents — `CLAUDE.md`

- Root agent guide: docs read order, doc-update protocol, match-existing-code rule, gotchas
- Notes that `common/` isn't copied into the images (reference.md claims otherwise)

## 2025-11-25 — initial commit (b712aa0)

- user_service: full CRUD + JWT login on SQLite — `user_service/app/*`
- product_service: `GET /products` with dummy data — `product_service/app/routes/product_routes.py`
- order_service: skeleton files only
- docker-compose with RabbitMQ + 3 services
- frontend.html static UI
- common/ shared package: requirements.txt only (config.py, events.py empty)
