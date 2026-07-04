from fastapi.testclient import TestClient

from app.main import create_app
from app.services.workout_validator import WorkoutValidator


def test_workout_validator_flags_avoided_primary_exercises() -> None:
    result = WorkoutValidator().validate(
        {
            "exercises": [
                {
                    "name": "barbell hip thrust",
                    "slot_name": "Main glute lift",
                    "movement_pattern": "hinge",
                    "is_primary": True,
                    "rpe": "8",
                }
            ]
        }
    )

    assert result["valid"] is False
    assert any("hip thrust" in warning for warning in result["warnings"])


def test_workout_validator_warns_about_legs_b_lower_back_load() -> None:
    result = WorkoutValidator().validate(
        {
            "day_type": "legs_b",
            "exercises": [
                {"name": "barbell romanian deadlift", "movement_pattern": "hinge", "is_primary": True, "rpe": "8"},
                {"name": "weighted hyperextension", "movement_pattern": "hinge", "is_primary": False, "rpe": "8"},
            ],
        }
    )

    assert result["valid"] is True
    assert any("lower back" in warning for warning in result["warnings"])


def test_validate_workout_route_returns_warnings() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/ai/validate-workout",
        json={
            "day_type": "legs_b",
            "exercises": [
                {"name": "barbell romanian deadlift", "movement_pattern": "hinge", "is_primary": True, "rpe": "8"},
                {"name": "weighted hyperextension", "movement_pattern": "hinge", "is_primary": False, "rpe": "8"},
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["warnings"]


def test_ai_placeholder_routes_return_structured_placeholders() -> None:
    client = TestClient(create_app())

    response = client.post("/ai/generate-workout", json={"goal": "today"})

    assert response.status_code == 200
    assert response.json()["status"] == "placeholder"
