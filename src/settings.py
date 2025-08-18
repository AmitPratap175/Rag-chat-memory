from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent/".env", extra="ignore", env_file_encoding="utf-8")

    DATA_DIR: str


settings = Settings()