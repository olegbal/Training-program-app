# Backend Foundation

## Scope

This slice creates the API foundation for the personal Telegram training app:

- FastAPI app factory and `/health`.
- Pydantic settings loaded from environment variables.
- SQLAlchemy 2.x declarative models for the MVP schema.
- Alembic scaffold with an initial PostgreSQL migration.
- Docker Compose services for `postgres` and `api`.

## Current Boundaries

Business endpoints, Telegram auth, exercise import, workout templates, bot, and Mini App are intentionally left for later vertical slices.

## Verification

Run from the repository root:

```bash
.venv/bin/python -m pytest apps/api/tests -q
```
