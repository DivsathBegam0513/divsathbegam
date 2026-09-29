"""Configuration shared by the API and the Streamlit process."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore")
    ai_provider: Literal["demo", "gemini"] = "demo"
    gemini_api_key: SecretStr = SecretStr("")
    gemini_model: str = "gemini-3.5-flash"
    backend_url: str = "http://127.0.0.1:8000"
    backend_api_key: SecretStr = SecretStr("")
    request_timeout_seconds: int = Field(default=90, ge=5, le=300)
    rate_limit_per_minute: int = Field(default=30, ge=1, le=1000)


@lru_cache
def get_settings() -> Settings:
    return Settings()
