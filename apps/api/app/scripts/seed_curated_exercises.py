import argparse
from pathlib import Path

from app.db.session import SessionLocal
from app.services.exercise_import import apply_curated_seed_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply curated exercise metadata seed.")
    parser.add_argument("--input", required=True, type=Path, help="Path to curated_exercises.seed.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with SessionLocal() as session:
        stats = apply_curated_seed_file(session, args.input)
    print(f"Seeded curated exercises: seeded={stats.seeded} missing={stats.missing}")


if __name__ == "__main__":
    main()
