"""Configuración leída desde variables de entorno para toda la app."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    spark_local_cores: str
    spark_driver_memory: str

    @property
    def postgres_jdbc_url(self) -> str:
        return f"jdbc:postgresql://{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


def get_settings() -> Settings:
    return Settings(
        minio_endpoint=os.environ.get("MINIO_ENDPOINT", "http://minio:9000"),
        minio_access_key=os.environ.get("MINIO_ROOT_USER", "bigdata_admin"),
        minio_secret_key=os.environ.get("MINIO_ROOT_PASSWORD", "bigdata_password_change_me"),
        postgres_host=os.environ.get("POSTGRES_HOST", "postgres"),
        postgres_port=int(os.environ.get("POSTGRES_PORT", "5432")),
        postgres_db=os.environ.get("POSTGRES_DB", "credit_risk"),
        postgres_user=os.environ.get("POSTGRES_USER", "bigdata_admin"),
        postgres_password=os.environ.get("POSTGRES_PASSWORD", "bigdata_password_change_me"),
        spark_local_cores=os.environ.get("SPARK_LOCAL_CORES", "2"),
        spark_driver_memory=os.environ.get("SPARK_DRIVER_MEMORY", "2g"),
    )
