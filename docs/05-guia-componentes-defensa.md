# Guía de componentes — qué hace cada pieza y cómo demostrarlo
### Para entender y defender la arquitectura, no solo para levantarla
**Fecha:** 09 de septiembre de 2026
**Ref:** `docs/03-arquitectura-poc-mvp.md` (arquitectura técnica), `docs/04-manual-usuario.md` (paso a paso operativo), Capítulo II del documento de tesis

Este documento es distinto a los otros dos: `docs/03` explica *cómo está diseñado* y `docs/04` explica *cómo levantarlo y verificarlo*. Este explica, en simple, **qué es y para qué sirve cada pieza**, **dónde ver el resultado**, y **cómo repetir la demo en vivo** si el profesor pide "hazlo de nuevo".

---

## 1. El mapa completo, en una frase por pieza

| # | Capa (tesis, Cap. II) | Herramienta | En una frase |
|---|---|---|---|
| 1 | Fuentes de datos | Kaggle (Home Credit Default Risk) | De ahí viene el dato crudo: 307,511 solicitudes de crédito reales, anonimizadas |
| 2 | Ingesta | Python (`ingestion/`) | Lee el CSV y lo mete al Data Lake sin tocarlo |
| 3 | Data Lake (medallón) | **MinIO** | Guarda los datos en 3 estados: crudo (Bronze), limpio (Silver), listo para analizar (Gold) |
| 4 | Procesamiento distribuido | **Spark / PySpark** | El motor que limpia, transforma y calcula |
| 5 | Analítica / estructurado | **PostgreSQL** | Guarda los KPIs ya calculados, en tablas que cualquier BI entiende |
| 6 | Consumo | **Metabase** (dashboard open source) | Donde se ve el resultado final |
| — | Soporte | **Jupyter**, **Adminer**, **Spark UI** | Ventanas para *comprobar* que las capas de arriba funcionan |

**La idea que hay que poder explicar en una frase:** el dato nunca se modifica donde llegó — cada capa escribe una copia mejorada en la siguiente (Bronze → Silver → Gold). Eso es la "arquitectura medallón".

---

## 2. Ficha rápida de cada herramienta

| Herramienta | Qué es | Para qué sirve aquí | Cómo verla |
|---|---|---|---|
| **MinIO** | "Disco" que habla el protocolo S3 (el estándar de facto para Data Lakes) | Guarda los Parquet de bronze/silver/gold | http://localhost:9001 |
| **Spark / PySpark** | Motor que procesa datos en paralelo | Corre los 3 jobs (Bronze→Silver→Gold): limpia, transforma, calcula KPIs | Spark UI, ver sección 4 |
| **PostgreSQL** | Base de datos relacional clásica (SQL) | Recibe solo el resultado final (Gold) — el "puente" hacia BI | Adminer o `psql` |
| **Jupyter Lab** | Cuaderno interactivo de Python | Explorar datos y correr el notebook-dashboard (sección 3) | http://localhost:9888 |
| **Adminer** | UI web mínima para SQL | Ver la tabla de KPIs sin instalar nada | http://localhost:9080 |
| **Spark UI** | Panel en vivo de Spark | Ver jobs/stages mientras el pipeline corre | http://localhost:9040 (solo mientras algo corre, ver sección 4) |
| **Metabase** | Herramienta open source de dashboards (arma gráficos con clics, sin SQL) | Consume `gold_credit_risk_kpis` de Postgres — la herramienta de la Capa 6 en esta arquitectura | http://localhost:9030 — ver sección 3 |

**Por qué MinIO y no solo carpetas / por qué Postgres no guarda todo:** MinIO existe porque el Data Lake necesita volumen + formato optimizado para que Spark lea en paralelo; Postgres solo recibe el resumen ya agregado porque las herramientas de negocio hablan SQL, no Parquet/S3. Son dos trabajos distintos, no una redundancia.

**Por qué Spark y no Pandas:** la tesis exige "procesamiento distribuido" — Pandas carga todo en un solo proceso; Spark particiona y procesa en paralelo, y el mismo código escalaría de 307K filas a millones sin reescribirse (más detalle en `docs/03`, sección 1).

---

## 3. Dashboard — dónde ver el resultado

Hasta hace poco no había un lugar visual para mostrar "esto es lo que acabamos de calcular" — Adminer solo muestra tablas crudas. Ahora hay dos opciones, para distinto uso:

### Opción principal: Metabase (persistente, con clics, sin SQL)

1. Abrir http://localhost:9030 (primera vez: crear cuenta admin local + conectar a Postgres, `postgres`/`5432`/`credit_risk`, ver `docs/04-manual-usuario.md` sección 6.4).
2. `+ New → Question` → elegir tabla `gold_credit_risk_kpis` → armar el gráfico (barras, torta, tabla) arrastrando columnas — sin escribir una sola línea de SQL.
3. Guardar como *Dashboard* — queda con una URL fija que se puede reabrir en cualquier momento (a diferencia del notebook, no hay que "correrlo" cada vez).

