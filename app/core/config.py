from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    env: Literal["development", "staging", "production", "test"] = Field(default="development")

    api_v1_prefix: str = "/api/v1"
    project_name: str = "Ecommerce API"
    project_description: str = "Production-ready ecommerce REST API"
    project_version: str = "1.0.0"

    debug: bool = False
    allowed_hosts: str = Field(default="*")
    cors_origins: str = Field(default="*")

    secret_key: str = Field(default="change-me")
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    jwt_algorithm: str = "HS256"

    database_url: str = Field(
        default="mssql+pyodbc://sa:Password123!@mssql:1433/ecommerce?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_pre_ping: bool = True

    redis_url: str = "redis://redis:6379/0"
    redis_cache_ttl_seconds: int = 120

    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    rate_limit_per_minute: int = 120

    sentry_dsn: AnyUrl | None = None

    # Email simulation
    email_from: str = "no-reply@ecommerce.local"

    def _parse_csv(self, value: str) -> list[str]:
        value = (value or "").strip()
        if value == "*" or value == "":
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        return self._parse_csv(self.allowed_hosts)

    @property
    def cors_origins_list(self) -> list[str]:
        return self._parse_csv(self.cors_origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()
