from app.db.session import SessionLocal
from app.services.workout_templates import seed_workout_templates


def main() -> None:
    with SessionLocal() as session:
        stats = seed_workout_templates(session)
    print(f"Seeded workout templates: templates={stats.templates_seeded} exercises={stats.exercises_seeded}")


if __name__ == "__main__":
    main()
