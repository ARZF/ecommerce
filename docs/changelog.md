# Changelog

> Append-only log of meaningful changes. Newest first.
> Agents: add one entry per completed task. Keep it short — details belong in git history.

Format: `YYYY-MM-DD — <what changed> — <files/services touched>`

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
