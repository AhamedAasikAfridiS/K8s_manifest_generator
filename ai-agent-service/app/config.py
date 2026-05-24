"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "K8s Manifest AI Agent Service"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8002

    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"

    openai_api_key: str = ""
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    use_mock_llm: bool = True

    upload_dir: str = "uploads"
    generated_dir: str = "generated"
    max_upload_size_mb: int = 10

    cors_origins: str = "http://localhost:5173"

    kube_score_path: str = "kube-score"
    kube_linter_path: str = "kube-linter"
    enable_kube_score: bool = True
    enable_kube_linter: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def generated_path(self) -> Path:
        return Path(self.generated_dir)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def should_use_mock(self) -> bool:
        if self.use_mock_llm:
            return True
        return not bool(self.openai_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
