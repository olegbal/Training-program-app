# API

The current Phase 1 API exposes:

```http
GET /health
GET /exercises
GET /exercises/{id}
GET /exercises/search?q=romanian&equipment=dumbbell
POST /admin/exercises/import
POST /admin/exercises/seed-curated
```

Admin exercise endpoints are disabled unless `ALLOW_ADMIN_ENDPOINTS=true` and require `X-Admin-Secret`.

Workout, auth, set logging, and AI endpoints are defined in `AGENTS.md` and will be added in later phases.
