# Current Status

> Snapshot of what works, what's stubbed, and what's missing.
> Agents: read this first. Update it after finishing any task.

Last updated: 2026-09-14

## Working

- **user_service** (port 8001) — full CRUD on SQLite (`user_service.db`): list/get/create/update/delete + JWT login at `POST /users/login`. Passwords are bcrypt-hashed; the JWT secret and expiry come from [common/config.py](../common/config.py) (`JWT_SECRET` / `JWT_EXPIRE_MINUTES`, dev fallback). Run `python check_auth.py` for an assertion pass.
- **product_service** (port 8002) — full CRUD on SQLite (`product_service.db`): list/get/create/update/delete. Seeds the 5 original dummy products on startup when the table is empty, so the frontend still has data. Run `python check_products.py` for an assertion pass.
- **order_service** (port 8003) — full CRUD on SQLite (`order_service.db`): list/get/create/update/delete, plus `GET /orders/user/{user_id}`. `status` defaults to `pending`. On startup it also consumes `user.created` and logs it. Run `python check_orders.py` from the service dir for an end-to-end assertion pass.
- **RabbitMQ events** — user_service publishes `user.created` after a user is created; order_service consumes it and logs it. Shared helpers in [common/events.py](../common/events.py). Verified end to end against a live broker with `python check_events.py`.
- **frontend.html** — static single-file UI calling the services (CORS is wide open: `allow_origins=["*"]`).
- **docker-compose.yml** — runs RabbitMQ (5672 / mgmt UI 15672) + the three services, with a broker healthcheck gating startup and `RABBITMQ_URL` set for the two that use it.

## Stubbed / empty (files exist, no code)

- Nothing left — every module in the layout now has code. (product_service has no `app/events/` directory at all.)

## Known gaps / TODO

1. **Events are fire-and-forget** — no outbox, retry or DLQ. A failed publish is logged and dropped, and only `user.created` exists so far (no `order.created` / `product.updated`). The consumer logs; it does not act on the event.
2. **No token verification** — nothing validates the JWT on protected routes, and product/order routes have no auth at all; CORS is still `allow_origins=["*"]` (plan §4 items 3-4).
3. **No cart / order-to-product link** — order_service stores a bare `product_id`; nothing decrements `products.stock` when an order is placed.
4. **No tests anywhere** — beyond the ad-hoc `check_auth.py`, `check_products.py`, `check_orders.py` and `check_events.py` scripts.
5. **No Alembic migrations** despite being in requirements — tables are created via `create_all` at startup.
6. **`total_price` is client-supplied** — order_service has no product price lookup, so the total is whatever the caller sends (nothing checks it against product_service).
7. **`DATABASE_URL` is hardcoded** in each `db.py` — the comment there claims an env override that doesn't exist.
8. **`JWT_SECRET` falls back to a committed default** — fine for dev, but the fallback must go before anything real ships.

## Local run

```bash
docker compose up --build        # all services + RabbitMQ
# or per-service dev run:
cd user_service && uvicorn app.main:app --port 8001
```

API docs per service at `http://localhost:<port>/docs` (FastAPI auto-docs).
