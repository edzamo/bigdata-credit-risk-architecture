"""Pruebas unitarias de la capa Gold (features de riesgo + KPIs agregados)."""
from pyspark.sql import Row

from aggregations.gold_credit_risk_kpis import GoldCreditRiskAggregator


def _sample_df(spark):
    return spark.createDataFrame(
        [
            Row(
                SK_ID_CURR=1, TARGET=0, NAME_INCOME_TYPE="Working",
                DAYS_BIRTH=-10950, DAYS_EMPLOYED=-1825,
                AMT_INCOME_TOTAL=100000.0, AMT_CREDIT=200000.0, AMT_ANNUITY=10000.0,
            ),
            Row(
                SK_ID_CURR=2, TARGET=1, NAME_INCOME_TYPE="Working",
                DAYS_BIRTH=-14600, DAYS_EMPLOYED=365243,  # centinela "sin empleo" del dataset real
                AMT_INCOME_TOTAL=50000.0, AMT_CREDIT=150000.0, AMT_ANNUITY=7500.0,
            ),
        ]
    )


def test_transform_computes_age_and_ratios(spark):
    aggregator = GoldCreditRiskAggregator(spark)

    result = aggregator.transform(_sample_df(spark))

    row = result.filter(result.SK_ID_CURR == 1).first()
    assert row.AGE_YEARS == 30
    assert round(row.CREDIT_INCOME_RATIO, 1) == 2.0


def test_transform_handles_employment_sentinel_value(spark):
    aggregator = GoldCreditRiskAggregator(spark)

    result = aggregator.transform(_sample_df(spark))

    row = result.filter(result.SK_ID_CURR == 2).first()
    assert row.YEARS_EMPLOYED is None


def test_build_kpis_aggregates_by_income_type(spark):
    aggregator = GoldCreditRiskAggregator(spark)
    transformed = aggregator.transform(_sample_df(spark))

    kpis = aggregator._build_kpis(transformed)

    row = kpis.filter(kpis.NAME_INCOME_TYPE == "Working").first()
    assert row.total_clientes == 2
    assert row.clientes_en_default == 1
