# Training Agent

Personal Telegram training tracker with a FastAPI backend, PostgreSQL, aiogram bot, and Telegram Mini App frontend.

The app is built for one allowed Telegram user, not as a public SaaS product.

## What Is Implemented

- Telegram Mini App authentication through signed Telegram `initData`.
- JWT-protected workout API.
- Exercise import from `olegbal/exercises-dataset`.
- Curated exercise metadata and default weekly workout templates.
- Today's workout, session start/complete/skip, exercise complete/skip/replace.
- Set logging, set update/delete, workout history.
- React Mini App screens: Today, Workout, History, Exercise Library, GIF modal.
- Telegram bot commands: `/start`, `/today`, `/history`, `/help`.
- AI/OpenClaw placeholder routes and `WorkoutValidator`.

## Runtime Services

Docker Compose starts:

- `postgres` - PostgreSQL database.
- `api` - FastAPI backend.
- `bot` - Telegram bot.
- `mini-app` - Vite React Mini App.
- `caddy` - local reverse proxy.

Local URLs:

- Mini App through Caddy: `http://localhost:8080`
- API through Caddy: `http://localhost:8080/api/health`
- API direct: `http://localhost:8000/health`
- Vite direct: `http://localhost:5173`

To test the Mini App inside Telegram without configuring a custom domain, follow [the Cloudflare Quick Tunnel runbook](docs/quick-tunnel-testing.md).

## Environment

Create `.env` from the example:

```bash
cp .env.example .env
```

Set at least:

```env
APP_URL=https://training.example.com
API_URL=https://training.example.com/api
MINI_APP_URL=https://training.example.com

POSTGRES_PASSWORD=change_me
DATABASE_URL=postgresql+psycopg://training:change_me@postgres:5432/training

TELEGRAM_BOT_TOKEN=123456:telegram_bot_token
TELEGRAM_ALLOWED_USER_IDS=123456789

JWT_SECRET=replace_me_with_long_random_secret
ADMIN_SECRET=replace_me
ALLOW_ADMIN_ENDPOINTS=false
```

With `TELEGRAM_BOT_TOKEN=replace_me`, the bot container starts in idle mode and does not poll Telegram.

## Dataset Import

The raw dataset comes from:

```text
https://github.com/olegbal/exercises-dataset
```

Clone it into the expected local path:

```bash
git clone https://github.com/olegbal/exercises-dataset data/exercises-dataset
```

The API container mounts `./data` as read-only at `/data`, so the dataset JSON is expected at:

```text
/data/exercises-dataset/data/exercises.json
```

Start the stack and initialize the database:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

Import exercises:

```bash
docker compose exec api python -m app.scripts.import_exercises \
  --input /data/exercises-dataset/data/exercises.json
```

Apply curated metadata:

```bash
docker compose exec api python -m app.scripts.seed_curated_exercises \
  --input /data/curated_exercises.seed.json
```

Seed workout templates:

```bash
docker compose exec api python -m app.scripts.seed_workout_templates
```

The import is idempotent. Media URLs are derived from dataset `image` and `gif_url` fields using:

```env
RAW_MEDIA_BASE=https://raw.githubusercontent.com/olegbal/exercises-dataset/main/
```

Do not manually invent exercise media URLs.

## OpenClaw VM Deployment

Yes, this app can run on an existing OpenClaw VM.

For the current MVP, OpenClaw is not required as an active AI engine. The VM can simply host the Docker Compose stack:

```bash
git clone <this-repo-url>
cd Training-program-app
cp .env.example .env
```

Fill `.env`, clone the dataset, then run:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.import_exercises \
  --input /data/exercises-dataset/data/exercises.json
docker compose exec api python -m app.scripts.seed_curated_exercises \
  --input /data/curated_exercises.seed.json
docker compose exec api python -m app.scripts.seed_workout_templates
```

The current compose file exposes Caddy on local port `8080`. For a real Telegram Mini App URL, put your existing OpenClaw VM reverse proxy in front of `http://127.0.0.1:8080`, or adjust Compose/Caddy to expose HTTPS on ports `80` and `443`.

Telegram Mini Apps require HTTPS in production.

## Where OpenClaw Fits

OpenClaw will sit behind the backend, not inside the Mini App.

Prepared routes:

```http
POST /ai/generate-workout
POST /ai/replace-exercise
POST /ai/explain-technique
POST /ai/analyze-progress
POST /ai/validate-workout
```

Current behavior:

- `/ai/validate-workout` runs deterministic `WorkoutValidator` checks.
- Other `/ai/*` routes return structured placeholders.

Future behavior:

1. Mini App asks backend for an AI action.
2. Backend gathers workout, history, curated exercises, and user rules.
3. Backend calls OpenClaw.
4. OpenClaw returns structured JSON.
5. Backend validates the result with `WorkoutValidator`.
6. Backend returns the result to Mini App.

OpenClaw should prefer curated exercises, include dataset media URLs, and must not choose hip thrust or glute bridge as a main exercise.

See also: `docs/openclaw.md`.

## Telegram Flow

1. User opens the Telegram bot.
2. Bot checks `TELEGRAM_ALLOWED_USER_IDS`.
3. Bot sends a button that opens the Mini App.
4. Mini App sends Telegram `initData` to `POST /auth/telegram`.
5. Backend validates the Telegram HMAC with `TELEGRAM_BOT_TOKEN`.
6. Backend checks the Telegram ID allowlist.
7. Backend returns a JWT.
8. Mini App uses `Authorization: Bearer <jwt>` for workout API calls.

Never trust `initDataUnsafe` from the frontend.

## MVP Smoke Test

After database setup and seeds:

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/exercises/search?q=leg%20press"
curl "http://localhost:8000/workouts/today"
```

Expected:

- `/health` returns `{"status":"ok"}`.
- exercise search returns imported exercises with `image_url` and `gif_url` when dataset media exists.
- `/workouts/today` returns the correct template for the current weekday.

Full authenticated workout smoke requires signed Telegram Mini App `initData`. In production, the Mini App receives it from Telegram automatically.

## Development Checks

API:

```bash
cd apps/api
.venv/bin/python -m ruff check app tests
.venv/bin/python -m pytest tests -q
```

Bot:

```bash
cd apps/bot
.venv/bin/python -m ruff check app tests
.venv/bin/python -m pytest tests -q
```

Mini App:

```bash
cd apps/mini-app
npm test -- --run
npm run build
```

Docker:

```bash
docker compose config
docker compose build api bot mini-app
```

## Useful Commands

Start:

```bash
docker compose up -d --build
```

Logs:

```bash
docker compose logs -f api
docker compose logs -f bot
```

Stop:

```bash
docker compose down
```

Reset local database:

```bash
docker compose down -v
```

This deletes the PostgreSQL volume.
