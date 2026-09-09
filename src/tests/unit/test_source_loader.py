"""Pruebas unitarias del Factory Method de loaders de fuentes (capa Bronze)."""
import pytest

from ingestion.source_loader import KaggleCreditLoader, SourceLoaderFactory


def test_factory_returns_kaggle_loader_for_known_source():
    loader = SourceLoaderFactory.create("kaggle_credit", csv_path="/tmp/does-not-matter.csv")

    assert isinstance(loader, KaggleCreditLoader)


def test_factory_raises_for_unknown_source():
    with pytest.raises(ValueError):
        SourceLoaderFactory.create("unknown_source")


def test_kaggle_loader_raises_when_csv_missing(spark, tmp_path):
    missing_path = tmp_path / "does-not-exist.csv"
    loader = KaggleCreditLoader(csv_path=str(missing_path))

    with pytest.raises(FileNotFoundError):
        loader.load(spark)
