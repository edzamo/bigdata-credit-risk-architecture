# Infraestructura Docker — cómo está armado el entorno, y su seguridad
### Explica las decisiones detrás del `docker-compose.yml`, no los pasos para levantarlo
**Fecha:** 09 de septiembre de 2026
**Ref:** `src/docker-compose.yml`, `docs/03-arquitectura-poc-mvp.md` (diagramas completos), `docs/04-manual-usuario.md` (paso a paso operativo)

Tercer documento de la serie — y el que faltaba: `docs/04` explica *cómo levantarlo*, `docs/05` explica *qué hace cada pieza y para qué sirve*. Este explica **cómo está armada la infraestructura misma** (proyecto, red, volúmenes, puertos, configuración) y **qué tan segura es esa infraestructura tal como está hoy** — para poder explicárselo a un cliente o a un tribunal sin usar la palabra "Docker" como caja negra.

---

## 1. El proyecto: un solo `docker-compose.yml`

Todo el ecosistema (MinIO, PostgreSQL, Spark, Jupyter, Adminer, Metabase) se define en un único archivo, con nombre de proyecto fijo `bigdata-credit-risk` (línea 1 del compose). Eso significa: un solo comando (`docker compose up -d`) levanta o baja **todo** de forma consistente, y Docker agrupa los contenedores, la red y los volúmenes bajo ese mismo nombre — no hay piezas sueltas que se puedan desincronizar entre sí.

## 2. La red: `bigdata-net` (bridge)

Todos los servicios comparten una única red interna tipo *bridge* (`docker-compose.yml`, bloque `networks`). En términos simples: es una red privada que Docker crea solo para este proyecto, aislada del resto de contenedores que pudieran estar corriendo en la misma máquina (por eso, aunque esta VM ya tenía otros contenedores de proyectos previos — minikube, Redis, un `helloword` — nada de eso interfiere).

Dentro de esa red, cada contenedor se encuentra con los demás **por nombre de servicio**, no por IP fija: `spark-processing` le habla a `postgres` y a `minio` usando exactamente esos nombres, como si fueran hostnames de internet. Es Docker resolviendo DNS interno automáticamente. Esto es lo que rompió cuando se probó Adminer con servidor `db` en vez de `postgres` — el nombre tiene que coincidir exactamente con el nombre del servicio en el compose, no es arbitrario.

## 3. Los volúmenes: qué persiste y por qué

| Volumen | Contenedor que lo usa | Qué guarda | Por qué es un volumen (no vive dentro del contenedor) |
|---|---|---|---|
| `minio-data` | `minio` | Los archivos Parquet de bronze/silver/gold | Si el contenedor de MinIO se recrea (`docker compose down` sin `-v`, luego `up`), el Data Lake no se pierde |
| `postgres-data` | `postgres` | La tabla `gold_credit_risk_kpis` y el catálogo de Postgres | Igual — recrear el contenedor no borra los KPIs calculados |
| `metabase-data` | `metabase` | Los dashboards armados, la cuenta de admin, la conexión guardada a Postgres | Sin esto, cada `docker compose down/up` obligaría a rehacer el setup de Metabase desde cero |

Los contenedores en sí son **desechables** — se pueden borrar y recrear en segundos porque no guardan nada importante en su propio sistema de archivos; todo lo que importa vive en estos tres volúmenes. `docker compose down -v` es la única forma de perder estos datos (lo borra a propósito, es el "reinicio completo" que ya documenta `docs/04` sección 7).

## 4. Puertos: filosofía, no el detalle completo

El detalle puerto por puerto ya está en `docs/03-arquitectura-poc-mvp.md` (sección 3, con diagrama). Acá solo la regla: **todo lo expuesto al host usa el rango 90xx**, específicamente para evitar el puerto 8080 (choca con Tomcat/proxies comunes) — fue un requisito explícito para que esto se pueda replicar en cualquier máquina sin pelearse con puertos ya ocupados por otras cosas.

## 5. Configuración y secretos: todo sale de `.env`, nada se commitea

