import uuid
from collections.abc import Iterator
from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.db.session import get_db
from app.main import create_app
from app.models.exercise import Exercise
from app.models.set import WorkoutSet
from app.models.template import TemplateExercise, WorkoutTemplate
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutSession
from app.services.telegram_auth import create_access_token


class FakeScalarResult:
    def __init__(self, value: object | None) -> None:
        self.value = value

    def one_or_none(self) -> object | None:
        return self.value

    def all(self) -> list[object]:
        if isinstance(self.value, list):
            return self.value
        if self.value is None:
            return []
        return [self.value]


class FakeSession:
    def __init__(self, values: list[object | None]) -> None:
        self.values = values
        self.added: list[object] = []
        self.deleted: list[object] = []
        self.commits = 0

    def scalars(self, statement: object) -> FakeScalarResult:
        return FakeScalarResult(self.values.pop(0))

    def add(self, value: object) -> None:
        self.added.append(value)

    def delete(self, value: object) -> None:
        self.deleted.append(value)

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, value: object) -> None:
        if getattr(value, "id", None) is None:
            value.id = uuid.uuid4()
        for child in getattr(value, "workout_exercises", []):
            if child.id is None:
                child.id = uuid.uuid4()
            child.session_id = value.id


def make_user() -> User:
    return User(id=uuid.uuid4(), telegram_id=123456789, username="coach", first_name="Alex")


def make_template() -> WorkoutTemplate:
    exercise = Exercise(
        id=uuid.uuid4(),
        source_id="sample-leg-press",
        name="sled 45 degrees leg press",
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
        description=None,
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
            reps_text="6-10",
            rpe_min=Decimal("7.5"),
            rpe_max=Decimal("9.0"),
            rest_seconds_min=120,
            rest_seconds_max=180,
        )
    ]
    return template


def make_started_session(user: User) -> WorkoutSession:
    template = make_template()
    workout_session = WorkoutSession(
        id=uuid.uuid4(),
        user_id=user.id,
        template_id=template.id,
        template=template,
        date=date(2026, 7, 6),
        title=template.title,
        day_type=template.code,
        status="started",
    )
    template_exercise = template.template_exercises[0]
    workout_session.workout_exercises = [
        WorkoutExercise(
            id=uuid.uuid4(),
            session_id=workout_session.id,
            exercise_id=template_exercise.exercise_id,
            exercise=template_exercise.exercise,
            slot_name=template_exercise.slot_name,
            order_index=template_exercise.order_index,
            planned_sets_min=template_exercise.planned_sets_min,
            planned_sets_max=template_exercise.planned_sets_max,
            reps_text=template_exercise.reps_text,
            rpe_text="7.5-9",
            rest_text="2-3 min",
            status="planned",
        )
    ]
    return workout_session


def test_start_today_requires_bearer_token() -> None:
    client = TestClient(create_app())

    response = client.post("/workouts/today/start?date=2026-07-06")

    assert response.status_code == 401


