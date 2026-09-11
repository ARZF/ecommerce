# Current Status

> Snapshot of what works, what's stubbed, and what's missing.
> Agents: read this first. Update it after finishing any task.

Last updated: 2026-09-11

## Working

- **user_service** (port 8001) — full CRUD on SQLite (`user_service.db`): list/get/create/update/delete + JWT login at `POST /users/login`. JWT secret is hardcoded in [user_routes.py:16](../user_service/app/routes/user_routes.py#L16).
- **product_service** (port 8002) — `GET /products` returns 5 dummy in-memory products (no DB, no persistence).
- **order_service** (port 8003) — skeleton only: Dockerfile + empty module files.
- **frontend.html** — static single-file UI calling the services (CORS is wide open: `allow_origins=["*"]`).
- **docker-compose.yml** — runs RabbitMQ (5672 / mgmt UI 15672) + the three services.

## Stubbed / empty (files exist, no code)

- `common/config.py`, `common/events.py` — planned shared config and event bus helpers.
- `user_service/app/events/user_events.py`, `order_service/app/events/order_events.py` — planned RabbitMQ publishers/consumers.
- `order_service/` — all app modules empty (`db.py`, `main.py`, models, routes, schemas).

## Known gaps / TODO

1. **order_service is not implemented** — no models, routes, or DB.
2. **No RabbitMQ usage yet** — broker runs but no service publishes or consumes.
3. **Passwords stored in plain text** — `passlib[bcrypt]` is in requirements but unused. Hash on create/update, verify in login.
4. **JWT secret hardcoded** — move to env var; also no token verification middleware on protected routes.
5. **product_service has no persistence** — dummy list; needs a real model/DB like user_service.
6. **No product create/update/delete**, no stock, no cart.
7. **No tests anywhere.**
8. **No Alembic migrations** despite being in requirements — tables are created via `create_all` at startup.

## Local run

```bash
docker compose up --build        # all services + RabbitMQ
# or per-service dev run:
cd user_service && uvicorn app.main:app --port 8001
```

API docs per service at `http://localhost:<port>/docs` (FastAPI auto-docs).
