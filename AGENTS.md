# AGENTS.md — Training Agent / Telegram Fitness Tracker

## Purpose

Build a self-hosted personal training system for one user.

The product must let the user:

1. Open a Telegram bot.
2. Launch a Telegram Mini App.
3. See today's workout.
4. See exercises with images/GIFs from `olegbal/exercises-dataset`.
5. Record sets: weight, reps, RPE, notes.
6. Mark exercises as completed / skipped / replaced.
7. Complete a workout session.
8. View workout history.
9. Later: use AI/OpenClaw to generate workouts, replace exercises, explain technique, and analyze progress.

The system is personal-first, not a public SaaS product.

---

## Current training context

The user trains on this weekly structure:

| Day | Type | Focus |
|---|---|---|
| Monday | Legs A | Quads + glutes + calves |
| Tuesday | Upper A | Back + biceps + rear delts |
| Wednesday | Rest | Recovery / walking / mobility |
| Thursday | Legs B | Hamstrings + glutes + calves |
| Friday | Boxing | Technique / conditioning |
| Saturday | Upper B | Chest + shoulders + triceps |
| Sunday | Rest | Recovery |

Important user preferences:

- Legs must be trained 2x/week.
- Upper body must not be ignored.
- The user is adapted to training load; do not over-soften the program.
- Workouts should be hard but controlled.
- Do not use hip thrust / glute bridge as a main exercise. Mark as `avoid`.
- Base lifts usually use RPE 7.5–9.
- Isolation exercises may use RPE 8–9.5.
- Do not program failure in every exercise.
- Track stress on lower back, shoulders, knees.
- Provide GIF/image links whenever an exercise comes from the dataset.

---

## Preferred stack

Use this stack unless the repository already uses something else.

### Backend

- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- pytest
- ruff
- mypy where practical

### Bot

- Python
- aiogram v3
- Telegram Bot API

### Mini App frontend

- React
- TypeScript
- Vite
- Telegram WebApp SDK
- Plain CSS or CSS modules. Avoid heavy UI frameworks for MVP.

### Deployment

- Docker Compose
- Caddy for HTTPS reverse proxy
- `.env` for secrets

---

## Repository structure to create

```text
training-agent/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── db/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── routes/
│   │   │   ├── services/
│   │   │   └── ai/
│   │   ├── tests/
│   │   ├── alembic/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── bot/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   └── handlers.py
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   └── mini-app/
│       ├── src/
│       │   ├── api/
│       │   ├── components/
│       │   ├── screens/
│       │   ├── types/
│       │   ├── App.tsx
│       │   └── main.tsx
│       ├── package.json
│       ├── vite.config.ts
│       └── Dockerfile
│
├── data/
│   ├── exercises-dataset/
│   └── curated_exercises.seed.json
│
├── docs/
│   ├── api.md
│   ├── data-model.md
│   └── deployment.md
│
├── docker-compose.yml
├── Caddyfile
├── .env.example
├── README.md
└── AGENTS.md
```

---

## Dataset handling

The raw exercise dataset is expected at:

```text
data/exercises-dataset/data/exercises.json
```

The source repository is:

```text
https://github.com/olegbal/exercises-dataset
```

Each imported exercise may contain fields like:

```text
id
name
category
body_part
equipment
instructions
instruction_steps
muscle_group
secondary_muscles
target
image
gif_url
```

Construct public media URLs like this:

```text
RAW_BASE=https://raw.githubusercontent.com/olegbal/exercises-dataset/main/
image_url = RAW_BASE + image
gif_url   = RAW_BASE + gif_url
```

Never invent dataset media URLs manually. Always derive them from `image` and `gif_url`.

Create an import command:

```bash
python -m app.scripts.import_exercises \
  --input /data/exercises-dataset/data/exercises.json
```

The import must be idempotent.

---

## Exercise curation rules

Do not expose all 1324 dataset exercises directly as primary choices.

Add these curation states:

```text
preferred
acceptable
backup
avoid
unreviewed
```

For MVP, seed a small curated library for the four strength templates.

### Required movement pattern fields

Add a `movement_pattern` field with values such as:

```text
squat
lunge
hinge
leg_press
leg_extension
leg_curl
calf_raise
vertical_pull
horizontal_pull
bench_press
incline_press
overhead_press
lateral_raise
rear_delt
biceps_curl
triceps_extension
anti_extension
anti_rotation
core_stability
conditioning
mobility
```

