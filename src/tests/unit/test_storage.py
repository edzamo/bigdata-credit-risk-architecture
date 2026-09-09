"""Pruebas unitarias del repositorio MinIO (patrón Repository) — solo construcción de rutas, sin IO real."""
from common.storage import MinioRepository


def test_bucket_path_builds_s3a_uri():
    assert MinioRepository._bucket_path("bronze", "home_credit/application") == "s3a://bronze/home_credit/application"


def test_bucket_path_strips_leading_and_trailing_slash():
    assert MinioRepository._bucket_path("silver", "/home_credit/application/") == "s3a://silver/home_credit/application"
