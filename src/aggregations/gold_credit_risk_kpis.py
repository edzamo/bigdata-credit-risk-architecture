"""Job Gold: features de riesgo crediticio + KPIs agregados para Power BI."""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from common.medallion_job import MedallionLayerJob
from common.session import get_spark_session
from common.storage import MinioRepository, PostgresRepository

SILVER_BUCKET = "silver"
SILVER_PATH = "home_credit/application"
GOLD_BUCKET = "gold"
GOLD_FEATURES_PATH = "home_credit/credit_risk_features"
GOLD_KPI_TABLE = "gold_credit_risk_kpis"

# Home Credit codifica "sin empleo" como 365243 días en DAYS_EMPLOYED (valor centinela documentado
# en el dataset de Kaggle) — se descarta antes de calcular años de empleo.
DAYS_EMPLOYED_SENTINEL = 365243


class GoldCreditRiskAggregator(MedallionLayerJob):
    def __init__(self, spark: SparkSession) -> None:
        self._spark = spark
        self._minio = MinioRepository(spark)
        self._postgres = PostgresRepository(spark)

    def extract(self) -> DataFrame:
        return self._minio.read_parquet(bucket=SILVER_BUCKET, path=SILVER_PATH)

    def transform(self, df: DataFrame) -> DataFrame:
        return (
            df.withColumn("AGE_YEARS", (-F.col("DAYS_BIRTH") / 365.25).cast("int"))
            .withColumn(
                "YEARS_EMPLOYED",
                F.when(
                    F.col("DAYS_EMPLOYED") < DAYS_EMPLOYED_SENTINEL,
                    -F.col("DAYS_EMPLOYED") / 365.25,
                ),
            )
            .withColumn(
                "CREDIT_INCOME_RATIO",
                F.when(F.col("AMT_INCOME_TOTAL") > 0, F.col("AMT_CREDIT") / F.col("AMT_INCOME_TOTAL")),
            )
            .withColumn(
                "ANNUITY_INCOME_RATIO",
                F.when(F.col("AMT_INCOME_TOTAL") > 0, F.col("AMT_ANNUITY") / F.col("AMT_INCOME_TOTAL")),
            )
        )

    def load(self, df: DataFrame) -> None:
        self._minio.write_parquet(df, bucket=GOLD_BUCKET, path=GOLD_FEATURES_PATH)
        self._postgres.write_table(self._build_kpis(df), GOLD_KPI_TABLE)

    @staticmethod
    def _build_kpis(df: DataFrame) -> DataFrame:
        return (
            df.groupBy("NAME_INCOME_TYPE")
            .agg(
                F.count("*").alias("total_clientes"),
                F.sum("TARGET").alias("clientes_en_default"),
                F.round(F.avg("TARGET") * 100, 2).alias("tasa_default_pct"),
                F.round(F.avg("AMT_CREDIT"), 2).alias("credito_promedio"),
                F.round(F.avg("CREDIT_INCOME_RATIO"), 2).alias("ratio_credito_ingreso_promedio"),
            )
            .orderBy(F.desc("tasa_default_pct"))
        )


def run_gold_aggregation() -> int:
    spark = get_spark_session()
    job = GoldCreditRiskAggregator(spark)
    df = job.run()
    row_count = df.count()
    print(
        f"Gold OK: {row_count} filas de features en s3a://{GOLD_BUCKET}/{GOLD_FEATURES_PATH}; "
        f"KPIs escritos en la tabla PostgreSQL '{GOLD_KPI_TABLE}'"
    )
    return row_count


if __name__ == "__main__":
    run_gold_aggregation()