Ningún usuario, contraseña o endpoint está escrito directamente en `docker-compose.yml` — todo se lee de variables de entorno (`${POSTGRES_PASSWORD:-bigdata_password_change_me}`, por ejemplo), con un valor por defecto solo para que la PoC funcione sin configuración adicional. El archivo real (`.env`) se arma copiando `.env.example` (que sí está versionado, pero solo con placeholders — ninguno es una credencial real) y **nunca se sube al repo**: está en `.gitignore` desde el primer commit.

Verifiqué el historial completo de git de este repositorio (no solo el estado actual) y confirmo: nunca se commiteó un `.env`, y el token de Kaggle que usamos tampoco quedó en ningún commit — se guardó siempre fuera del repo, en `~/.kaggle/`.

## 6. Seguridad — revisión honesta de cómo está hoy

Esto es lo que pediste revisar. Ni es todo perfecto, ni es un desastre — es exactamente lo esperable de una PoC de tesis en una VM local, con límites claros para cuando esto deje de ser una demo.

**Verificado y correcto:**
- `.env` real nunca versionado, ni en el estado actual ni en el historial completo.
- Contraseñas por defecto marcadas explícitamente `..._change_me` — obligan a decidir, no dan una falsa sensación de que ya están "listas para producción".
- La red bridge aísla el tráfico entre contenedores del resto del host.
- Esta VM tiene IP privada (`192.168.64.x`, sin metadata de nube) — no está expuesta a internet tal como está.

**Limitaciones conocidas, a tener presente si esto se comparte o se despliega más allá de esta VM:**

| Punto | Situación actual | Por qué importa | Qué hacer si se expone más allá de esta VM |
|---|---|---|---|
| Puertos bindeados a `0.0.0.0` | Todos los servicios escuchan en todas las interfaces de red, no solo `localhost` | Hoy no es explotable (red privada, sin salida a internet), pero si esta VM alguna vez tiene IP pública o hay port-forwarding, cualquiera en esa red llega directo a estos servicios | Restringir con firewall (`ufw`) por IP de origen, o cambiar a `127.0.0.1:9080:8080` en el compose para lo que no necesite acceso externo |
| **Jupyter sin token ni contraseña** | `--NotebookApp.token='' --NotebookApp.password=''` — cualquiera que llegue al puerto 9888 tiene ejecución de código Python completa dentro del contenedor | Es, en la práctica, ejecución remota de código sin autenticación — aceptable solo en un entorno de desarrollo local y aislado como este | Activar un token (`jupyter lab --IdentityProvider.token=<valor>`) antes de exponerlo a cualquier red compartida |
| Adminer y Postgres expuestos directo | Puerto 9080 (Adminer, UI completa de administración de BD) y 9432 (Postgres directo) alcanzables desde cualquiera en la red de la VM | Adminer es una herramienta con historial de ser blanco de escaneos automatizados cuando queda pública | Mismo tratamiento: firewall o bind a `127.0.0.1` |
| Metabase, primera visita = admin | La primera persona que entra a `/setup` en el puerto 9030 se vuelve administrador de la instancia | Ventana de carrera si dos personas prueban al mismo tiempo, o si queda expuesto antes de completar el setup | Completar el setup de Metabase apenas se levanta el contenedor, no dejarlo pendiente |
| Sin TLS en ningún servicio | Todo el tráfico (MinIO, Postgres, Metabase, Adminer, Jupyter) va sin cifrar | Aceptable dentro de una sola máquina/red privada; no aceptable si el tráfico cruza redes | Un reverse proxy (nginx/Traefik) con TLS delante de todo, si esto pasa a ser multi-máquina |

**Lo que esta arquitectura explícitamente no es:** un despliegue de producción para un banco real. Es una PoC de un solo host, sin alta disponibilidad, sin backups automatizados, sin rotación de credenciales, sin auditoría de accesos. Vale la pena decirlo así de claro en la defensa — el objetivo del hito era demostrar la arquitectura medallón funcionando end-to-end en Docker, no endurecer un sistema para producción; eso queda como trabajo futuro documentado, no como un hueco que se esconde.

---
*Guía de infraestructura — complementa `docs/03-arquitectura-poc-mvp.md` (diseño técnico), `docs/04-manual-usuario.md` (operación) y `docs/05-guia-componentes-defensa.md` (conceptual)*
