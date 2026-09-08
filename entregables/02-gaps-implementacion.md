# Arquitectura Big Data — Riesgo Crediticio
### Memo de gaps — hito Docker + medallón hasta Gold
**Fecha:** 08 de septiembre de 2026
**Ref:** `kick-off-project.md`, `entregables/01-alcance-tecnico.md`, `Plantilla de Proyecto de IEEE APR.docx` (Capítulo II)

Diagnóstico de brechas entre lo que exige el revisor para el próximo avance y lo que existe hoy en el proyecto, más la ruta de implementación para cerrarlas.

> ✅ **Entorno:** el cliente confirma implementación **on-premise con Docker**, sin proveedor cloud. Coincide con lo insinuado por el mensaje del revisor y con lo ya documentado en `entregables/01-alcance-tecnico.md` (sección 4).

---

## 1. Qué exige el revisor (kick-off)

> *"para el siguiente avance me indica que requiero tener arquitectura herramientas en el Docker y el Docker funcionando, arquitectura medallón hasta la parte gold"*

Tres condiciones concretas para el próximo checkpoint:
1. Arquitectura de herramientas **corriendo en Docker** (no solo diagramada).
2. **Docker funcionando** — contenedores levantados y operativos.
3. **Medallón hasta Gold** — Bronze → Silver → Gold funcionando de punta a punta, al menos con el dataset Home Credit Default Risk.

El alcance del revisor es explícitamente técnico: *"la parte técnica NADA MÁS"* — no espera avance de redacción, marco teórico ni metodología (eso ya lo lleva el estudiante con su tutor metodológico).

---

## 2. Qué existe hoy

| Elemento | Estado |
|---|---|
| Capítulo II (diseño de arquitectura de 6 capas) | ✅ Redactado y aprobado — no requiere rediseño |
| Entorno Docker | ❌ No existe |
| Data Lake / medallón (Bronze/Silver/Gold) | ❌ No existe |
| Ingesta del dataset Home Credit Default Risk | ❌ No existe |
| Ingesta de fuentes macroeconómicas (World Bank, IMF, FRED, etc.) | ❌ No existe |
| Procesamiento Spark/PySpark | ❌ No existe |
| Repositorio de código (`src/`, `dags/`, `tests/`) | ❌ No existe — solo plan en `CLAUDE.md` |

En otras palabras: el diseño está completo y aprobado, pero **la implementación técnica todavía no ha arrancado**. Todo el hito pedido por el revisor está por construirse.

---

## 3. Gaps a cerrar para el checkpoint

| # | Gap | Severidad |
|---|---|---|
| 1 | **No hay entorno Docker levantado.** Es el requisito explícito y no negociable del revisor para el próximo avance. | 🔴 Crítico |
| 2 | **No hay Data Lake ni patrón medallón implementado.** El documento pide Bronze/Silver/Gold en Parquet; hoy no existe ningún storage, ni siquiera local. | 🔴 Crítico |
| 3 | **Storage del Data Lake no confirmado (MinIO vs. filesystem local).** El documento no especifica la tecnología de storage subyacente — solo dice "Data Lake" en Parquet. MinIO (S3-compatible) es la opción natural on-premise, pero es una decisión de implementación no explícita en la tesis. | 🟠 Alto |
| 4 | **Sin ingesta del dataset principal.** Home Credit Default Risk (215,257 filas × 102 columnas + 3 tablas relacionadas) todavía no se ha descargado ni cargado a Bronze. | 🔴 Crítico |
| 5 | **Sin acceso confirmado a APIs macroeconómicas.** World Bank, IMF, FRED, Yahoo Finance, Nasdaq Data Link, BIS, EIA — no se sabe si ya hay credenciales/API keys o si eso entra en nuestro alcance de implementación. | 🟠 Alto |
| 6 | **Recursos de hardware local sin validar.** Spark + PostgreSQL + MinIO + Power BI en contenedores simultáneos exige RAM/CPU que no se ha confirmado que el equipo del cliente tenga disponible. | 🟠 Alto |
| 7 | **Delta Lake vs. Parquet plano sin decidir.** El documento especifica Parquet a secas; Parquet plano no soporta `merge`/upsert idempotente nativo, lo cual complica reprocesos en Silver/Gold. Delta Lake lo resolvería pero no está mencionado en la tesis — cambiar de tecnología requeriría justificarlo o mantenerse en Parquet con overwrite particionado. | 🟡 Medio |
| 8 | **Sin repositorio de código estructurado.** La convención de carpetas (`src/common`, `src/ingestion`, `src/processing`, `src/aggregations`, `dags/`, `tests/unit/`) está definida en `CLAUDE.md` pero aún no creada — se crea recién cuando arranque el primer módulo real, para evitar scaffolding vacío. | 🟢 Bajo |