def test_start_today_creates_session_from_template_for_current_user() -> None:
    user = make_user()
    template = make_template()
    session = FakeSession([user, None, template])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post(
        "/workouts/today/start?date=2026-07-06",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session"]["id"]
    assert body["session"]["day_type"] == "legs_a"
    assert body["session"]["status"] == "started"
    assert body["exercises"][0]["slot_name"] == "Жим ногами / hack squat / squat"
    assert body["exercises"][0]["exercise"]["name"] == "sled 45 degrees leg press"
    assert isinstance(session.added[0], WorkoutSession)
    assert isinstance(session.added[0].workout_exercises[0], WorkoutExercise)
    assert session.added[0].user_id == user.id
    assert session.added[0].date == date(2026, 7, 6)


def test_complete_workout_session_marks_owned_session_completed() -> None:
    user = make_user()
    workout_session = make_started_session(user)
    session = FakeSession([user, workout_session])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post(
        f"/workouts/{workout_session.id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session"]["id"] == str(workout_session.id)
    assert body["session"]["status"] == "completed"
    assert workout_session.status == "completed"
    assert workout_session.completed_at is not None
    assert session.commits == 1


def test_skip_workout_session_marks_owned_session_skipped() -> None:
    user = make_user()
    workout_session = make_started_session(user)
    session = FakeSession([user, workout_session])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post(
        f"/workouts/{workout_session.id}/skip",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session"]["id"] == str(workout_session.id)
    assert body["session"]["status"] == "skipped"
    assert workout_session.status == "skipped"
    assert session.commits == 1


def test_get_workout_session_returns_owned_session() -> None:
    user = make_user()
    workout_session = make_started_session(user)
    session = FakeSession([user, workout_session])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.get(
        f"/workouts/{workout_session.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session"]["id"] == str(workout_session.id)
    assert body["exercises"][0]["exercise"]["name"] == "sled 45 degrees leg press"


def test_add_set_creates_next_set_for_owned_workout_exercise() -> None:
    user = make_user()
    workout_session = make_started_session(user)
    workout_exercise = workout_session.workout_exercises[0]
    workout_exercise.sets = [
        WorkoutSet(
            id=uuid.uuid4(),
            workout_exercise_id=workout_exercise.id,
            set_index=1,
            weight=Decimal("80.00"),
            reps=10,
            rpe=Decimal("8.0"),
            is_warmup=False,
        )
    ]
    session = FakeSession([user, workout_exercise])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post(
        f"/workout-exercises/{workout_exercise.id}/sets",
        headers={"Authorization": f"Bearer {token}"},
        json={"weight": "82.50", "reps": 9, "rpe": "8.5", "is_warmup": False, "notes": "solid"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["set_index"] == 2
    assert body["reps"] == 9
    assert body["notes"] == "solid"
    assert workout_exercise.sets[-1].set_index == 2
    assert workout_exercise.sets[-1].workout_exercise_id == workout_exercise.id
    assert session.commits == 1


def test_complete_workout_exercise_marks_owned_exercise_completed() -> None:
    user = make_user()
    workout_session = make_started_session(user)
    workout_exercise = workout_session.workout_exercises[0]
    session = FakeSession([user, workout_exercise])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post(
        f"/workout-exercises/{workout_exercise.id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(workout_exercise.id)
    assert body["status"] == "completed"
    assert workout_exercise.status == "completed"
    assert session.commits == 1


def test_skip_workout_exercise_marks_owned_exercise_skipped() -> None:
    user = make_user()
    workout_session = make_started_session(user)
    workout_exercise = workout_session.workout_exercises[0]
    session = FakeSession([user, workout_exercise])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post(
        f"/workout-exercises/{workout_exercise.id}/skip",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(workout_exercise.id)
    assert body["status"] == "skipped"
    assert workout_exercise.status == "skipped"
    assert session.commits == 1


def test_replace_workout_exercise_sets_replacement_for_owned_exercise() -> None:
    user = make_user()
    workout_session = make_started_session(user)
    workout_exercise = workout_session.workout_exercises[0]
    replacement = Exercise(
        id=uuid.uuid4(),
        source_id="replacement-leg-press",
        name="lever leg press",
        target="quadriceps",
        secondary_muscles=["glutes"],
        equipment="leverage machine",
        image_url="https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/lever-leg-press/0.jpg",
        gif_url="https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/lever-leg-press/1.gif",
        curation_status="acceptable",
    )
    session = FakeSession([user, workout_exercise, replacement])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post(
        f"/workout-exercises/{workout_exercise.id}/replace",
        headers={"Authorization": f"Bearer {token}"},
        json={"exercise_id": str(replacement.id), "notes": "machine was free"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(workout_exercise.id)
    assert body["status"] == "replaced"
    assert body["exercise"]["name"] == "lever leg press"
    assert workout_exercise.replaced_from_exercise_id is not None
    assert workout_exercise.exercise_id == replacement.id
    assert workout_exercise.notes == "machine was free"
    assert session.commits == 1


def test_update_set_changes_owned_set_values() -> None:
    user = make_user()
    workout_set = WorkoutSet(
        id=uuid.uuid4(),
        workout_exercise_id=uuid.uuid4(),
        set_index=1,
        weight=Decimal("80.00"),
        reps=10,
        rpe=Decimal("8.0"),
        is_warmup=False,
        notes=None,
    )
    session = FakeSession([user, workout_set])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.put(
        f"/sets/{workout_set.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"weight": "82.50", "reps": 9, "rpe": "8.5", "is_warmup": True, "notes": "warmup-ish"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(workout_set.id)
    assert body["weight"] == "82.50"
    assert body["reps"] == 9
    assert body["rpe"] == "8.5"
    assert body["is_warmup"] is True
    assert body["notes"] == "warmup-ish"
    assert workout_set.weight == Decimal("82.50")
    assert workout_set.reps == 9
    assert session.commits == 1


def test_delete_set_removes_owned_set() -> None:
    user = make_user()
    workout_set = WorkoutSet(
        id=uuid.uuid4(),
        workout_exercise_id=uuid.uuid4(),
        set_index=1,
        weight=Decimal("80.00"),
        reps=10,
        rpe=Decimal("8.0"),
        is_warmup=False,
    )
    session = FakeSession([user, workout_set])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.delete(
        f"/sets/{workout_set.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert session.deleted == [workout_set]
    assert session.commits == 1


def test_history_returns_owned_sessions_with_exercises_and_sets() -> None:
    user = make_user()
    workout_session = make_started_session(user)
    workout_session.status = "completed"
    workout_exercise = workout_session.workout_exercises[0]
    workout_exercise.status = "completed"
    workout_exercise.sets = [
        WorkoutSet(
            id=uuid.uuid4(),
            workout_exercise_id=workout_exercise.id,
            set_index=1,
            weight=Decimal("80.00"),
            reps=10,
            rpe=Decimal("8.0"),
            is_warmup=False,
            notes="clean",
        )
    ]
    session = FakeSession([user, [workout_session]])
    app = create_app()
    settings = Settings(
        jwt_secret="jwt-secret",
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
    )
    token = create_access_token({"sub": str(user.id), "telegram_id": user.telegram_id}, secret="jwt-secret")

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.get("/workouts/history", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["sessions"][0]["session"]["id"] == str(workout_session.id)
    assert body["sessions"][0]["session"]["status"] == "completed"
    assert body["sessions"][0]["exercises"][0]["status"] == "completed"
    assert body["sessions"][0]["exercises"][0]["sets"][0]["reps"] == 10
