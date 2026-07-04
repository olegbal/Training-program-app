# Deployment

The project is designed to run behind Caddy with Docker Compose.

Development compose exposes:

- API on port `8000`
- Mini App on port `5173`
- Caddy on port `8080`
- PostgreSQL on port `5432`

Production should expose only Caddy on ports `80` and `443`, use real secrets from `.env`, and mount the exercise dataset read-only.

Because the API container runs as a non-root user, mounted dataset files must be readable by that user. A safe host-side default is directories at `755` and JSON files at `644`, mounted read-only into the container.