---

## 4. Ruta de implementación propuesta

Para llegar al hito pedido (Docker funcionando + medallón hasta Gold) con el dataset Home Credit Default Risk como primer caso:

1. **`docker-compose.yml`** con los servicios base: MinIO (Data Lake S3-compatible), PostgreSQL (almacenamiento estructurado), y el entorno Spark (standalone o local mode dentro del contenedor de procesamiento).
2. **`src/common/session.py`** — sesión Spark + credenciales/conexión a MinIO y PostgreSQL, parametrizada por variables de entorno (sin credenciales hardcodeadas).
3. **`src/ingestion/credit_bronze_loader.py`** — descarga del dataset Home Credit Default Risk (Kaggle) y escritura a Bronze en Parquet, particionado, con escritura idempotente (`overwrite`).
4. **Capa Silver** — limpieza, deduplicación, tratamiento de nulos y homologación de tipos sobre el dataset principal (aún sin las fuentes macro, para llegar rápido al hito).
5. **Capa Gold** — al menos un dataset analítico agregado (ej. features base para riesgo crediticio) que demuestre el pipeline completo Bronze→Silver→Gold funcionando end-to-end.
6. **Validación end-to-end** — correr el pipeline completo dentro de Docker y confirmar que Gold se genera correctamente antes del checkpoint.

Las fuentes macroeconómicas (World Bank, IMF, FRED, etc.) y la capa de orquestación con Airflow quedan para una segunda iteración, una vez satisfecho el hito mínimo exigido por el revisor.

---

## 5. Preguntas abiertas para el cliente

1. ¿El equipo local tiene los recursos (RAM/CPU) para correr MinIO + Spark + PostgreSQL en contenedores simultáneamente? (Recomendado: mínimo 8 GB RAM disponibles para Docker).
2. ¿Ya existen credenciales/API keys para las fuentes macroeconómicas, o se gestionan como parte de esta consultoría? (No bloquea el hito actual, pero sí la segunda iteración).
3. ¿Se autoriza evaluar Delta Lake como alternativa a Parquet plano para soportar `merge`/upsert idempotente en Silver/Gold, o se mantiene estrictamente lo especificado en el documento (Parquet)?
4. ¿Hay fecha límite del revisor para este checkpoint, más allá de "el siguiente avance"? Esto define si conviene priorizar solo el dataset principal o intentar incluir alguna fuente macro desde ya.

---

## 6. Próximos pasos

1. **Confirmar recursos de hardware y respuestas a la sección 5** con el cliente.
2. **Levantar `docker-compose.yml`** con MinIO, PostgreSQL y el contenedor de procesamiento Spark.
3. **Implementar Bronze** — `src/common/session.py` + `src/ingestion/credit_bronze_loader.py` para Home Credit Default Risk.
4. **Implementar Silver y Gold** sobre el mismo dataset, cerrando el pipeline end-to-end.
5. **Checkpoint con el revisor** — Docker funcionando + medallón hasta Gold, listo para mostrar.

---
*Preparado para el hito de Docker + medallón hasta Gold · Fuente: kick-off del revisor, 08 sept 2026*
