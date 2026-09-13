# AGENTS.md

E-commerce microservices — FastAPI + RabbitMQ + a static frontend. Three services
(user/product/order), one shared requirements file. See [README.md](README.md) to run.

## Read first

[docs/status.md](docs/status.md) → [plan.md](docs/plan.md) → [reference.md](docs/reference.md) → [changelog.md](docs/changelog.md).

`reference.md` is the source of truth for layout, endpoints and conventions. Don't restate it
here — this file only carries the rules that must load without being asked for, plus the traps.

## After every task (required by docs/README.md)

- Update `docs/status.md`; add a line to `docs/changelog.md` (`YYYY-MM-DD — what changed — files`); tick the item off in `docs/plan.md`.
- Structural change (new route, model, file)? Update `docs/reference.md` too.

## Match the code that's already here

Any agent writing code follows the pattern of the neighbouring files — same structure, naming,
error handling and comment density. Read the closest existing file before writing a new one.

For an endpoint that means copying the shape in [user_routes.py](user_service/app/routes/user_routes.py):
`APIRouter(prefix="/<resource>", tags=["<resource>"])`, `db: Session = Depends(get_db)`,
`HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="...")`, a `response_model`, and
SQLAlchemy models never returned directly. Imports inside a service are `from app.xxx import ...`.

Match the style, not the security debt: the hardcoded JWT secret and plaintext password
comparison in `user_routes.py` are known gaps (noted in reference.md), not a pattern to copy
into new code.

## Commit messages — Conventional Commits

```
<type>(<scope>): <description>
```

Imperative mood, lowercase, no trailing period, subject ≤ 72 chars. Write it as the change
itself ("add", not "added"/"adds").

**Types:** `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `style`, `revert`.

**Scope** is the part of the repo touched — `user_service`, `product_service`, `order_service`,
`common`, `docker`, `docs`. Drop the scope when the change genuinely spans everything.

```
feat(user_service): hash passwords on create
fix(order_service): return 404 for an unknown order id
docs(changelog): log the AGENTS.md addition
chore(deps): pin aio-pika to 9.4.2
refactor(common): move the pika connection helper out of events
```

**Breaking changes:** `!` after the type or scope, plus a `BREAKING CHANGE:` footer saying what
callers must do differently.

```
feat(user_service)!: make password_hash write-only in responses

BREAKING CHANGE: UserOut no longer returns password_hash.
```

Use a body only when the *why* isn't clear from the subject — don't pad. Subject only is fine
for most changes here. The existing history is a single non-conventional commit (`first commit`),
so there's nothing to stay consistent with; this applies from here on.

## Gotchas

- **`common/` is not in the images.** Each Dockerfile copies `common/requirements.txt` only,
  then `COPY <service>/ .` — so at runtime `from common.x import ...` fails in Docker *and*
  locally (cwd is the service dir). Shared code must be copied by the Dockerfile before it can
  be imported. reference.md says the Dockerfiles copy `common/`; it's wrong.
- **Ports:** host `8001/8002/8003` → container `8000`.
- **Dependencies:** one file for everything, [common/requirements.txt](common/requirements.txt).
  Add there, then `docker compose up --build`.
- **No migrations despite `alembic` being installed.** Tables come from
  `Base.metadata.create_all(bind=engine)` in each `main.py`. A new model must be imported in
  `main.py` above that call (see the `# noqa: F401` note) or its table is never created.
- **No test setup** — no framework, no fixtures, nothing in the repo. Leave the smallest
  runnable check (a script or a few asserts) instead of introducing a suite.
