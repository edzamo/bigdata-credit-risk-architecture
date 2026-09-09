"""Pruebas unitarias del esqueleto Template Method MedallionLayerJob."""
import pytest
from pyspark.sql import Row

from common.medallion_job import MedallionLayerJob


class _DummyJob(MedallionLayerJob):
    def __init__(self, spark, empty: bool = False) -> None:
        self._spark = spark
        self._empty = empty
        self.loaded = None

    def extract(self):
        if self._empty:
            return self._spark.createDataFrame([], "id INT")
        return self._spark.createDataFrame([Row(id=1)])

    def load(self, df) -> None:
        self.loaded = df


def test_run_calls_extract_transform_validate_load_in_order(spark):
    job = _DummyJob(spark)

    result = job.run()

    assert job.loaded is not None
    assert result.count() == 1


def test_run_raises_on_empty_dataframe(spark):
    job = _DummyJob(spark, empty=True)

    with pytest.raises(ValueError):
        job.run()
