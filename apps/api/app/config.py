from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_url: str = "https://training.example.com"
    api_url: str = "https://training.example.com/api"
    mini_app_url: str = "https://training.example.com"

    database_url: str = "postgresql+psycopg://training:training@localhost:5432/training"

    telegram_bot_token: str = Field(default="replace_me")
    telegram_allowed_user_ids: list[int] = Field(default_factory=list)

    jwt_secret: str = Field(default="replace_me_with_long_random_secret")
    admin_secret: str = Field(default="replace_me")

    exercises_dataset_path: str = "/data/exercises-dataset/data/exercises.json"
    raw_media_base: str = "https://raw.githubusercontent.com/olegbal/exercises-dataset/main/"

    allow_admin_endpoints: bool = False
    openai_api_key: str = ""
    openclaw_enabled: bool = False

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
