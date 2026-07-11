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