### Required difficulty field

```text
beginner
intermediate
advanced
```

### Avoid by default

```text
hip thrust
glute bridge
```

These can exist in the database, but should not be selected as primary exercises for this user.

---

## Initial workout templates

Create these templates and seed them into the database.

### Legs A — Monday

Focus: quads + glutes + calves.

| Exercise slot | Sets | Reps | RPE | Rest |
|---|---:|---|---|---|
| Leg press / hack squat / squat | 4 | 6–10 | 7.5–9 | 2–3 min |
| Bulgarian split squat | 3 | 8–12 each leg | 8 | 90–120 sec |
| Leg extension | 3 | 12–15 | 8–9 | 60–90 sec |
| Leg curl | 2 | 10–15 | 8 | 60–90 sec |
| Calf raise | 4 | 10–20 | 8–9 | 60 sec |
| Plank / dead bug | 2–3 | time or 8–12 | control | 45–60 sec |

Preferred dataset search terms:

```text
sled 45 degrees leg press
lever leg press
dumbbell bulgarian split squat
lever leg extension
lever lying leg curl
lever seated leg curl
lever standing calf raise
front plank
dead bug
```

### Upper A — Tuesday

Focus: back + biceps + rear delts.

| Exercise slot | Sets | Reps | RPE | Rest |
|---|---:|---|---|---|
| Lat pulldown / pull-up | 4 | 6–12 | 8 | 2 min |
| Seated row | 4 | 8–12 | 8 | 90–120 sec |
| One-arm dumbbell row / chest-supported row | 3 | 10–12 | 8 | 90 sec |
| Face pull / reverse fly | 3 | 12–20 | 8 | 60 sec |
| Biceps curl | 3 | 8–12 | 8 | 60–90 sec |
| Hammer curl | 2–3 | 10–15 | 8 | 60 sec |

Preferred dataset search terms:

```text
cable pulldown
cable wide grip lat pulldown
cable seated row
lever seated row
dumbbell one arm row
cable face pull
lever reverse fly
dumbbell biceps curl
ez barbell curl
dumbbell hammer curl
```

### Legs B — Thursday

Focus: hamstrings + glutes + calves. No hip thrust / glute bridge.

| Exercise slot | Sets | Reps | RPE | Rest |
|---|---:|---|---|---|
| Romanian deadlift | 4 | 6–10 | 7.5–8.5 | 2–3 min |
| High-foot leg press | 4 | 8–12 | 8 | 90–120 sec |
| Leg curl | 3 | 10–15 | 8–9 | 60–90 sec |
| Reverse lunge | 3 | 8–12 each leg | 8 | 90 sec |
| 45° hyperextension | 3 | 10–15 | 8 | 60–90 sec |
| Calf raise | 4 | 12–20 | 8–9 | 60 sec |
| Side plank / Pallof press | 2–3 | time or 10–12 | control | 45–60 sec |

Preferred dataset search terms:

```text
barbell romanian deadlift
dumbbell romanian deadlift
barbell stiff leg deadlift
dumbbell stiff leg deadlift
sled 45 degrees leg press
lever leg press
lever lying leg curl
lever seated leg curl
dumbbell reverse lunge
dumbbell rear lunge
hyperextension
weighted hyperextension
lever standing calf raise
side plank
cable pallof press
```

### Upper B — Saturday

Focus: chest + shoulders + triceps.

| Exercise slot | Sets | Reps | RPE | Rest |
|---|---:|---|---|---|
| Bench press / chest press | 4 | 6–10 | 8 | 2 min |
| Incline dumbbell press | 3 | 8–12 | 8 | 90–120 sec |
| Face pull / light row | 2–3 | 12–15 | 7 | 60–90 sec |
| Seated dumbbell shoulder press | 2–3 | 6–10 | 7.5–8 | 90–120 sec |
| Lateral raise | 3 | 12–20 | 8–9 | 60 sec |
| Cable triceps pushdown | 3 | 10–15 | 8 | 60 sec |
| Overhead triceps extension | 2 | 10–15 | 8 | 60 sec |

Preferred dataset search terms:

```text
dumbbell bench press
barbell bench press
lever chest press
dumbbell incline bench press
barbell incline bench press
cable face pull
dumbbell seated shoulder press
lever shoulder press
dumbbell lateral raise
cable lateral raise
cable triceps pushdown
cable overhead triceps extension
dumbbell overhead triceps extension
```

---

## Database schema

