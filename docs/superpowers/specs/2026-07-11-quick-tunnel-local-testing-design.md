# Quick Tunnel Local Telegram Testing Design

## Goal

Let the owner manually test the Training Agent inside Telegram while the application runs in the current local workspace. The setup must not require a custom domain, router port forwarding, or committing secrets.

## Architecture

Docker Compose runs PostgreSQL, FastAPI, the Telegram bot, the Mini App, and Caddy. Caddy exposes the combined application locally on port `8080`. A temporary Cloudflare Quick Tunnel forwards a random HTTPS `trycloudflare.com` address to Caddy.

Telegram opens the temporary HTTPS address from the bot's Web App button. The Mini App sends Telegram `initData` to the FastAPI authentication endpoint through the same public origin. FastAPI validates the Telegram signature and restricts access to `TELEGRAM_ALLOWED_USER_IDS`.

## Local configuration

The local `.env` file is created from `.env.example` and remains ignored by Git. The owner supplies these values directly in that file:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_ALLOWED_USER_IDS`
- `JWT_SECRET`
- `ADMIN_SECRET`

After the Quick Tunnel starts, its temporary HTTPS URL is assigned to `APP_URL` and `MINI_APP_URL`. The Mini App continues using the same-origin `/api` route through Caddy. The bot may call FastAPI over the private Compose network while presenting the public tunnel URL in Telegram buttons.

## Startup flow

1. Create the local `.env` without real values being committed or printed.
2. Build and start the Docker Compose services.
3. Apply Alembic migrations.
4. Import the exercise dataset when present.
5. Apply curated exercise metadata and seed workout templates.
6. Start `cloudflared` as an ephemeral container that forwards to the Caddy service.
7. Capture the generated `trycloudflare.com` URL.
8. Put the URL in `.env` and recreate the bot service.
9. Open the bot in Telegram and launch the Mini App.

## Security

- No secrets are written to tracked files or terminal output.
- The bot token and raw Telegram `initData` are not logged.
- Telegram access remains restricted to the configured allowlist.
- PostgreSQL and direct API ports are not required for public access; the tunnel targets only Caddy.
- Quick Tunnel is used only for development and manual testing.

## Failure handling

- If the Quick Tunnel restarts, its hostname changes; update `MINI_APP_URL` and recreate the bot.
- If Telegram reports an invalid Web App URL, confirm the URL is HTTPS and the tunnel is still running.
- If authentication returns `401`, verify the configured bot token and allowed Telegram ID.
- If today's workout returns `404`, apply migrations and seed workout templates.
- If exercise media is missing, import the external dataset at the documented path; do not invent media URLs.

## Verification

Automated checks cover backend authentication, workout services, bot handlers, and frontend behavior. Manual acceptance is complete when the allowed Telegram user can:

1. Run `/start` and open the Mini App.
2. View today's workout.
3. Start a session and add a set.
4. Complete or skip an exercise.
5. Complete the workout.
6. See the saved session in history.

An unlisted Telegram user must receive no usable access.
