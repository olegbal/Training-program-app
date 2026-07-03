from app import models  # noqa: F401
from app.db.base import Base


def test_metadata_contains_mvp_tables() -> None:
    expected_tables = {
        "users",
        "exercises",
        "workout_templates",
        "template_exercises",
        "workout_sessions",
        "workout_exercises",
        "sets",
    }

    assert expected_tables.issubset(set(Base.metadata.tables))


def test_exercises_table_contains_dataset_media_and_curation_columns() -> None:
    exercises = Base.metadata.tables["exercises"]

    expected_columns = {
        "source_id",
        "name",
        "movement_pattern",
        "difficulty",
        "image_path",
        "gif_path",
        "image_url",
        "gif_url",
        "curation_status",
        "avoid_reason",
    }

    assert expected_columns.issubset(set(exercises.columns.keys()))
