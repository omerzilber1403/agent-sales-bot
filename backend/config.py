from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # pydantic-settings v2
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # כלליים
    ENV: str = "dev"

    # ספק מודל: mock | ollama | openai
    LLM_PROVIDER: str = "openai"  # שינוי ברירת מחדל ל-OpenAI

    # OpenAI (ספק ראשי)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"  # מודל ברירת מחדל
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 256

    # Ollama (לוקאלי, חינמי)
    OLLAMA_HOST: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: Optional[str] = None  # למשל: llama3.2:3b

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"DEBUG: Config loaded - LLM_PROVIDER: {settings.LLM_PROVIDER}")  # Debug info
    print(f"DEBUG: Config loaded - OPENAI_API_KEY exists: {bool(settings.OPENAI_API_KEY)}")  # Debug info
    return settings
