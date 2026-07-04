import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from time import time
from typing import Any
from urllib.parse import parse_qsl


class TelegramAuthError(ValueError):
    pass


@dataclass(frozen=True)
class TelegramUserData:
    telegram_id: int
    username: str | None = None
    first_name: str | None = None


def validate_telegram_init_data(
    init_data: str,
    *,
    bot_token: str,
    allowed_user_ids: list[int],
) -> TelegramUserData:
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("Telegram initData hash is missing")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise TelegramAuthError("Telegram initData signature is invalid")

    user_payload = params.get("user")
    if not user_payload:
        raise TelegramAuthError("Telegram initData user is missing")

    user = json.loads(user_payload)
    telegram_id = int(user["id"])
    if not allowed_user_ids:
        raise TelegramAuthError("Allowed Telegram users are not configured")
    if telegram_id not in allowed_user_ids:
        raise TelegramAuthError("Telegram user is not allowed")

    return TelegramUserData(
        telegram_id=telegram_id,
        username=user.get("username"),
        first_name=user.get("first_name"),
    )


def create_access_token(payload: dict[str, Any], *, secret: str, expires_in_seconds: int = 60 * 60 * 24 * 30) -> str:
    now = int(time())
    claims = {**payload, "iat": now, "exp": now + expires_in_seconds}
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _base64url_json(header),
            _base64url_json(claims),
        ]
    )
    signature = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_base64url_encode(signature)}"


def decode_access_token(token: str, *, secret: str) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError as exc:
        raise TelegramAuthError("JWT structure is invalid") from exc

    signing_input = f"{encoded_header}.{encoded_payload}"
    expected_signature = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(_base64url_encode(expected_signature), encoded_signature):
        raise TelegramAuthError("JWT signature is invalid")

    payload = json.loads(_base64url_decode(encoded_payload))
    if int(payload["exp"]) < int(time()):
        raise TelegramAuthError("JWT is expired")
    return payload


def _base64url_json(value: dict[str, Any]) -> str:
    return _base64url_encode(json.dumps(value, separators=(",", ":"), sort_keys=True).encode())


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _base64url_decode(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}").decode()
