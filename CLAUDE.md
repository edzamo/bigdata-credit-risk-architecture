# Proyecto: Arquitectura Big Data — Riesgo Crediticio (Trabajo de Titulación)

## Rol de Claude en este proyecto
Actuar como **arquitecto de soluciones de Big Data**, con alcance **limitado a la implementación técnica**:
- ✅ Diagnóstico del alcance ya realizado (ver `docs/01-alcance-tecnico.md`).
- 🔜 Implementar la arquitectura de 6 capas ya definida en el documento de tesis (Docker, medallón hasta Gold, ingesta, Spark, analítica, Power BI).
- ❌ **Fuera de alcance:** redacción de capítulos, marco teórico, metodología, discusión — eso lo maneja el estudiante con su tutor metodológico. Aquí solo nos ocupamos del desarrollo/implementación técnica.

## Contexto del proyecto
Trabajo de titulación (Universidad Tecnológica Israel — UISRAEL), formato de tesis con metodología **CRISP-DM**. Tema: **Arquitectura Big Data para integrar y analizar la evolución del riesgo crediticio en entidades financieras**, orientada a optimizar decisiones de concesión de créditos.

Dataset principal: **Home Credit Default Risk** (Kaggle, 215,257 filas × 102 columnas + tablas relacionadas), complementado con fuentes macroeconómicas y financieras: World Bank, IMF, FRED, Yahoo Finance, Nasdaq Data Link, BIS, EIA.

## Estructura del repositorio
Dos carpetas principales: `src/` (todo lo ejecutable — Docker Compose, imágenes y, más adelante, el código del pipeline) y `docs/` (toda la documentación de la consultoría). Ver `README.md` para el árbol completo.

- `docs/kick-off-project.md` — mensajes de WhatsApp del revisor/tutor con el siguiente hito exigido: Docker funcionando + arquitectura medallón hasta capa Gold. (Insumo confidencial, no se versiona.)
- `docs/Plantilla de Proyecto de IEEE APR.docx` — documento de tesis (ya redactado en gran parte, no una plantilla vacía). Contiene el Capítulo I (diagnóstico) y Capítulo II (propuesta de arquitectura) ya definidos. (Insumo confidencial, no se versiona.)
- `docs/01-alcance-tecnico.md` — nota de alcance con el resumen del proyecto, la arquitectura de 6 capas ya especificada en el documento, confirmación de que **no hay nube definida** (todo apunta a on-premise/Docker según el kick-off), y las preguntas abiertas para el cliente.
- `docs/02-gaps-implementacion.md` — gaps entre lo exigido por el revisor y lo que existe, con ruta de implementación.
- `docs/03-arquitectura-poc-mvp.md` — diseño de la PoC/MVP: diagramas de arquitectura, red/puertos, comportamiento del pipeline y patrones de diseño.

## Arquitectura ya definida en el documento (Capítulo II) — NO diseñar, IMPLEMENTAR
6 capas, con herramientas ya especificadas por el propio documento de tesis:
1. **Fuentes de datos**: Home Credit Default Risk, World Bank, IMF, FRED, Yahoo Finance, Nasdaq Data Link, BIS.
2. **Ingesta**: Python, APIs REST, procesos ETL.
3. **Data Lake (medallón)**: Bronze → Silver → Gold, formato Parquet.
4. **Procesamiento distribuido**: Apache Spark / PySpark (limpieza, transformación, integración, feature engineering).
5. **Analítica**: descriptivo, correlaciones, indicadores, ML (Random Forest, XGBoost).
6. **Consumo**: Power BI (dashboard ejecutivo, dashboard de riesgo, KPIs financieros).

Stack adicional: PostgreSQL, Pandas/NumPy, Scikit-learn, Matplotlib/Seaborn.

## Nube: NO definida
El documento no menciona AWS/GCP/Azure en ningún punto — todas las herramientas son agnósticas de infraestructura. El mensaje de kick-off del revisor ("arquitectura herramientas en el Docker... hasta la parte gold") apunta a **on-premise con Docker**, igual que en `project-bigdata-01`. No se ha planteado alternativa cloud para este proyecto; si el cliente la pide, habría que generar un memo de decisión similar al de proyecto 01.

## Próximo hito (pedido explícitamente por el revisor)
- Arquitectura de herramientas corriendo en Docker.
- Docker funcionando (contenedores levantados).
- Arquitectura medallón implementada **hasta la capa Gold**, funcionando end-to-end (al menos con el dataset Home Credit Default Risk).

## Preguntas abiertas para el cliente
1. ¿Confirma implementación on-premise con Docker (no cloud)?
2. ¿El equipo local tiene recursos suficientes (RAM/CPU) para Spark + PostgreSQL + Power BI en contenedores?
3. ¿Hay ya credenciales/acceso a las APIs macroeconómicas, o eso también entra en nuestro alcance?

