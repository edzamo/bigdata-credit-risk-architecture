"""Pruebas unitarias de la capa Silver (deduplicación, nulos, idempotencia)."""
from pyspark.sql import Row

from processing.silver_credit_cleaner import SilverCreditCleaner


def test_transform_deduplicates_by_id(spark):
    df = spark.createDataFrame(
        [
            Row(SK_ID_CURR=1, TARGET=0, NAME_INCOME_TYPE="Working", AMT_INCOME_TOTAL=100000.0),
            Row(SK_ID_CURR=1, TARGET=0, NAME_INCOME_TYPE="Working", AMT_INCOME_TOTAL=100000.0),
            Row(SK_ID_CURR=2, TARGET=1, NAME_INCOME_TYPE="Pensioner", AMT_INCOME_TOTAL=50000.0),
        ]
    )
    cleaner = SilverCreditCleaner(spark)

    result = cleaner.transform(df)

    assert result.count() == 2


def test_transform_fills_numeric_nulls_with_median(spark):
    df = spark.createDataFrame(
        [
            Row(SK_ID_CURR=1, AMT_INCOME_TOTAL=100000.0),
            Row(SK_ID_CURR=2, AMT_INCOME_TOTAL=200000.0),
            Row(SK_ID_CURR=3, AMT_INCOME_TOTAL=None),
        ]
    )
    cleaner = SilverCreditCleaner(spark)

    result = cleaner.transform(df)

    assert result.filter(result.AMT_INCOME_TOTAL.isNull()).count() == 0


def test_transform_fills_string_nulls_with_unknown(spark):
    df = spark.createDataFrame(
        [
            Row(SK_ID_CURR=1, NAME_INCOME_TYPE="Working"),
            Row(SK_ID_CURR=2, NAME_INCOME_TYPE=None),
        ]
    )
    cleaner = SilverCreditCleaner(spark)

    result = cleaner.transform(df)

    values = {row.NAME_INCOME_TYPE for row in result.collect()}
    assert "UNKNOWN" in values


def test_transform_drops_rows_with_null_id(spark):
    df = spark.createDataFrame(
        [
            Row(SK_ID_CURR=1, TARGET=0),
            Row(SK_ID_CURR=None, TARGET=1),
        ]
    )
    cleaner = SilverCreditCleaner(spark)

    result = cleaner.transform(df)

    assert result.count() == 1


def test_transform_is_idempotent(spark):
    df = spark.createDataFrame(
        [
            Row(SK_ID_CURR=1, TARGET=0, AMT_INCOME_TOTAL=100000.0),
            Row(SK_ID_CURR=2, TARGET=1, AMT_INCOME_TOTAL=None),
        ]
    )
    cleaner = SilverCreditCleaner(spark)

    once = cleaner.transform(df)
    twice = cleaner.transform(once)

    assert once.count() == twice.count()
