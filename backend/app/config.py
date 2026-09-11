"""
Descrição: Centraliza e valida as configurações da aplicação e suas integrações.
Autor: Leôncio Ferreira
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./data/vigi.db"

    mqtt_host: str = "mqtt"
    mqtt_port: int = 1883
    mqtt_client_id: str = "vigi-backend"
    mqtt_qos: int = 1
    mqtt_topic_inspections: str = "vigi/esteira/inspecoes"


@lru_cache
def get_settings() -> Settings:
    return Settings()