Implement migrations for these tables.

### users

```text
id UUID PK
telegram_id BIGINT UNIQUE NOT NULL
username TEXT NULL
first_name TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

### exercises

```text
id UUID PK
source_id TEXT UNIQUE NOT NULL
name TEXT NOT NULL
ru_name TEXT NULL
body_part TEXT NULL
target TEXT NULL
secondary_muscles JSONB NOT NULL DEFAULT []
equipment TEXT NULL
movement_pattern TEXT NULL
difficulty TEXT NULL
image_path TEXT NULL
gif_path TEXT NULL
image_url TEXT NULL
gif_url TEXT NULL
instructions JSONB NULL
instruction_steps JSONB NULL
curation_status TEXT NOT NULL DEFAULT 'unreviewed'
avoid_reason TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

### workout_templates

```text
id UUID PK
code TEXT UNIQUE NOT NULL
title TEXT NOT NULL
weekday INT NOT NULL
focus TEXT NOT NULL
description TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Weekday convention:

```text
0 = Sunday
1 = Monday
2 = Tuesday
3 = Wednesday
4 = Thursday
5 = Friday
6 = Saturday
```

### template_exercises

```text
id UUID PK
template_id UUID FK workout_templates.id
exercise_id UUID FK exercises.id NULL
slot_name TEXT NOT NULL
order_index INT NOT NULL
planned_sets_min INT NOT NULL
planned_sets_max INT NOT NULL
reps_min INT NULL
reps_max INT NULL
reps_text TEXT NULL
rpe_min NUMERIC(3,1) NULL
rpe_max NUMERIC(3,1) NULL
rest_seconds_min INT NULL
rest_seconds_max INT NULL
notes TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

### workout_sessions

```text
id UUID PK
user_id UUID FK users.id
template_id UUID FK workout_templates.id NULL
date DATE NOT NULL
title TEXT NOT NULL
day_type TEXT NOT NULL
status TEXT NOT NULL DEFAULT 'planned'
energy TEXT NULL
sleep TEXT NULL
notes TEXT NULL
started_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Allowed session status:

```text
planned
started
completed
skipped
```

### workout_exercises

```text
id UUID PK
session_id UUID FK workout_sessions.id
exercise_id UUID FK exercises.id NULL
replaced_from_exercise_id UUID FK exercises.id NULL
slot_name TEXT NOT NULL
order_index INT NOT NULL
planned_sets_min INT NOT NULL
planned_sets_max INT NOT NULL
reps_text TEXT NULL
rpe_text TEXT NULL
rest_text TEXT NULL
status TEXT NOT NULL DEFAULT 'planned'
notes TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Allowed exercise status:

```text
planned
in_progress
completed
skipped
replaced
```

### sets

