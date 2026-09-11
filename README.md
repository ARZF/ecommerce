# E-Commerce Microservices

FastAPI microservices + RabbitMQ + static frontend.

- **user_service** (8001) — users + JWT login (SQLite)
- **product_service** (8002) — products (dummy data)
- **order_service** (8003) — orders (skeleton)
- **RabbitMQ** (5672, mgmt UI 15672)

## Run

```bash
docker compose up --build
```

API docs: `http://localhost:8001/docs`, `:8002/docs`, `:8003/docs`

## Documentation

See [docs/](docs/) — status, plan, changelog, and project reference for agents.
