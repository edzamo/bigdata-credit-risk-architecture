"""Job Bronze: ingesta cruda de Home Credit Default Risk hacia el Data Lake (sin transformar)."""
import os

from pyspark.sql import DataFrame, SparkSession

from common.medallion_job import MedallionLayerJob
from common.session import get_spark_session
from common.storage import MinioRepository
from ingestion.source_loader import SourceLoaderFactory

BRONZE_BUCKET = "bronze"
BRONZE_PATH = "home_credit/application"
DEFAULT_CSV_PATH = "/opt/app/data/raw/application_train.csv"


class CreditBronzeLoader(MedallionLayerJob):
    def __init__(self, spark: SparkSession, csv_path: str = DEFAULT_CSV_PATH) -> None:
        self._spark = spark
        self._csv_path = csv_path
        self._repository = MinioRepository(spark)

    def extract(self) -> DataFrame:
        loader = SourceLoaderFactory.create("kaggle_credit", csv_path=self._csv_path)
        return loader.load(self._spark)

    def load(self, df: DataFrame) -> None:
        self._repository.write_parquet(df, bucket=BRONZE_BUCKET, path=BRONZE_PATH)


def run_bronze_ingestion(csv_path: str = DEFAULT_CSV_PATH) -> int:
    spark = get_spark_session()
    job = CreditBronzeLoader(spark, csv_path=csv_path)
    df = job.run()
    row_count = df.count()
    print(f"Bronze OK: {row_count} filas escritas en s3a://{BRONZE_BUCKET}/{BRONZE_PATH}")
    return row_count


if __name__ == "__main__":
    run_bronze_ingestion(os.environ.get("CREDIT_CSV_PATH", DEFAULT_CSV_PATH))