## Notas de estilo/trabajo
- Este proyecto es distinto al de `project-bigdata-01` (esa es una tesis de arquitectura big data aplicada a rutas de transporte NYC/Quito). No mezclar contextos.
- Aquí la arquitectura objetivo **ya viene definida por el documento** — el trabajo es de implementación, no de diseño desde cero ni de negociación de alcance con el tutor académico.

---

## Convenciones de desarrollo (plan — crear solo cuando arranque la implementación)

Repositorio de ecosistema Big Data con arquitectura de medalla (Bronze / Silver / Gold). `src/` es la única carpeta de desarrollo: ya contiene `docker-compose.yml` y `docker/` (imagen Spark/Jupyter); el código Python modular (`common/`, `ingestion/`, `processing/`, `aggregations/`, `dags/`, `tests/unit/`) se agrega ahí mismo, como hermanos de `docker-compose.yml`. **No crear las carpetas de código todavía** — son el plan para cuando escribamos el primer módulo real (el hito de Docker + medallón hasta Gold). Evitamos scaffolding vacío sin lógica.

### Stack tecnológico
- **Procesamiento**: PySpark (Spark 3.x) — confirmado explícitamente en el documento de tesis.
- **Lenguaje**: Python 3.11 con type hints explícitos (versión no especificada en el documento, se adopta como estándar).
- **Formato de almacenamiento**: Parquet — confirmado en el documento. ⚠️ El documento no menciona Delta Lake; a evaluar con el cliente si conviene adoptarlo para soportar `merge`/upsert idempotente en la capa Silver/Gold, o mantenernos en Parquet plano tal como está especificado.
- **Storage medallón**: MinIO (compatible S3) sobre Docker — no está explícito en el documento, pero es la implementación natural del "Data Lake" que sí menciona, dado que todo apunta a on-premise (ver kick-off). A confirmar con el cliente (pregunta abierta #1 en `docs/01-alcance-tecnico.md`).
- **Almacenamiento estructurado**: PostgreSQL — confirmado en el documento.
- **Orquestación**: Apache Airflow — no exigido explícitamente en el documento ni en el kick-off; se adopta como estándar de la consultoría para automatizar Bronze→Silver→Gold.
- **Analítica/ML**: Scikit-learn (Random Forest, XGBoost), Pandas/NumPy — confirmados en el documento.
- **Visualización**: Power BI — confirmado en el documento.
- **Calidad y pruebas**: Pytest / Great Expectations — no exigido explícitamente, estándar propio de la consultoría (relevante aquí por la exigencia de "calidad de datos" como métrica de evaluación de la arquitectura, capítulo I del documento).

### Estructura de carpetas (dentro de `src/`)
- `src/docker-compose.yml`, `src/docker/`, `src/.env.example` — infraestructura (ya implementada).
- `src/data/`, `src/notebooks/` — datos locales y notebooks de validación (ignorados por git, solo `.gitkeep`).
- `src/common/` — modelos y lógica reutilizable (conexión a MinIO/S3, PostgreSQL, config de sesión Spark).
- `src/ingestion/` — lógica de ingesta (Bronze): extracción desde Home Credit Default Risk (Kaggle) y APIs macroeconómicas (World Bank, IMF, FRED, Yahoo Finance, Nasdaq Data Link, BIS, EIA).
- `src/processing/` — limpieza, deduplicación e idempotencia (Silver): tratamiento de duplicados, valores faltantes, homologación de formatos.
- `src/aggregations/` — agregaciones y métricas finales (Gold): datasets analíticos enriquecidos, features para Random Forest/XGBoost, KPIs para Power BI.
- `src/dags/` — orquestación (Airflow) únicamente.
- `src/tests/unit/` — pruebas unitarias correspondientes a cada módulo nuevo.

### Reglas de código
1. Respetar la estructura de carpetas de arriba — no mezclar lógica de capas distintas en un mismo módulo.
2. Type hints explícitos en todo el código Python (`pyspark.sql.DataFrame`, `Dict`, `Optional`, etc.).
3. Evitar UDFs de Python en Spark salvo estrictamente necesario; priorizar funciones nativas de `pyspark.sql.functions`.
4. Escrituras siempre idempotentes (`overwrite` particionado, o `merge` si se adopta Delta Lake).
5. Al crear o modificar código, indicar siempre el file path exacto (ej. `src/processing/silver_credit_cleaner.py`).
6. Toda función/módulo nuevo lleva su prueba unitaria correspondiente en `src/tests/unit/`.

### Tarea inicial
Definida por el kick-off del revisor: dejar **Docker funcionando con la arquitectura de herramientas** y la **arquitectura medallón implementada hasta la capa Gold** (al menos con el dataset Home Credit Default Risk). Primer paso técnico concreto: `src/common/session.py` (sesión Spark + conexión MinIO/PostgreSQL) y `src/ingestion/credit_bronze_loader.py` para la ingesta inicial de Home Credit Default Risk a la capa Bronze.
