import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    env_type: Optional[str] = None
    json_file: str = "data/feedback_ratings.json"
    webhook_host: str = "https://bot-xy4x.onrender.com"

    @property
    def webhook_path(self):
        return f"/webhook/{self.bot_token}"

    @property
    def webhook_url(self):
        return f"{self.webhook_host}{self.webhook_path}"

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


class TestSettings(Settings):
    json_file: str = "tests/data/test_feedback_ratings.json"


def get_config() -> Settings:
    env_type: str | None = os.environ.get("ENV_TYPE")
    match env_type:
        case None:
            return Settings()
        case "local":
            return Settings()
        case "test":
            return TestSettings()
        case "docker":
            raise NotImplementedError
        case _:
            raise ValueError(f"{env_type} is not supported")


config = get_config()
