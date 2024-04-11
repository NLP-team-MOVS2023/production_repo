from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from sqlalchemy import URL

import os


class Settings(BaseSettings):
    HOST_DB: str
    PORT_DB: str
    USER_DB: str
    PASSWORD_DB: str
    NAME_DB: str

    env_type: Optional[str] = None

    @property
    def connection_url(self):
        url_object = URL.create(
            "postgresql",
            username=self.USER_DB,
            password=self.PASSWORD_DB,
            host=self.HOST_DB,
            port=self.PORT_DB,
            database=self.NAME_DB,
        )
        return url_object

    model_config = SettingsConfigDict(
        env_file=r"service/baseline/db/.env", env_file_encoding="utf-8"
    )


class TestSettings(Settings):

    @property
    def connection_url(self):
        return "sqlite:///:memory:"


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
