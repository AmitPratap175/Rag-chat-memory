from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent/".env", extra="ignore", env_file_encoding="utf-8")

    DATA_DIR: str
    SCRAPED_DIR: str = "chatbot/data/scraped_content"
    DOCUMENTS_DIR: str = "chatbot/data/documents"


settings = Settings()