from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "development"
    database_url: str = "sqlite:///./data/cineplay.db"
    jwt_secret: str = "development-only-secret-change-before-production"
    session_cookie_name: str = "cineplay_session"
    cookie_secure: bool = False
    frontend_origins: list[str] = ["http://localhost:3000"]
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-20b"
    llm_mode: str = "mock"
    llm_timeout_seconds: int = Field(default=20, ge=5, le=60)
    llm_max_tokens: int = Field(default=500, ge=100, le=1500)
    chat_max_rows: int = Field(default=20, ge=1, le=50)
    admin_email: str = "admin@cineplay.example.com"
    admin_password: str | None = None
    admin_name: str = "Administrador"
    demo_user_email: str = "usuario@cineplay.example.com"
    demo_user_password: str | None = None
    demo_user_name: str = "Usuario Demo"

    @field_validator("frontend_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.lstrip().startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("llm_mode")
    @classmethod
    def validate_llm_mode(cls, value: str) -> str:
        if value not in {"mock", "groq"}:
            raise ValueError("LLM_MODE debe ser mock o groq")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
