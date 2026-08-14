"""Configuracion de TONY cargada desde variables de entorno / .env (v0.3 S19 paso 2, pendiente S14).

Solo variables no sensibles viven aqui con valores por defecto. Credenciales reales quedan
fuera del codigo (security/secrets, todavia no implementado): en desarrollo se toleran en
.env (gitignored); en produccion deberan venir de un almacen de secretos real.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    tony_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://tony:tony@localhost:5432/tony"


@lru_cache
def get_settings() -> Settings:
    """Settings cacheados por proceso. Usar Settings() directamente en tests para aislar env."""
    return Settings()
