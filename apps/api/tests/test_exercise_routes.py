import uuid
from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import create_app
from app.models.exercise import Exercise


class FakeScalarResult:
    def __init__(self, values: list[Exercise]) -> None:
        self.values = values

    def all(self) -> list[Exercise]:
        return self.values

    def one_or_none(self) -> Exercise | None:
        return self.values[0] if self.values else None


class FakeSession:
    def __init__(self, values: list[Exercise]) -> None:
        self.values = values

    def scalars(self, statement: object) -> FakeScalarResult:
        return FakeScalarResult(self.values)


def test_exercises_search_returns_exercise_media_urls() -> None:
    exercise = Exercise(
        id=uuid.uuid4(),
        source_id="ex-1",
        name="Dumbbell Romanian Deadlift",
        body_part="upper legs",
        target="hamstrings",
        secondary_muscles=["glutes"],
        equipment="dumbbell",
        image_path="exercises/dumbbell-romanian-deadlift/0.jpg",
        gif_path="exercises/dumbbell-romanian-deadlift/1.gif",
        image_url="https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/dumbbell-romanian-deadlift/0.jpg",
        gif_url="https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/dumbbell-romanian-deadlift/1.gif",
        curation_status="unreviewed",
    )
    app = create_app()

    def override_db() -> Iterator[FakeSession]:
        yield FakeSession([exercise])

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    response = client.get("/exercises/search?q=romanian&equipment=dumbbell")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Dumbbell Romanian Deadlift"
    assert response.json()[0]["image_url"].endswith("/exercises/dumbbell-romanian-deadlift/0.jpg")
    assert response.json()[0]["gif_url"].endswith("/exercises/dumbbell-romanian-deadlift/1.gif")


def test_admin_import_is_disabled_by_default() -> None:
    client = TestClient(create_app())

    response = client.post("/admin/exercises/import")

    assert response.status_code == 404
