# Deployment

The project is designed to run behind Caddy with Docker Compose.

Development compose exposes:

- API on port `8000`
- Mini App on port `5173`
- Caddy on port `8080`
- PostgreSQL on port `5432`

Production should expose only Caddy on ports `80` and `443`, use real secrets from `.env`, and mount the exercise dataset read-only.
