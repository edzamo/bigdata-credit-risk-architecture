"""Prueba unitaria del patrón Singleton para la SparkSession compartida."""
from common.session import get_spark_session


def test_get_spark_session_returns_same_instance():
    first = get_spark_session()
    second = get_spark_session()

    assert first is second
