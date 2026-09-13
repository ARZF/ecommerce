# Current Status

> Snapshot of what works, what's stubbed, and what's missing.
> Agents: read this first. Update it after finishing any task.

Last updated: 2026-09-14

## Working

- **user_service** (port 8001) — full CRUD on SQLite (`user_service.db`): list/get/create/update/delete + JWT login at `POST /users/login`. JWT secret is hardcoded in [user_routes.py:16](../user_service/app/routes/user_routes.py#L16).
- **product_service** (port 8002) — full CRUD on SQLite (`product_service.db`): list/get/create/update/delete. Seeds the 5 original dummy products on startup when the table is empty, so the frontend still has data. Run `python check_products.py` for an assertion pass.
- **order_service** (port 8003) — full CRUD on SQLite (`order_service.db`): list/get/create/update/delete, plus `GET /orders/user/{user_id}`. `status` defaults to `pending`; run `python check_orders.py` from the service dir for an end-to-end assertion pass.
- **frontend.html** — static single-file UI calling the services (CORS is wide open: `allow_origins=["*"]`).
- **docker-compose.yml** — runs RabbitMQ (5672 / mgmt UI 15672) + the three services.

## Stubbed / empty (files exist, no code)

- `common/config.py`, `common/events.py` — planned shared config and event bus helpers.
- `user_service/app/events/user_events.py`, `order_service/app/events/order_events.py` — planned RabbitMQ publishers/consumers.

## Known gaps / TODO

1. **No RabbitMQ usage yet** — broker runs but no service publishes or consumes.
2. **Passwords stored in plain text** — `passlib[bcrypt]` is in requirements but unused. Hash on create/update, verify in login.
3. **JWT secret hardcoded** — move to env var; also no token verification middleware on protected routes.
4. **No cart / order-to-product link** — order_service stores a bare `product_id`; nothing decrements `products.stock` when an order is placed.
5. **No tests anywhere** — beyond the ad-hoc `order_service/check_orders.py` and `product_service/check_products.py` scripts.
6. **No Alembic migrations** despite being in requirements — tables are created via `create_all` at startup.
7. **`total_price` is client-supplied** — order_service has no product price lookup, so the total is whatever the caller sends (nothing checks it against product_service).
8. **`DATABASE_URL` is hardcoded** in each `db.py` — the comment there claims an env override that doesn't exist.

## Local run

```bash
docker compose up --build        # all services + RabbitMQ
# or per-service dev run:
cd user_service && uvicorn app.main:app --port 8001
```

API docs per service at `http://localhost:<port>/docs` (FastAPI auto-docs).
