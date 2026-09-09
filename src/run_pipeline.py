"""Orquesta el pipeline completo Bronze -> Silver -> Gold en una sola ejecución.

Punto de entrada usado por el servicio `pipeline-runner` de docker-compose.yml, para que
levantar el ecosistema con un solo comando (`docker compose up`) deje el medallón completo
funcionando de punta a punta.
"""
import os
import sys

from aggregations.gold_credit_risk_kpis import run_gold_aggregation
from ingestion.credit_bronze_loader import DEFAULT_CSV_PATH, run_bronze_ingestion
from processing.silver_credit_cleaner import run_silver_cleaning


def main() -> None:
    csv_path = os.environ.get("CREDIT_CSV_PATH", DEFAULT_CSV_PATH)

    print("=== Bronze ===", flush=True)
    run_bronze_ingestion(csv_path)

    print("=== Silver ===", flush=True)
    run_silver_cleaning()

    print("=== Gold ===", flush=True)
    run_gold_aggregation()

    print("Pipeline Bronze -> Silver -> Gold completado.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
