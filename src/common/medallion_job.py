"""Esqueleto común (patrón Template Method) para los jobs Bronze/Silver/Gold.

Cada capa implementa `extract`/`load` (y opcionalmente `transform`); `run()` fija el orden
extract -> transform -> validate -> load para las tres capas del medallón.
"""
from abc import ABC, abstractmethod

from pyspark.sql import DataFrame


class MedallionLayerJob(ABC):
    def run(self) -> DataFrame:
        df = self.extract()
        df = self.transform(df)
        self.validate(df)
        self.load(df)
        return df

    @abstractmethod
    def extract(self) -> DataFrame:
        """Lee el input de la capa (fuente externa o capa anterior del medallón)."""

    def transform(self, df: DataFrame) -> DataFrame:
        """Por defecto no transforma nada; cada capa sobreescribe lo que necesite."""
        return df

    def validate(self, df: DataFrame) -> None:
        """Chequeo mínimo compartido: ninguna capa debe producir un resultado vacío."""
        if df.rdd.isEmpty():
            raise ValueError(f"{type(self).__name__}: el DataFrame resultante está vacío")

    @abstractmethod
    def load(self, df: DataFrame) -> None:
        """Escribe el resultado (Data Lake y/o PostgreSQL), siempre de forma idempotente."""
