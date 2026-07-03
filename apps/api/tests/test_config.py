from app.config import Settings


def test_settings_parse_allowed_telegram_ids_from_comma_separated_env() -> None:
    settings = Settings(
        telegram_bot_token="123:token",
        telegram_allowed_user_ids="123, 456,789",
        jwt_secret="secret-value",
        admin_secret="admin-value",
    )

    assert settings.telegram_allowed_user_ids == [123, 456, 789]


def test_settings_default_admin_endpoints_disabled() -> None:
    settings = Settings(
        telegram_bot_token="123:token",
        telegram_allowed_user_ids="123",
        jwt_secret="secret-value",
        admin_secret="admin-value",
    )

    assert settings.allow_admin_endpoints is False