Es la implementación de la **Capa 6 · Consumo** de esta arquitectura (`docs/03`, sección 2).

### Opción rápida: notebook con gráficos ya armados

`src/notebooks/dashboard_riesgo_crediticio.ipynb` — ya probado, corre sin errores. Útil cuando se quiere algo ya armado de antemano (histogramas de edad/ratio crédito-ingreso que Metabase no arma solo) o para no depender de configurar la conexión en Metabase en el momento:

1. Abrir http://localhost:9888 (Jupyter Lab).
2. Abrir `dashboard_riesgo_crediticio.ipynb`.
3. `Kernel → Restart Kernel and Run All Cells`.

> Nota: `src/notebooks/*.ipynb` no se versiona en git (es un artefacto de exploración local, ver `.gitignore`) — si se replica en una VM nueva, hay que volver a crear este notebook o pedirlo aparte. Metabase sí persiste (guarda sus dashboards en el volumen `metabase-data`, sobrevive a `docker compose down` sin `-v`).

---

## 4. Re-ejecutar en caliente (para una demo en vivo)

Si el profesor dice "vuelve a correrlo" o "muéstrame que funciona de nuevo", esto es lo que se hace, en orden, para que se vea el proceso — no solo el resultado final:

1. **Disparar el pipeline dentro del contenedor interactivo** (así la Spark UI queda visible durante la corrida, a diferencia de `pipeline-runner` que se ejecuta y se cierra solo):
   ```bash
   docker compose exec spark-processing python run_pipeline.py
   ```
2. **Mientras corre** (dura segundos con este dataset), abrir http://localhost:9040 — se ven los Jobs/Stages de Spark en vivo. Esto es lo que demuestra que el procesamiento es realmente distribuido, no un script secuencial.
3. **Al terminar**, la terminal muestra `Bronze OK / Silver OK / Gold OK / Pipeline completado` — es la confirmación de que las tres capas se reescribieron.
4. **Confirmar en Metabase**: solo hace falta refrescar el dashboard (botón de recarga arriba a la derecha) — como consulta la tabla en vivo, no hay que "volver a correr" nada. Si se quiere el detalle de features (histogramas de edad/ratio), volver a correr el notebook-dashboard (sección 3) regenera esos gráficos con el resultado fresco.

**Por qué no duplica ni corrompe nada al repetirlo:** cada capa escribe con `overwrite` (reemplaza, no acumula) — correr esto 10 veces seguidas da exactamente el mismo resultado. Es la idempotencia que exige `CLAUDE.md` como regla de código, y es justo lo que hace segura una demo en vivo: no hay riesgo de "romper" el estado con una repetición.

---

## 5. El recorrido de un dato, sin jerga

1. Un CSV con 307,511 solicitudes de crédito llega desde Kaggle.
2. **Bronze:** se copia tal cual a MinIO (Parquet) — es la materia prima, sin tocar.
3. **Silver:** Spark lee Bronze, limpia (nulos, tipos, duplicados), reescribe en MinIO.
4. **Gold:** Spark lee Silver, calcula columnas nuevas (edad, ratio crédito/ingreso) y agrega KPIs. Escribe el detalle en MinIO y el resumen en Postgres.
5. Postgres queda con la tabla final, lista para Metabase o el notebook-dashboard.

---

## 6. Preguntas frecuentes de defensa (respuesta corta)

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué Docker y no instalar todo directo? | Reproducibilidad — el mismo compose levanta el ecosistema idéntico en cualquier máquina |
| ¿Por qué no la nube (AWS/GCP/Azure)? | El kick-off del revisor pidió Docker/on-premise; MinIO habla el mismo protocolo que S3 real, así que migrar después no reescribe código |
| ¿Esto es "Big Data" corriendo en una laptop? | El volumen es deliberadamente manejable para demostrar la arquitectura; el patrón (Spark/MinIO) escala horizontalmente sin cambiar código |
| ¿Dónde está el dashboard? | Metabase, http://localhost:9030 (sección 3) — implementación open source de la Capa 6 |
| ¿Cómo repites la demo si te lo piden? | Sección 4 de esta guía — un comando, visible en la Spark UI, verificable en el notebook |
| ¿Dónde está el Machine Learning? | Fuera de este MVP — Gold deja los features listos; el modelado es iteración 2 (`docs/03`, sección 1) |
| ¿Por qué siempre `overwrite`? | Idempotencia — repetir el pipeline no debe duplicar datos, es requisito explícito del proyecto |

---
*Guía conceptual — complementa `docs/03-arquitectura-poc-mvp.md` (diseño técnico) y `docs/04-manual-usuario.md` (operación)*
