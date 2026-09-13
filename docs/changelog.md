# Changelog

> Append-only log of meaningful changes. Newest first.
> Agents: add one entry per completed task. Keep it short — details belong in git history.

Format: `YYYY-MM-DD — <what changed> — <files/services touched>`

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
