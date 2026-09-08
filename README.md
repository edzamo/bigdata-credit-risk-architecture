<<<<<<< HEAD
# bigdata-credit-risk-architecture
ecosistema de bigdata poc
=======
# Bigdata Credit Risk Architecture

Diseño e implementación de un ecosistema de Big Data (arquitectura de medalla — Bronze / Silver / Gold) para analizar la evolución del riesgo crediticio en entidades financieras, integrando datos crediticios, macroeconómicos y de mercado.

Trabajo de consultoría de implementación técnica para un proyecto académico. Este repositorio documenta el alcance técnico y la arquitectura de referencia (ya definida en el diseño de la investigación) que se está construyendo.

## Contenido
- [`CLAUDE.md`](CLAUDE.md) — contexto completo del proyecto: arquitectura de 6 capas, stack tecnológico, alcance de la consultoría.
- [`entregables/`](entregables) — nota de alcance técnico.

## Arquitectura (6 capas)
Fuentes de datos → Ingesta (Python/APIs/ETL) → Data Lake medallón (Bronze/Silver/Gold, Parquet) → Procesamiento distribuido (Apache Spark) → Analítica (Random Forest, XGBoost) → Consumo (Power BI).

## Stack
Python · PySpark · PostgreSQL · Parquet · Power BI · Docker (on-premise).

---
Nota: los insumos originales del proyecto (comunicaciones y documento de tesis) se mantienen fuera de este repositorio por confidencialidad.
>>>>>>> 428ca83 (Alcance técnico y arquitectura del ecosistema Big Data de riesgo crediticio)
