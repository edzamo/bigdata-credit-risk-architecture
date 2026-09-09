# Alcance técnico — Arquitectura Big Data para Riesgo Crediticio
### Nota de entendimiento — consultoría de implementación
**Fecha:** 08 de septiembre de 2026
**Fuentes revisadas:** `kick-off-project.md`, `Plantilla de Proyecto de IEEE APR.docx`

---

## 1. De qué trata la tesis

Trabajo de titulación (Universidad Tecnológica Israel — UISRAEL) orientado a **diseñar e implementar una Arquitectura Big Data** que integre, almacene, procese y analice información relacionada con la **evolución del riesgo crediticio** en entidades financieras, para optimizar las decisiones de concesión de créditos.

**Pregunta de investigación:** ¿Cómo contribuir al análisis de la evolución del riesgo en entidades financieras mediante el diseño e implementación de una Arquitectura Big Data que integre y procese información financiera relevante para optimizar las decisiones de concesión de créditos?

**Objetivo general:** Diseñar e implementar una Arquitectura Big Data para la integración, almacenamiento, procesamiento y análisis de información relacionada con la evolución del riesgo en entidades financieras, mediante tecnologías de procesamiento distribuido y analítica avanzada.

**Objetivos específicos:**
1. Contextualizar los fundamentos teóricos, metodológicos y tecnológicos (Big Data, arquitectura de datos, riesgo financiero, analítica avanzada).
2. Determinar fuentes de información, características y requisitos de integración/procesamiento.
3. Diseñar e implementar la Arquitectura Big Data (integración, almacenamiento, procesamiento, análisis).
4. Validar la arquitectura mediante indicadores de calidad de datos, rendimiento, escalabilidad y soporte a la toma de decisiones.

**Metodología de investigación:** cuantitativa, aplicada y de desarrollo tecnológico; alcance exploratorio-descriptivo-correlacional-explicativo; diseño no experimental y longitudinal retrospectivo. **Metodología de desarrollo: CRISP-DM** (comprensión del negocio → comprensión de datos → preparación/integración → diseño e implementación de la arquitectura → modelado → evaluación → despliegue).

Nota importante: la parte metodológica/narrativa del documento (capítulos, redacción académica, marco teórico) **ya está siendo trabajada por el equipo del estudiante** — no es parte de nuestro alcance (ver sección 3).

---

## 2. Fuentes de datos previstas

| Dominio | Fuente |
|---|---|
| Crediticio | Home Credit Default Risk (Kaggle — tabla principal: 215,257 filas × 102 columnas + 3 tablas relacionadas de igual tamaño) |
| Macroeconómico | World Bank Open Data, IMF Data, FRED |
| Financiero global | Yahoo Finance, Nasdaq Data Link, Bank for International Settlements (BIS) |
| Mercado / commodities | Energy Information Administration (EIA) — petróleo WTI y Brent, riesgo país, tasas de interés, inflación |

Variable objetivo del dataset principal: `TARGET` (1 = impago, 0 = pago correcto).

---

## 3. Arquitectura ya definida en el documento (Capítulo II — Propuesta)

El documento **ya especifica una arquitectura de 6 capas**, con herramientas puntuales. Esto es lo que tenemos que construir — no hay que diseñarla desde cero, hay que **implementarla**:

| # | Capa | Herramientas ya definidas en el documento |
|---|---|---|
| 1 | Fuentes de datos | Home Credit Default Risk, World Bank, IMF, FRED, Yahoo Finance, Nasdaq Data Link, BIS |
| 2 | Ingesta | Python, APIs REST, procesos ETL |
| 3 | Data Lake (medallón) | Bronze (datos originales) → Silver (depurados) → Gold (enriquecidos), formato **Parquet** |
| 4 | Procesamiento distribuido | **Apache Spark / PySpark** — limpieza, transformación, integración, feature engineering |
| 5 | Analítica | Análisis descriptivo, correlaciones, indicadores; ML con **Random Forest, XGBoost** |
| 6 | Consumo | **Power BI** — dashboard ejecutivo, dashboard de riesgo, KPIs financieros |

Stack adicional mencionado en el documento: PostgreSQL (almacenamiento estructurado), Pandas/NumPy, Scikit-learn, Matplotlib/Seaborn.

## 4. ¿Está definida la nube (AWS / GCP / Azure)?

**No.** En ningún punto del documento se menciona un proveedor cloud. Todas las herramientas listadas (Spark, PostgreSQL, Parquet, Power BI) son **agnósticas de nube** y funcionan igual on-premise (Docker) que en cualquier proveedor. Es decir, el documento describe el **qué** (capas y herramientas) pero no el **dónde** (infraestructura de despliegue) — esa decisión sigue abierta.

Esto se refuerza con el mensaje de kick-off del revisor/tutor:

> *"para el siguiente avance me indica que requiero tener arquitectura herramientas en el Docker y el Docker funcionando, arquitectura medallón hasta la parte gold"*

Esto apunta directamente a una implementación **on-premise con Docker** (mismo patrón que `project-bigdata-01`), al menos como próximo hito exigido. No se ha planteado explícitamente una alternativa cloud para este proyecto — a diferencia del proyecto 01, aquí no hace falta un memo de decisión cloud-vs-on-premise salvo que el cliente lo pida; el camino ya está insinuado por el revisor.

---

## 5. Alcance de nuestra consultoría en este proyecto

Según lo indicado por el cliente: **nuestro trabajo se limita a la implementación técnica / desarrollo** de la arquitectura ya descrita en el Capítulo II. No cubrimos:
- Redacción de capítulos, marco teórico, discusión, conclusiones (responsabilidad del estudiante/parte metodológica).
- Definición de objetivos o metodología de investigación (ya aprobados).

Sí cubrimos:
- Levantar el entorno Docker con las herramientas de cada capa.
- Construir el Data Lake con arquitectura medallón (Bronze → Silver → Gold) en Parquet.
- Implementar la ingesta (Python/APIs/ETL) desde las fuentes listadas.
- Implementar el procesamiento distribuido con Spark/PySpark.
- Dejar la capa analítica lista para los modelos (Random Forest, XGBoost) e indicadores.
- Dejar la capa de consumo conectada a Power BI.

## 6. Próximo hito (según kick-off)

El revisor pidió como siguiente avance:
- [ ] Arquitectura de herramientas corriendo en Docker.
- [ ] Docker funcionando (contenedores levantados).
- [ ] Arquitectura medallón implementada **hasta la capa Gold** (Bronze → Silver → Gold funcionando end-to-end, aunque sea con el dataset Home Credit Default Risk como primer caso).

## 7. Preguntas abiertas para el cliente

1. ¿Confirma que la implementación va **on-premise con Docker** (no cloud) para este proyecto, tal como sugiere el mensaje del revisor?
2. ¿El equipo local dispone de los recursos (RAM/CPU) para correr Spark + PostgreSQL + Power BI (o su equivalente gratuito, ya que Power BI Desktop es gratuito pero requiere Windows) en contenedores?
3. ¿Hay ya credenciales/acceso a las APIs de las fuentes macroeconómicas (World Bank, IMF, FRED, Nasdaq Data Link, BIS, EIA), o eso también es parte de nuestro alcance?
