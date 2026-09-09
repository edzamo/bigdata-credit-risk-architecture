# Bigdata Credit Risk Architecture

PoC/MVP de un ecosistema Big Data (arquitectura de medalla — Bronze / Silver / Gold) para analizar la evolución del riesgo crediticio en entidades financieras, sobre el dataset **Home Credit Default Risk**.

Trabajo de consultoría de implementación técnica para un proyecto de titulación (UISRAEL). La arquitectura de 6 capas ya fue diseñada y aprobada en el documento de tesis (Capítulo II) — este repositorio implementa esa arquitectura como PoC 100% open source y dockerizada, pensada para correr completa en **una sola máquina/VM con recursos mínimos**.

## Estructura del repositorio

Dos carpetas principales: `src/` (todo lo ejecutable) y `docs/` (toda la documentación).

```
.
├── CLAUDE.md                 # Contexto del proyecto: arquitectura, alcance, convenciones de código
├── README.md                 # Este archivo
│
├── src/                       # Fuente de desarrollo
│   ├── docker-compose.yml     # Orquesta MinIO, PostgreSQL, Adminer, Spark/Jupyter en una red bridge
│   ├── .env.example           # Variables de entorno necesarias (sin credenciales reales)
│   ├── docker/spark-processing/  # Imagen PySpark 3.5.1 + Java 17 usada por Spark y Jupyter
│   ├── data/                  # Datasets locales — ignorado por git, solo .gitkeep
│   ├── notebooks/             # Notebooks de validación por capa — ignorado por git, solo .gitkeep
│   ├── common/                # (pendiente) Sesión Spark, repositorios MinIO/PostgreSQL
│   ├── ingestion/              # (pendiente) Capa Bronze
│   ├── processing/             # (pendiente) Capa Silver
│   ├── aggregations/           # (pendiente) Capa Gold
│   ├── dags/                   # (pendiente) Orquestación Airflow
│   └── tests/unit/             # (pendiente) Pruebas unitarias, una por módulo
│
└── docs/                       # Documentación de la consultoría
    ├── 01-alcance-tecnico.md
    ├── 02-gaps-implementacion.md
    └── 03-arquitectura-poc-mvp.md   # Arquitectura, diagramas, patrones de diseño, red y puertos
```

> `.claude/` (configuración de subagentes de Claude Code usados durante la consultoría) es local y no se versiona — no forma parte del entregable técnico de la tesis.

## Arquitectura (6 capas)

Fuentes de datos → Ingesta (Python/APIs/ETL) → Data Lake medallón (Bronze/Silver/Gold, Parquet en MinIO) → Procesamiento distribuido (Apache Spark) → Analítica (Random Forest, XGBoost) → Consumo (Power BI).

Diagramas de arquitectura, red/puertos y comportamiento del pipeline: [`docs/03-arquitectura-poc-mvp.md`](docs/03-arquitectura-poc-mvp.md).

## Stack

Python 3.11 · PySpark 3.5.1 · MinIO (S3-compatible) · PostgreSQL · Parquet · Power BI · Docker / Docker Compose (on-premise, sin proveedor cloud).

## Cómo levantarlo

```bash
cd src
cp .env.example .env      # ajustar credenciales/recursos si hace falta
docker compose up -d
```

| Servicio | URL local |
|---|---|
| MinIO Console | http://localhost:9001 |
| Adminer (PostgreSQL) | http://localhost:9080 |
| Spark UI | http://localhost:9040 |
| Jupyter Lab | http://localhost:9888 |

Ningún puerto usa 8080 (se reservó el rango 90xx en adelante) para evitar choques con otros servicios en la máquina donde se replique. Detalle completo de puertos y dimensionamiento de recursos en [`docs/03-arquitectura-poc-mvp.md`](docs/03-arquitectura-poc-mvp.md).

---
Nota: los insumos originales del proyecto (comunicaciones y documento de tesis del cliente) se mantienen fuera de este repositorio por confidencialidad.
