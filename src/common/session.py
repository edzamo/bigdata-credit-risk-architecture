"""SparkSession única por proceso (patrón Singleton) con soporte S3A para MinIO y JDBC para PostgreSQL."""
from typing import Optional

from pyspark.sql import SparkSession

from common.settings import get_settings

_spark_session: Optional[SparkSession] = None


def get_spark_session() -> SparkSession:
    """Devuelve la SparkSession compartida del proceso, creándola solo la primera vez."""
    global _spark_session
    if _spark_session is not None:
        return _spark_session

    settings = get_settings()
    _spark_session = (
        SparkSession.builder.appName("bigdata-credit-risk")
        .master(f"local[{settings.spark_local_cores}]")
        .config("spark.driver.memory", settings.spark_driver_memory)
        .config("spark.driver.extraClassPath", "/opt/spark-jars/*")
        .config("spark.executor.extraClassPath", "/opt/spark-jars/*")
        .config("spark.hadoop.fs.s3a.endpoint", settings.minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", settings.minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", settings.minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    _spark_session.sparkContext.setLogLevel("WARN")
    return _spark_session
