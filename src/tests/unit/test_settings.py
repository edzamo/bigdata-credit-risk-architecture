"""Pruebas unitarias de la carga de configuración desde variables de entorno."""
from common.settings import get_settings

_ENV_VARS = [
    "MINIO_ENDPOINT", "MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD",
    "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD",
]


def test_get_settings_uses_defaults_when_env_missing(monkeypatch):
    for var in _ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    settings = get_settings()

    assert settings.postgres_host == "postgres"
    assert settings.postgres_jdbc_url == "jdbc:postgresql://postgres:5432/credit_risk"


def test_get_settings_reads_env_overrides(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "custom-host")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    monkeypatch.setenv("POSTGRES_DB", "custom_db")

    settings = get_settings()

    assert settings.postgres_jdbc_url == "jdbc:postgresql://custom-host:6543/custom_db"
