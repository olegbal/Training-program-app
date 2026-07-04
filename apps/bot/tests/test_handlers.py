import asyncio
from types import SimpleNamespace

from app.config import BotSettings
from app.handlers import start, today
from app.messages import format_today_message


class FakeMessage:
    def __init__(self, telegram_id: int) -> None:
        self.from_user = SimpleNamespace(id=telegram_id)
        self.answers: list[dict[str, object]] = []

    async def answer(self, text: str, **kwargs: object) -> None:
        self.answers.append({"text": text, **kwargs})


class FakeApiClient:
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url

    async def __aenter__(self) -> "FakeApiClient":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    async def get_today_workout(self) -> dict[str, object]:
        return {
            "session": {
                "title": "Ноги A",
                "focus": "квадрицепсы + ягодицы + икры",
                "status": "planned",
            },
            "exercises": [
                {"slot_name": "Жим ногами", "planned_sets": "4", "planned_reps": "6-10"},
                {"slot_name": "Планка", "planned_sets": "2-3", "planned_reps": "time"},
            ],
        }


def test_format_today_message_includes_title_and_exercises() -> None:
    text = format_today_message(
        {
            "session": {"title": "Ноги A", "focus": "квадрицепсы + ягодицы + икры", "status": "planned"},
            "exercises": [{"slot_name": "Жим ногами", "planned_sets": "4", "planned_reps": "6-10"}],
        }
    )

    assert "Ноги A" in text
    assert "квадрицепсы + ягодицы + икры" in text
    assert "Жим ногами" in text
    assert "4 x 6-10" in text


def test_start_denies_users_outside_allowed_list() -> None:
    message = FakeMessage(telegram_id=111)
    settings = BotSettings(
        mini_app_url="https://training.example.com",
        telegram_allowed_user_ids=[222],
    )

    asyncio.run(start(message, settings))

    assert message.answers[0]["text"] == "Доступ закрыт."
    assert "reply_markup" not in message.answers[0]


def test_today_uses_api_and_sends_mini_app_button(monkeypatch) -> None:
    monkeypatch.setattr("app.handlers.TrainingApiClient", FakeApiClient)
    message = FakeMessage(telegram_id=222)
    settings = BotSettings(
        api_url="http://api:8000",
        mini_app_url="https://training.example.com",
        telegram_allowed_user_ids=[222],
    )

    asyncio.run(today(message, settings))

    assert "Ноги A" in str(message.answers[0]["text"])
    assert "Жим ногами" in str(message.answers[0]["text"])
    assert message.answers[0]["reply_markup"] is not None
