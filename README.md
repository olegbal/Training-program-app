# Training Agent

Personal Telegram training tracker with a FastAPI backend, aiogram bot, and Telegram Mini App frontend.

## Current Status

Phase 1 project skeleton is in progress:

- FastAPI API with `/health`.
- PostgreSQL service.
- Telegram bot skeleton with `/start`, `/today`, `/history`, and `/help`.
- Vite React Mini App skeleton.
- Caddy reverse proxy for local development.

Workout templates, Telegram Mini App authentication, exercise import, set logging, and history are planned for later phases in `AGENTS.md`.

## Local Development

Copy environment placeholders if you want local overrides:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up --build
```

Development URLs:

- Mini App through Caddy: `http://localhost:8080`
- API through Caddy: `http://localhost:8080/api/health`
- API direct: `http://localhost:8000/health`
- Vite direct: `http://localhost:5173`

With the default `TELEGRAM_BOT_TOKEN=replace_me`, the bot container starts in idle mode and does not poll Telegram.

## Backend Tests

```bash
cd apps/api
python -m pytest tests -q
```
