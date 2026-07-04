import hashlib
import hmac
import json
from urllib.parse import urlencode

import pytest

from app.services.telegram_auth import (
    TelegramAuthError,
    create_access_token,
    decode_access_token,
    validate_telegram_init_data,
)


def signed_init_data(bot_token: str, user: dict[str, object], extra: dict[str, str] | None = None) -> str:
    params = {
        "auth_date": "1783179000",
        "query_id": "AAH-test-query",
        "user": json.dumps(user, separators=(",", ":")),
    }
    if extra:
        params.update(extra)
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    params["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(params)


def test_validate_telegram_init_data_accepts_signed_allowed_user() -> None:
    init_data = signed_init_data(
        "123:bot-token",
        {"id": 123456789, "username": "coach", "first_name": "Alex"},
    )

    user = validate_telegram_init_data(
        init_data,
        bot_token="123:bot-token",
        allowed_user_ids=[123456789],
    )

    assert user.telegram_id == 123456789
    assert user.username == "coach"
    assert user.first_name == "Alex"


def test_validate_telegram_init_data_rejects_tampered_payload() -> None:
    init_data = signed_init_data("123:bot-token", {"id": 123456789}).replace("123456789", "123456780")

    with pytest.raises(TelegramAuthError):
        validate_telegram_init_data(init_data, bot_token="123:bot-token", allowed_user_ids=[123456789])


def test_validate_telegram_init_data_rejects_non_allowed_user() -> None:
    init_data = signed_init_data("123:bot-token", {"id": 222})

    with pytest.raises(TelegramAuthError):
        validate_telegram_init_data(init_data, bot_token="123:bot-token", allowed_user_ids=[123456789])


def test_validate_telegram_init_data_rejects_when_allowed_users_not_configured() -> None:
    init_data = signed_init_data("123:bot-token", {"id": 123456789})

    with pytest.raises(TelegramAuthError):
        validate_telegram_init_data(init_data, bot_token="123:bot-token", allowed_user_ids=[])


def test_access_token_round_trip() -> None:
    token = create_access_token({"sub": "user-id", "telegram_id": 123456789}, secret="jwt-secret")

    payload = decode_access_token(token, secret="jwt-secret")

    assert payload["sub"] == "user-id"
    assert payload["telegram_id"] == 123456789
