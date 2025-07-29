from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.parent/".env", extra="ignore", env_file_encoding="utf-8")

    GOOGLE_API_KEY: str
    # ELEVENLABS_API_KEY: str
    # ELEVENLABS_VOICE_ID: str
    # TOGETHER_API_KEY: str

    QDRANT_API_KEY: str | None
    QDRANT_URL: str
    # QDRANT_PORT: str = "6333"
    # QDRANT_HOST: str | None = None
    WHATSAPP_PHONE_NUMBER_ID: str = "737836732745461"
    WHATSAPP_TOKEN: str= "EAAWkndygUyIBPJ1aNdwMgR2ghggdbKmlEDigyarGtGtW2hUnwZADDCPICgTJFGUMAqqHmQHF0UZCQJqL4fxUd9L0wf61iwZA17NwizROSI9MkdMQ4K4oRAJpZCdfD2AyxfqThXGtKBDImk7vnGpGaYDydefhk8GujwtGdwJZAzTt0WZAJoftTZBgd2d5iFOggm9vZAXhgQrUzZBiBZAZAXiNSwTvRHRCf85QXbuzPfb3XeAYLtQpAZDZD"
    WHATSAPP_VERIFY_TOKEN: str = "Brahmware2025"


    TEXT_MODEL_NAME: str = "gemini-2.0-flash"
    SMALL_TEXT_MODEL_NAME: str = "gemma2-9b-it"
    STT_MODEL_NAME: str = "gemini-2.0-flash"
    TTS_MODEL_NAME: str = "gemini-2.5-flash-preview-tts"
    ITT_MODEL_NAME: str = "gemini-2.0-flash"
    TTI_MODEL_NAME: str = "models/gemini-2.0-flash-exp-image-generation"

    MEMORY_TOP_K: int = 3
    RAG_TOP_K: int = 3
    ROUTER_MESSAGES_TO_ANALYZE: int = 3
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 20
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5

    SHORT_TERM_MEMORY_DB_PATH: str = "memory.db"


settings = Settings()
