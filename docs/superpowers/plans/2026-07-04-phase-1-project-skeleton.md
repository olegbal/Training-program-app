# Phase 1 Project Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable five-service project skeleton for the Training Agent MVP.

**Architecture:** Keep the existing FastAPI backend foundation and add skeletal bot, Mini App, and Caddy services. Docker Compose wires `postgres`, `api`, `bot`, `mini-app`, and `caddy` so local development can start with one command.

**Tech Stack:** Python 3.12, FastAPI, aiogram v3, React, TypeScript, Vite, Docker Compose, Caddy.

---

### Task 1: Documentation

**Files:**
- Create: `docs/superpowers/specs/2026-07-04-phase-1-project-skeleton-design.md`
- Create: `docs/superpowers/plans/2026-07-04-phase-1-project-skeleton.md`
- Create: `README.md`

- [ ] Record the Phase 1 scope and acceptance criteria.
- [ ] Document local run commands and service URLs.

### Task 2: Bot Skeleton

**Files:**
- Create: `apps/bot/app/config.py`
- Create: `apps/bot/app/handlers.py`
- Create: `apps/bot/app/main.py`
- Create: `apps/bot/app/__init__.py`
- Create: `apps/bot/pyproject.toml`
- Create: `apps/bot/Dockerfile`
- Create: `apps/bot/.dockerignore`

- [ ] Add Pydantic settings for bot token, API URL, Mini App URL, and allowed IDs.
- [ ] Add aiogram handlers for `/start`, `/today`, `/history`, and `/help`.
- [ ] Make placeholder tokens start an idle process instead of crashing.
- [ ] Add a non-root Docker runtime.

### Task 3: Mini App Skeleton

**Files:**
- Create: `apps/mini-app/src/main.tsx`
- Create: `apps/mini-app/src/App.tsx`
- Create: `apps/mini-app/src/api/client.ts`
- Create: `apps/mini-app/src/components/StatusPill.tsx`
- Create: `apps/mini-app/src/screens/TodayScreen.tsx`
- Create: `apps/mini-app/src/types/telegram.d.ts`
- Create: `apps/mini-app/src/styles.css`
- Create: `apps/mini-app/package.json`
- Create: `apps/mini-app/package-lock.json`
- Create: `apps/mini-app/tsconfig.json`
- Create: `apps/mini-app/tsconfig.node.json`
- Create: `apps/mini-app/vite.config.ts`
- Create: `apps/mini-app/index.html`
- Create: `apps/mini-app/Dockerfile`
- Create: `apps/mini-app/.dockerignore`

- [ ] Add a simple Today screen that can run before backend workout endpoints exist.
- [ ] Add Telegram WebApp type declarations without trusting `initDataUnsafe`.
- [ ] Add a Vite Docker image that runs as a non-root user and installs dependencies with `npm ci`.

### Task 4: Compose and Proxy

**Files:**
- Modify: `docker-compose.yml`
- Create: `Caddyfile`

- [ ] Add `bot`, `mini-app`, and `caddy` services.
- [ ] Mount the dataset path read-only for the API.
- [ ] Proxy `/api/*` to the backend and frontend traffic to Vite.

### Task 5: Verification

**Commands:**
- `cd apps/api && python -m pytest tests -q`
- `docker compose config`
- `docker compose build api bot mini-app caddy`

- [ ] Run backend tests.
- [ ] Validate Compose syntax.
- [ ] Build all Docker images that can be built in the current environment.
