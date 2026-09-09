"""Factory Method para loaders de fuentes de datos de la capa Bronze.

En el MVP solo existe la fuente del dataset principal (Kaggle, CSV local). Las fuentes
macroeconómicas (World Bank, IMF, FRED, etc.) se agregan aquí en la iteración 2 sin tocar
el resto del pipeline.
"""
from abc import ABC, abstractmethod
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession


class SourceLoader(ABC):
    @abstractmethod
    def load(self, spark: SparkSession) -> DataFrame: ...


class KaggleCreditLoader(SourceLoader):
    """Lee el CSV de Home Credit Default Risk ya descargado localmente (application_train.csv)."""

    def __init__(self, csv_path: str) -> None:
        self._csv_path = csv_path

    def load(self, spark: SparkSession) -> DataFrame:
        if not Path(self._csv_path).exists():
            raise FileNotFoundError(
                f"No se encontró el dataset en '{self._csv_path}'. Descarga "
                "application_train.csv de Kaggle (competencia Home Credit Default Risk) "
                "y colócalo en esa ruta antes de correr la ingesta."
            )
        return (
            spark.read.option("header", True)
            .option("inferSchema", True)
            .csv(self._csv_path)
        )


class SourceLoaderFactory:
    """Devuelve el loader correcto según la fuente pedida."""

    @staticmethod
    def create(source: str, **kwargs: str) -> SourceLoader:
        if source == "kaggle_credit":
            return KaggleCreditLoader(csv_path=kwargs["csv_path"])
        raise ValueError(f"Fuente no soportada en el MVP: '{source}'")