```text
id UUID PK
workout_exercise_id UUID FK workout_exercises.id
set_index INT NOT NULL
weight NUMERIC(7,2) NULL
reps INT NULL
rpe NUMERIC(3,1) NULL
is_warmup BOOLEAN NOT NULL DEFAULT false
notes TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

---

## Telegram authentication

The Mini App must authenticate by sending Telegram `initData` to the backend.

Rules:

- Never trust `initDataUnsafe` from the frontend.
- Backend must validate `initData` HMAC using the bot token.
- For MVP, additionally restrict access to `TELEGRAM_ALLOWED_USER_IDS`.
- Do not log bot tokens, API keys, or raw initData.

Implement:

```http
POST /auth/telegram
```

Request:

```json
{
  "init_data": "query-string-from-Telegram-WebApp"
}
```

Response:

```json
{
  "access_token": "jwt",
  "user": {
    "id": "uuid",
    "telegram_id": 123456789,
    "username": "..."
  }
}
```

Use JWT for API calls from the Mini App.

---

## API endpoints for MVP

### Health

```http
GET /health
```

### Exercises

```http
GET /exercises
GET /exercises/{id}
GET /exercises/search?q=romanian&equipment=barbell
POST /admin/exercises/import
POST /admin/exercises/seed-curated
```

Admin endpoints must require an admin secret or be disabled unless `ALLOW_ADMIN_ENDPOINTS=true`.

### Workouts

```http
GET /workouts/today
POST /workouts/today/start
GET /workouts/{session_id}
POST /workouts/{session_id}/complete
POST /workouts/{session_id}/skip
GET /workouts/history
```

### Workout exercises

```http
POST /workout-exercises/{id}/complete
POST /workout-exercises/{id}/skip
POST /workout-exercises/{id}/replace
```

### Sets

```http
POST /workout-exercises/{id}/sets
PUT /sets/{set_id}
DELETE /sets/{set_id}
```

---

## API response shape

For `GET /workouts/today`, return:

```json
{
  "session": {
    "id": "uuid",
    "date": "2026-07-03",
    "title": "Ноги B",
    "day_type": "legs_b",
    "focus": "задняя поверхность бедра + ягодицы + икры",
    "status": "planned"
  },
  "exercises": [
    {
      "id": "uuid",
      "slot_name": "Румынская тяга",
      "status": "planned",
      "planned_sets": "4",
      "planned_reps": "6–10",
      "planned_rpe": "7.5–8.5",
      "rest": "2–3 мин",
      "exercise": {
        "id": "uuid",
        "name": "barbell romanian deadlift",
        "ru_name": "Румынская тяга со штангой",
        "equipment": "barbell",
        "target": "hamstrings",
        "image_url": "...",
        "gif_url": "..."
      },
      "sets": []
    }
  ]
}
```

---

## Mini App requirements

Create these screens:

### 1. Today screen

Must show:

- today's day label;
- workout title;
- focus;
- progress: completed exercises / total exercises;
- button: `Начать тренировку` or `Продолжить`;
- button: `Журнал`.

### 2. Workout screen

Must show exercise cards.

Each card must include:

- exercise title;
- planned sets/reps/RPE/rest;
- image preview;
- button to open GIF modal;
- technique/instructions collapsed section if available;
- set input rows: weight, reps, RPE, warmup toggle, notes;
- button to add set;
- button to mark completed;
- button to skip;
- button to replace.

### 3. Exercise modal

Must show:

- GIF;
- image;
- dataset name;
- equipment;
- target;
- instruction steps;
- raw media links.

### 4. History screen

Must show:

- previous sessions;
- exercises and sets inside session;
- completed/skipped status.

### 5. Exercise library screen

Must show:

- search;
- filters: equipment, body_part, movement_pattern, curation_status;
- image/GIF links.

---

## Bot requirements

Create Telegram bot commands:

```text
/start
/today
/history
/help
```

`/start` must send:

- short explanation;
- button to open Mini App.

`/today` must send:

- today's workout title;
- short list of exercises;
- button to open Mini App.

The bot must use the same backend API as the Mini App.

---

## AI / OpenClaw phase

Do not implement full AI generation in MVP unless explicitly requested.

Prepare interfaces:

```http
POST /ai/generate-workout
POST /ai/replace-exercise
POST /ai/explain-technique
POST /ai/analyze-progress
POST /ai/validate-workout
```

For now, these may return deterministic placeholders or rule-based output.

Future AI rules:

- Build workouts only from curated exercises when possible.
- Always run validator before returning generated workout.
- Do not select hip thrust / glute bridge as a main exercise.
- Include GIF/image URLs.
- Include simplified version when requested.
- Keep response JSON structured.

---

## Workout validator rules

Create a service `WorkoutValidator`.

Minimum checks:

1. No hip thrust / glute bridge as a primary exercise.
2. Legs are trained twice per week in the default template.
3. Upper body has both pulling and pushing coverage.
4. No all-failure programming.
5. RPE for compound lifts usually stays 7.5–9.
6. Isolation may go 8–9.5.
7. Legs B must not overload lower back excessively.
8. A workout should include at most one heavy hip hinge.
9. Core appears at least 2x/week.
10. Calves appear in both leg days.

Return warnings, not only pass/fail.

Example:

```json
{
  "valid": true,
  "warnings": [
    "Legs B includes Romanian deadlift and hyperextension; keep hyperextension at RPE 7–8 if lower back is fatigued."
  ]
}
```

---

## Security requirements

Do not compromise on these:

- Do not commit `.env`.
- Do not log secrets.
- Use `.env.example` with placeholder values.
- Validate Telegram initData server-side.
- Restrict MVP access to allowed Telegram IDs.
- Admin/import endpoints must be disabled or protected.
- Dataset directory should be read-only in production.
- Run containers as non-root where practical.
- Do not mount Docker socket into app containers.
- CORS must allow only the Mini App domain in production.
- Use HTTPS in production.

---

## Environment variables

Create `.env.example`:

```env
APP_ENV=development
APP_URL=https://training.example.com
API_URL=https://training.example.com/api
MINI_APP_URL=https://training.example.com

