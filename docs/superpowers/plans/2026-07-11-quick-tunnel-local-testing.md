# Quick Tunnel Local Telegram Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in Cloudflare Quick Tunnel workflow that lets the owner test the existing Mini App inside Telegram from the current local workspace without configuring a custom domain.

**Architecture:** Keep the existing application stack unchanged and add a Compose overlay containing one ephemeral `cloudflared` service. The tunnel proxies a temporary HTTPS `trycloudflare.com` hostname to the existing Caddy service over the private Compose network, while Telegram secrets remain only in the ignored local `.env` file.

**Tech Stack:** Docker Compose, Cloudflare `cloudflared`, Caddy, Telegram Bot API, FastAPI, React/Vite

## Global Constraints

- Do not require a custom domain or router port forwarding.
- Do not commit `.env`, Telegram bot tokens, JWT secrets, admin secrets, or raw Telegram `initData`.
- Keep Telegram access restricted by `TELEGRAM_ALLOWED_USER_IDS`.
- Expose the Quick Tunnel only through Caddy; do not expose PostgreSQL through the tunnel.
- Use Quick Tunnel only for development and manual testing.

---

### Task 1: Add the opt-in Quick Tunnel service

**Files:**
- Create: `docker-compose.quick-tunnel.yml`
- Test: Docker Compose configuration validation

**Interfaces:**
- Consumes: the existing Compose service named `caddy`, reachable as `http://caddy:80`
- Produces: an opt-in Compose service named `cloudflared` whose logs contain the temporary public HTTPS URL

- [ ] **Step 1: Verify the overlay does not exist yet**

Run:

```bash
test ! -e docker-compose.quick-tunnel.yml
```

Expected: exit code `0`.

- [ ] **Step 2: Create the Quick Tunnel overlay**

Create `docker-compose.quick-tunnel.yml` with:

```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    command:
      - tunnel
      - --no-autoupdate
      - --url
      - http://caddy:80
    depends_on:
      caddy:
        condition: service_started
    restart: "no"
```

- [ ] **Step 3: Validate the combined Compose configuration**

Run:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.quick-tunnel.yml \
  config --quiet
```

Expected: exit code `0` with no output.

- [ ] **Step 4: Commit the overlay**

```bash
git add docker-compose.quick-tunnel.yml
git commit -m "feat(dev): add quick tunnel service" \
  -m "Provide an opt-in Cloudflare tunnel for local Telegram testing."
```

### Task 2: Document the manual Telegram test runbook

**Files:**
- Create: `docs/quick-tunnel-testing.md`
- Modify: `README.md`
- Test: documented command validation and repository secret scan

**Interfaces:**
- Consumes: `docker-compose.quick-tunnel.yml`, `.env.example`, and the existing migration and seed commands
- Produces: exact owner-facing commands for configuration, startup, URL discovery, bot recreation, verification, and shutdown

- [ ] **Step 1: Write the runbook**

Create `docs/quick-tunnel-testing.md` with these sections and exact commands:

````markdown
# Telegram testing with Cloudflare Quick Tunnel

This workflow exposes the local Caddy service through a temporary HTTPS URL. It is intended only for manual development testing.

## 1. Configure local secrets

Copy `.env.example` to the ignored `.env` file and set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS`, `JWT_SECRET`, and `ADMIN_SECRET`. Do not paste these values into chat or commit `.env`.

## 2. Start and initialize the application

```bash
docker compose up -d --build postgres api mini-app caddy
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed_curated_exercises --input /data/curated_exercises.seed.json
docker compose exec api python -m app.scripts.seed_workout_templates
```

Import the external exercise dataset when it exists at `data/exercises-dataset/data/exercises.json`:

```bash
docker compose exec api python -m app.scripts.import_exercises --input /data/exercises-dataset/data/exercises.json
```

## 3. Start the temporary tunnel

```bash
docker compose -f docker-compose.yml -f docker-compose.quick-tunnel.yml up -d cloudflared
docker compose -f docker-compose.yml -f docker-compose.quick-tunnel.yml logs -f cloudflared
```

Copy the generated `https://...trycloudflare.com` URL. Stop following logs with `Ctrl+C`; leave the container running.

## 4. Point the bot at the tunnel

Set these values in `.env`:

```env
APP_URL=https://generated-name.trycloudflare.com
MINI_APP_URL=https://generated-name.trycloudflare.com
API_URL=http://api:8000
```

Start or recreate the bot:

```bash
docker compose up -d --force-recreate bot
```

## 5. Verify

```bash
curl http://localhost:8080/api/health
docker compose ps
docker compose logs --tail=100 api bot
```

Open the bot in Telegram, run `/start`, and launch the Mini App. Verify today's workout, set entry, exercise completion, workout completion, and history.

## 6. Stop

```bash
docker compose -f docker-compose.yml -f docker-compose.quick-tunnel.yml down
```

Every new Quick Tunnel container may receive a different hostname. When it changes, update `.env` and recreate the bot again.
````

- [ ] **Step 2: Link the runbook from README**

Add this paragraph after the local URL list in `README.md`:

```markdown
To test the Mini App inside Telegram without configuring a custom domain, follow [the Cloudflare Quick Tunnel runbook](docs/quick-tunnel-testing.md).
```

- [ ] **Step 3: Validate the documented Compose command**

Run:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.quick-tunnel.yml \
  config --quiet
```

Expected: exit code `0` with no output.

- [ ] **Step 4: Verify no local secrets are tracked**

Run:

```bash
git ls-files .env
git diff --check
```

Expected: `git ls-files .env` prints nothing and `git diff --check` exits with code `0`.

- [ ] **Step 5: Commit the runbook**

```bash
git add README.md docs/quick-tunnel-testing.md
git commit -m "docs: add quick tunnel test runbook" \
  -m "Document local Telegram startup, verification, and shutdown."
```

### Task 3: Verify the complete repository before local deployment

**Files:**
- Test only; no tracked files change

**Interfaces:**
- Consumes: the completed Quick Tunnel overlay and runbook
- Produces: fresh verification evidence before the local stack is started with owner-provided secrets

- [ ] **Step 1: Run API checks**

```bash
cd apps/api
.venv/bin/python -m ruff check app tests
.venv/bin/python -m pytest tests -q
```

Expected: Ruff exits `0` and all API tests pass.

- [ ] **Step 2: Run bot checks**

```bash
cd apps/bot
.venv/bin/python -m ruff check app tests
.venv/bin/python -m pytest tests -q
```

Expected: Ruff exits `0` and all bot tests pass.

- [ ] **Step 3: Run Mini App checks**

```bash
cd apps/mini-app
npm test -- --run
npm run build
```

Expected: all Vitest tests pass and Vite completes a production build.

- [ ] **Step 4: Confirm final repository state**

```bash
git status --short
git log --oneline -3
```

Expected: no uncommitted tracked changes and the two implementation commits appear after the design and plan commits.
