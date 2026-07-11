import hashlib
import hmac
import json
import uuid
from collections.abc import Iterator
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.config import Settings, get_settings
from app.db.session import get_db
from app.main import create_app
from app.models.user import User
from app.services.telegram_auth import decode_access_token


class FakeScalarResult:
    def __init__(self, value: User | None) -> None:
        self.value = value

    def one_or_none(self) -> User | None:
        return self.value


class FakeSession:
    def __init__(self) -> None:
        self.user: User | None = None
        self.commits = 0

    def scalars(self, statement: object) -> FakeScalarResult:
        return FakeScalarResult(self.user)

    def add(self, user: User) -> None:
        self.user = user

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, user: User) -> None:
        if user.id is None:
            user.id = uuid.uuid4()
        return None


class RacingFakeSession:
    def __init__(self) -> None:
        self.existing_user = User(
            id=uuid.uuid4(),
            telegram_id=123456789,
            username="old-name",
            first_name="Old",
        )
        self.lookups = 0
        self.commits = 0
        self.rollbacks = 0

    def scalars(self, statement: object) -> FakeScalarResult:
        self.lookups += 1
        return FakeScalarResult(None if self.lookups == 1 else self.existing_user)

    def add(self, user: User) -> None:
        return None

    def commit(self) -> None:
        if self.rollbacks == 0:
            raise IntegrityError("INSERT INTO users", {}, Exception("duplicate telegram_id"))
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def refresh(self, user: User) -> None:
        return None


def signed_init_data(bot_token: str, user: dict[str, object]) -> str:
    params = {
        "auth_date": "1783179000",
        "query_id": "AAH-test-query",
        "user": json.dumps(user, separators=(",", ":")),
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    params["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(params)


def test_auth_telegram_creates_user_and_returns_jwt() -> None:
    session = FakeSession()
    app = create_app()
    settings = Settings(
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
        jwt_secret="jwt-secret",
    )

    def override_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post(
        "/auth/telegram",
        json={
            "init_data": signed_init_data(
                "123:bot-token",
                {"id": 123456789, "username": "coach", "first_name": "Alex"},
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["user"]["telegram_id"] == 123456789
    assert session.user is not None
    assert session.user.username == "coach"
    assert session.commits == 1
    payload = decode_access_token(response.json()["access_token"], secret="jwt-secret")
    assert payload["telegram_id"] == 123456789


def test_auth_telegram_recovers_when_concurrent_request_creates_user() -> None:
    session = RacingFakeSession()
    app = create_app()
    settings = Settings(
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
        jwt_secret="jwt-secret",
    )

    def override_db() -> Iterator[RacingFakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/auth/telegram",
        json={
            "init_data": signed_init_data(
                "123:bot-token",
                {"id": 123456789, "username": "coach", "first_name": "Alex"},
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["user"]["id"] == str(session.existing_user.id)
    assert session.existing_user.username == "coach"
    assert session.existing_user.first_name == "Alex"
    assert session.rollbacks == 1
    assert session.commits == 1


def test_auth_telegram_rejects_invalid_init_data() -> None:
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: Settings(
        telegram_bot_token="123:bot-token",
        telegram_allowed_user_ids=[123456789],
        jwt_secret="jwt-secret",
    )
    client = TestClient(app)

    response = client.post("/auth/telegram", json={"init_data": "user=%7B%22id%22%3A123456789%7D&hash=bad"})

    assert response.status_code == 401