DATABASE_URL=postgresql+psycopg://training:training@postgres:5432/training
POSTGRES_DB=training
POSTGRES_USER=training
POSTGRES_PASSWORD=change_me

TELEGRAM_BOT_TOKEN=replace_me
TELEGRAM_ALLOWED_USER_IDS=123456789

JWT_SECRET=replace_me_with_long_random_secret
ADMIN_SECRET=replace_me

EXERCISES_DATASET_PATH=/data/exercises-dataset/data/exercises.json
RAW_MEDIA_BASE=https://raw.githubusercontent.com/olegbal/exercises-dataset/main/

ALLOW_ADMIN_ENDPOINTS=false

OPENAI_API_KEY=
OPENCLAW_ENABLED=false
```

---

## Docker Compose requirements

Create services:

```text
postgres
api
bot
mini-app
caddy
```

Development can expose ports:

```text
api: 8000
mini-app: 5173 or built static via Caddy
postgres: 5432
```

Production should expose only Caddy ports 80/443.

---

## Testing requirements

Backend tests:

- Telegram initData validation with known test vectors or mocked signature.
- Exercise import is idempotent.
- Media URLs are derived correctly.
- `/workouts/today` returns correct template by weekday.
- Creating sets works.
- Completing an exercise works.
- Completing a session works.
- Access is denied for non-allowed Telegram IDs.

Frontend tests, if feasible:

- Today screen renders workout.
- Exercise card opens GIF modal.
- Set input submits correct payload.
- Mark completed updates UI.

Always add tests for non-trivial service logic.

---

## Codex working rules

When modifying this repo:

1. Start by inspecting the current tree.
2. Read this file before coding.
3. Do not introduce new major frameworks without explaining why.
4. Prefer small, reviewable commits/tasks.
5. Keep MVP scope tight.
6. Do not implement AI generation before core tracker works.
7. Do not hardcode secrets.
8. Do not invent dataset media filenames.
9. Run tests before final answer.
10. If tests cannot run, clearly state why and what was checked instead.

---

## Implementation phases

### Phase 1 — Project skeleton

Deliver:

- repo structure;
- Docker Compose;
- backend FastAPI skeleton;
- bot skeleton;
- mini-app skeleton;
- `.env.example`;
- README.

Acceptance:

```bash
docker compose up --build
```

starts all services without crashing.

### Phase 2 — Database and import

Deliver:

- SQLAlchemy models;
- Alembic migrations;
- import script for exercises;
- seed curated exercises;
- exercise search endpoints.

Acceptance:

```bash
GET /exercises/search?q=leg%20press
```

returns exercises with `image_url` and `gif_url`.

### Phase 3 — Workout templates

Deliver:

- seed templates for Legs A, Upper A, Legs B, Upper B, rest, boxing;
- `/workouts/today`;
- session start/complete.

Acceptance:

```bash
GET /workouts/today
```

returns the correct day template and exercises.

### Phase 4 — Mini App tracker

Deliver:

- Today screen;
- Workout screen;
- GIF modal;
- set logging;
- complete/skip exercise;
- complete session;
- history screen.

Acceptance:

The user can complete a workout from the Mini App and view it in history.

### Phase 5 — Telegram bot

Deliver:

- `/start`;
- `/today`;
- Mini App button;
- access restricted to allowed Telegram IDs.

Acceptance:

The bot sends a button that opens the Mini App.

### Phase 6 — AI/OpenClaw interfaces

Deliver:

- placeholder AI routes;
- validation service;
- documented OpenClaw skill interface.

Acceptance:

`POST /ai/validate-workout` returns validation warnings for a workout.

---

## Non-goals for MVP

Do not build these yet:

- payments;
- multi-user SaaS admin panel;
- social sharing;
- complex charts;
- nutrition tracking;
- wearable integration;
- automatic deload planning;
- full autonomous OpenClaw deployment;
- commercial license workflow for dataset media.

---

## Definition of done for MVP v1

The MVP is done when:

1. Telegram bot launches the Mini App.
2. Mini App authenticates the user.
3. Today's workout appears.
4. Every exercise has image/GIF when dataset match exists.
5. User can add sets with weight/reps/RPE.
6. User can mark exercises completed/skipped.
7. User can complete the workout.
8. Workout history shows saved sessions and sets.
9. Access is restricted to the allowed Telegram user.
10. The app runs on a VM via Docker Compose behind HTTPS.

