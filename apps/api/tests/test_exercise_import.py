import json
from pathlib import Path

from app.services.exercise_import import (
    ImportStats,
    SeedStats,
    apply_curated_seed_file,
    build_media_url,
    import_exercise_file,
    map_dataset_exercise,
)


class FakeScalarResult:
    def __init__(self, value: object | None) -> None:
        self.value = value

    def one_or_none(self) -> object | None:
        return self.value


class FakeSession:
    def __init__(self) -> None:
        self.by_source_id: dict[str, object] = {}
        self.by_name: dict[str, object] = {}
        self.added: list[object] = []
        self.commits = 0

    def scalars(self, statement: object) -> FakeScalarResult:
        params = statement.compile().params
        if "source_id_1" in params:
            return FakeScalarResult(self.by_source_id.get(params["source_id_1"]))
        return FakeScalarResult(self.by_name.get(params["name_1"]))

    def add(self, exercise: object) -> None:
        self.added.append(exercise)
        self.by_source_id[exercise.source_id] = exercise
        self.by_name[exercise.name] = exercise

    def commit(self) -> None:
        self.commits += 1


def test_build_media_url_derives_from_dataset_path() -> None:
    assert (
        build_media_url("exercises/barbell-romanian-deadlift/0.jpg")
        == "https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/barbell-romanian-deadlift/0.jpg"
    )


def test_build_media_url_returns_none_when_path_missing() -> None:
    assert build_media_url(None) is None
    assert build_media_url("") is None


def test_map_dataset_exercise_preserves_media_paths_and_marks_hip_thrust_avoid() -> None:
    mapped = map_dataset_exercise(
        {
            "id": "123",
            "name": "Barbell Hip Thrust",
            "body_part": "upper legs",
            "target": "glutes",
            "secondary_muscles": ["hamstrings"],
            "equipment": "barbell",
            "image": "exercises/barbell-hip-thrust/0.jpg",
            "gif_url": "exercises/barbell-hip-thrust/1.gif",
            "instructions": {"setup": "Bench behind shoulders"},
            "instruction_steps": ["Sit on the floor", "Drive hips up"],
        }
    )

    assert mapped["source_id"] == "123"
    assert mapped["name"] == "Barbell Hip Thrust"
    assert mapped["image_path"] == "exercises/barbell-hip-thrust/0.jpg"
    assert mapped["gif_path"] == "exercises/barbell-hip-thrust/1.gif"
    assert mapped["image_url"].endswith("/exercises/barbell-hip-thrust/0.jpg")
    assert mapped["gif_url"].endswith("/exercises/barbell-hip-thrust/1.gif")
    assert mapped["curation_status"] == "avoid"
    assert mapped["avoid_reason"] == "Avoid as a main exercise for this user."


def test_import_exercise_file_is_idempotent(tmp_path: Path) -> None:
    input_path = tmp_path / "exercises.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "id": "ex-1",
                    "name": "Dumbbell Romanian Deadlift",
                    "body_part": "upper legs",
                    "target": "hamstrings",
                    "equipment": "dumbbell",
                    "image": "exercises/dumbbell-romanian-deadlift/0.jpg",
                }
            ]
        ),
        encoding="utf-8",
    )
    session = FakeSession()

    first_stats = import_exercise_file(session, input_path)
    second_stats = import_exercise_file(session, input_path)

    assert first_stats == ImportStats(created=1, updated=0)
    assert second_stats == ImportStats(created=0, updated=1)
    assert len(session.added) == 1
    assert session.commits == 2


def test_apply_curated_seed_updates_existing_exercise_by_name(tmp_path: Path) -> None:
    seed_path = tmp_path / "curated.json"
    seed_path.write_text(
        json.dumps(
            [
                {
                    "name": "Dumbbell Romanian Deadlift",
                    "ru_name": "Румынская тяга с гантелями",
                    "movement_pattern": "hinge",
                    "difficulty": "intermediate",
                    "curation_status": "preferred",
                }
            ]
        ),
        encoding="utf-8",
    )
    session = FakeSession()
    session.add(
        type(
            "ExerciseLike",
            (),
            {
                "source_id": "ex-1",
                "name": "Dumbbell Romanian Deadlift",
                "ru_name": None,
                "movement_pattern": None,
                "difficulty": None,
                "curation_status": "unreviewed",
                "avoid_reason": None,
            },
        )()
    )

    stats = apply_curated_seed_file(session, seed_path)
    exercise = session.by_source_id["ex-1"]

    assert stats == SeedStats(seeded=1, missing=0)
    assert exercise.ru_name == "Румынская тяга с гантелями"
    assert exercise.movement_pattern == "hinge"
    assert exercise.difficulty == "intermediate"
    assert exercise.curation_status == "preferred"
    assert session.commits == 1


def test_apply_curated_seed_reports_missing_exercise(tmp_path: Path) -> None:
    seed_path = tmp_path / "curated.json"
    seed_path.write_text(json.dumps([{"name": "Cable Face Pull", "curation_status": "preferred"}]), encoding="utf-8")
    session = FakeSession()

    stats = apply_curated_seed_file(session, seed_path)

    assert stats == SeedStats(seeded=0, missing=1)
    assert session.commits == 1
