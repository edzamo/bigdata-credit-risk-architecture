"""Repositorios de acceso a almacenamiento (patrón Repository) — MinIO (Data Lake) y PostgreSQL (KPIs).

El código de negocio (`processing/`, `aggregations/`) depende de estas clases, no de `boto3`/JDBC
directamente, para poder testear la lógica de transformación sin infraestructura real.
"""
from typing import List, Optional

from pyspark.sql import DataFrame, SparkSession

from common.settings import Settings, get_settings


class MinioRepository:
    """Lee y escribe Parquet en el Data Lake medallón (bronze/silver/gold) sobre MinIO."""

    def __init__(self, spark: SparkSession, settings: Optional[Settings] = None) -> None:
        self._spark = spark
        self._settings = settings or get_settings()

    @staticmethod
    def _bucket_path(bucket: str, path: str) -> str:
        return f"s3a://{bucket}/{path.strip('/')}"

    def read_parquet(self, bucket: str, path: str) -> DataFrame:
        return self._spark.read.parquet(self._bucket_path(bucket, path))

    def write_parquet(
        self,
        df: DataFrame,
        bucket: str,
        path: str,
        partition_by: Optional[List[str]] = None,
    ) -> None:
        """Escritura idempotente: `overwrite` reemplaza el contenido completo de la ruta."""
        writer = df.write.mode("overwrite")
        if partition_by:
            writer = writer.partitionBy(*partition_by)
        writer.parquet(self._bucket_path(bucket, path))


class PostgresRepository:
    """Escribe datasets agregados (Gold) como tablas consultables desde Power BI/Adminer."""

    def __init__(self, spark: SparkSession, settings: Optional[Settings] = None) -> None:
        self._spark = spark
        self._settings = settings or get_settings()

    def write_table(self, df: DataFrame, table_name: str) -> None:
        """Escritura idempotente: `overwrite` reemplaza la tabla completa en cada corrida."""
        s = self._settings
        (
            df.write.format("jdbc")
            .option("url", s.postgres_jdbc_url)
            .option("dbtable", table_name)
            .option("user", s.postgres_user)
            .option("password", s.postgres_password)
            .option("driver", "org.postgresql.Driver")
            .mode("overwrite")
            .save()
        )
