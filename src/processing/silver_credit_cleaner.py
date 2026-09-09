"""Job Silver: deduplicación, tratamiento de nulos y homologación de tipos sobre Bronze."""
from typing import Dict, List, Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import NumericType, StringType

from common.medallion_job import MedallionLayerJob
from common.session import get_spark_session
from common.storage import MinioRepository

BRONZE_BUCKET = "bronze"
BRONZE_PATH = "home_credit/application"
SILVER_BUCKET = "silver"
SILVER_PATH = "home_credit/application"
ID_COLUMN = "SK_ID_CURR"


class SilverCreditCleaner(MedallionLayerJob):
    def __init__(self, spark: SparkSession) -> None:
        self._spark = spark
        self._repository = MinioRepository(spark)

    def extract(self) -> DataFrame:
        return self._repository.read_parquet(bucket=BRONZE_BUCKET, path=BRONZE_PATH)

    def transform(self, df: DataFrame) -> DataFrame:
        df = df.filter(df[ID_COLUMN].isNotNull())
        df = df.dropDuplicates([ID_COLUMN])
        df = self._fill_nulls(df)
        return df

    @staticmethod
    def _fill_nulls(df: DataFrame) -> DataFrame:
        """Estrategia de imputación por tipo de columna: mediana para numéricas, 'UNKNOWN' para texto."""
        numeric_cols: List[str] = [f.name for f in df.schema.fields if isinstance(f.dataType, NumericType)]
        string_cols: List[str] = [f.name for f in df.schema.fields if isinstance(f.dataType, StringType)]

        medians: Dict[str, Optional[float]] = {
            c: df.stat.approxQuantile(c, [0.5], 0.01)[0] if df.stat.approxQuantile(c, [0.5], 0.01) else None
            for c in numeric_cols
        }
        fill_values: Dict[str, object] = {c: v for c, v in medians.items() if v is not None}
        fill_values.update({c: "UNKNOWN" for c in string_cols})
        return df.fillna(fill_values) if fill_values else df

    def load(self, df: DataFrame) -> None:
        self._repository.write_parquet(df, bucket=SILVER_BUCKET, path=SILVER_PATH)


def run_silver_cleaning() -> int:
    spark = get_spark_session()
    job = SilverCreditCleaner(spark)
    df = job.run()
    row_count = df.count()
    print(f"Silver OK: {row_count} filas escritas en s3a://{SILVER_BUCKET}/{SILVER_PATH}")
    return row_count


if __name__ == "__main__":
    run_silver_cleaning()
