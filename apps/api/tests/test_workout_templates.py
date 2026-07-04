import uuid
from collections.abc import Iterator
from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import create_app
from app.models.exercise import Exercise
from app.models.template import TemplateExercise, WorkoutTemplate
from app.services.workout_templates import DEFAULT_TEMPLATE_SEEDS, get_template_seed_for_date


class FakeScalarResult:
    def __init__(self, value: object | None) -> None:
        self.value = value

    def one_or_none(self) -> object | None:
        return self.value


class FakeSession:
    def __init__(self, template: WorkoutTemplate | None) -> None:
        self.template = template

    def scalars(self, statement: object) -> FakeScalarResult:
        return FakeScalarResult(self.template)


def test_get_template_seed_for_date_uses_project_weekday_convention() -> None:
    assert get_template_seed_for_date(date(2026, 7, 5)).code == "rest_sunday"
    assert get_template_seed_for_date(date(2026, 7, 6)).code == "legs_a"
    assert get_template_seed_for_date(date(2026, 7, 7)).code == "upper_a"
    assert get_template_seed_for_date(date(2026, 7, 10)).code == "boxing"
    assert get_template_seed_for_date(date(2026, 7, 11)).code == "upper_b"


def test_legs_b_seed_does_not_program_hip_thrust_or_glute_bridge() -> None:
    legs_b = next(seed for seed in DEFAULT_TEMPLATE_SEEDS if seed.code == "legs_b")
    slot_text = " ".join(slot.slot_name.lower() for slot in legs_b.slots)
    search_text = " ".join(name.lower() for slot in legs_b.slots for name in slot.exercise_names)

    assert "hip thrust" not in slot_text
    assert "glute bridge" not in slot_text
    assert "hip thrust" not in search_text
    assert "glute bridge" not in search_text


def test_workouts_today_returns_template_exercises_with_media() -> None:
    exercise = Exercise(
        id=uuid.uuid4(),
        source_id="sample-leg-press",
        name="sled 45 degrees leg press",
        ru_name="Жим ногами в тренажере",
        body_part="upper legs",
        target="quadriceps",
        secondary_muscles=["glutes"],
        equipment="sled machine",
        image_url="https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/sled-45-degrees-leg-press/0.jpg",
        gif_url="https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/sled-45-degrees-leg-press/1.gif",
        curation_status="preferred",
    )
    template = WorkoutTemplate(
        id=uuid.uuid4(),
        code="legs_a",
        title="Ноги A",
        weekday=1,
        focus="квадрицепсы + ягодицы + икры",
        description="Hard but controlled lower-body session.",
    )
    template.template_exercises = [
        TemplateExercise(
            id=uuid.uuid4(),
            template_id=template.id,
            exercise_id=exercise.id,
            exercise=exercise,
            slot_name="Жим ногами / hack squat / squat",
            order_index=1,
            planned_sets_min=4,
            planned_sets_max=4,
            reps_min=6,
            reps_max=10,
            reps_text="6-10",
            rpe_min=Decimal("7.5"),
            rpe_max=Decimal("9.0"),
            rest_seconds_min=120,
            rest_seconds_max=180,
        )
    ]
    app = create_app()

    def override_db() -> Iterator[FakeSession]:
        yield FakeSession(template)

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    response = client.get("/workouts/today?date=2026-07-06")

    assert response.status_code == 200
    assert response.json()["session"]["date"] == "2026-07-06"
    assert response.json()["session"]["day_type"] == "legs_a"
    assert response.json()["exercises"][0]["planned_reps"] == "6-10"
    assert response.json()["exercises"][0]["planned_rpe"] == "7.5-9"
    assert response.json()["exercises"][0]["exercise"]["gif_url"].endswith("/exercises/sled-45-degrees-leg-press/1.gif")
