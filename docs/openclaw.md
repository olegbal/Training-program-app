# OpenClaw Integration Interface

The MVP does not generate workouts with AI. It exposes stable placeholder routes so the future OpenClaw layer can be added without changing Mini App or bot contracts.

## Routes

- `POST /ai/generate-workout`
- `POST /ai/replace-exercise`
- `POST /ai/explain-technique`
- `POST /ai/analyze-progress`
- `POST /ai/validate-workout`

The first four routes return deterministic placeholder JSON until `OPENCLAW_ENABLED=true` is implemented.

## Validator Contract

`POST /ai/validate-workout` accepts structured workout JSON:

```json
{
  "day_type": "legs_b",
  "exercises": [
    {
      "name": "barbell romanian deadlift",
      "movement_pattern": "hinge",
      "is_primary": true,
      "rpe": "8"
    }
  ]
}
```

It returns:

```json
{
  "valid": true,
  "warnings": []
}
```

Future OpenClaw generation must call the validator before returning a workout, prefer curated exercises, avoid hip thrust or glute bridge as main exercises, and include dataset media URLs when exercise matches exist.
