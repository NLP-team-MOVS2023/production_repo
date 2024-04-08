from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    HOST_DB: SecretStr
    PORT_DB: SecretStr
    USER_DB: SecretStr
    PASSWORD_DB: SecretStr
    NAME_DB: SecretStr
    model_config = SettingsConfigDict(
        env_file=r'C:\Users\Надя\PycharmProjects\nlp_project_MOVS\service\baseline\db\.env', env_file_encoding='utf-8')


config = Settings()
