import argparse
from pathlib import Path

from app.db.session import SessionLocal
from app.services.exercise_import import import_exercise_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import exercises from olegbal/exercises-dataset JSON.")
    parser.add_argument("--input", required=True, type=Path, help="Path to data/exercises.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with SessionLocal() as session:
        stats = import_exercise_file(session, args.input)
    print(f"Imported exercises: created={stats.created} updated={stats.updated}")


if __name__ == "__main__":
    main()
