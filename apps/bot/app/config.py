from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
        enable_decoding=False,
    )

    api_url: str = "http://api:8000"
    mini_app_url: str = "http://localhost:5173"
    telegram_bot_token: str = Field(default="replace_me")
    telegram_allowed_user_ids: list[int] = Field(default_factory=list)

    @field_validator("telegram_allowed_user_ids", mode="before")
    @classmethod
    def parse_allowed_user_ids(cls, value: Any) -> list[int]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [int(item) for item in value]
        raise TypeError("telegram_allowed_user_ids must be a comma-separated string or list of integers")

    @property
    def has_real_token(self) -> bool:
        return self.telegram_bot_token not in {"", "replace_me"}


@lru_cache
def get_settings() -> BotSettings:
    return BotSettings()
