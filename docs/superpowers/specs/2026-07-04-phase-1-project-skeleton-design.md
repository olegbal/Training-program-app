# Phase 1 Project Skeleton Design

## Scope

Phase 1 completes the runnable repository skeleton for the personal Telegram fitness tracker. The existing FastAPI backend foundation stays in place. This slice adds the missing bot, Mini App, Caddy reverse proxy, README, and Docker Compose wiring required by `AGENTS.md`.

## Architecture

The repository runs five services in development:

- `postgres`: PostgreSQL 17 with a healthcheck and persistent volume.
- `api`: FastAPI service exposing `/health`.
- `bot`: aiogram v3 service with `/start`, `/today`, `/history`, and `/help` handlers. It uses the same API URL and Mini App URL settings that later phases will use.
- `mini-app`: Vite React app served by the Vite development server in Docker.
- `caddy`: reverse proxy for `/api/*` to the API and all other traffic to the Mini App.

The bot does not require a real Telegram token to keep local `docker compose up --build` usable. When `TELEGRAM_BOT_TOKEN=replace_me`, it starts in idle mode and logs that polling is disabled.

## Boundaries

This phase does not implement Telegram Mini App authentication, exercise import, workout sessions, workout templates, AI routes, or production Caddy hardening. Those belong to later phases in `AGENTS.md`.

## Verification

Run backend tests from the repository root:

```bash
cd apps/api && python -m pytest tests -q
```

Run the full development stack:

```bash
docker compose up --build
```

The acceptance condition is that all services build and start without crashing.
