# Manual de usuario — levantar y probar la PoC en una VM Linux
### Guía paso a paso para replicar el entorno y verificar cada servicio
**Fecha:** 09 de septiembre de 2026
**Ref:** `docs/03-arquitectura-poc-mvp.md` (arquitectura, red y puertos), `src/docker-compose.yml`

Este manual asume una VM limpia con **Ubuntu 22.04 LTS** (o similar), mínimo **10 GB RAM / 4 vCPU / 20 GB disco** (subió de 8 a 10 GB al agregar Metabase como dashboard, ver `docs/03` sección 6), sin conflictos previos de permisos (el problema de TCC de macOS que tuvimos en el Mac de desarrollo no existe en Linux).

Funciona tanto en VMs **amd64** como **arm64** (todas las imágenes del compose son multi-arquitectura); la imagen de `spark-processing` detecta el JDK correcto en build vía symlink, sin pasos manuales adicionales.

> 💡 Los pasos de instalación genéricos (Docker, `git`, `pipx`, manejo básico de terminal) son estándar de la industria, no algo propio de este proyecto — si algo no queda claro o da un error no cubierto aquí, se puede pedir ayuda a cualquier asistente de IA gratuito (ChatGPT, Gemini, Copilot, etc.) pegando el mensaje de error. Los pasos específicos de este proyecto (variables de entorno, rutas, nombres de buckets/tablas) sí están documentados paso a paso en este manual y no se deben improvisar.

---

## 1. Requisitos previos en la VM

```bash
# Docker Engine + Docker Compose plugin (Ubuntu/Debian)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker   # o cierra sesión y vuelve a entrar

# Verificar
docker --version
docker compose version
```

---

## 2. Clonar el repositorio

```bash
git clone -b feature/mvp-v01 https://github.com/edzamo/bigdata-credit-risk-architecture.git
cd bigdata-credit-risk-architecture/src
```

## 3. Descargar el dataset (paso manual obligatorio)

Kaggle exige autenticación, así que este paso no se puede automatizar dentro del compose. El cliente actual de Kaggle usa un **token de API único** (formato `KGAT_...`), ya no el `kaggle.json` de versiones anteriores; el token nunca va dentro del repo, se guarda en el home del usuario en la VM.

1. Generar el token en [kaggle.com/settings](https://www.kaggle.com/settings) → "Create New Token".
2. Instalar el cliente `kaggle`. En Ubuntu 24.04 `pip install` a nivel de sistema está bloqueado (PEP 668), así que se instala con `pipx`:
   ```bash
   sudo apt install -y pipx
   pipx install kaggle
   pipx ensurepath && source ~/.bashrc   # o abre una terminal nueva para que el PATH tome efecto
   ```
3. Guardar el token fuera del repo (el cliente lo lee automáticamente de esa ruta):
   ```bash
   mkdir -p ~/.kaggle && chmod 700 ~/.kaggle
   echo "KGAT_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > ~/.kaggle/access_token   # tu token real
   chmod 600 ~/.kaggle/access_token
   ```
   Alternativa sin dejarlo en disco: `export KAGGLE_API_TOKEN=KGAT_xxx...` en la sesión de shell.
4. Verificar que el token funciona:
   ```bash
   kaggle competitions list
   ```
5. **Unirse a la competencia desde el navegador (obligatorio, no se puede saltar por API, y lo debe hacer el dueño de la cuenta en persona).** `home-credit-default-risk` es una *competencia* de Kaggle, no un dataset suelto: aunque el token sea válido, la API responde `403 Forbidden` en la descarga hasta que la cuenta haya aceptado las reglas manualmente.
   1. Entrar a [kaggle.com/competitions/home-credit-default-risk/rules](https://www.kaggle.com/competitions/home-credit-default-risk/rules) con la cuenta logueada.
   2. Click en **"I Understand and Accept"** / **"Join Competition"**.
   3. ⚠️ Si la cuenta no tiene el teléfono verificado, Kaggle va a pedir en ese momento verificación por SMS y, en algunos casos, **subir una foto de un documento de identidad desde el celular**. Es un paso de Kaggle, no del proyecto — hay que tener el celular a mano antes de intentar este paso, y puede tardar unos minutos en aprobarse.
   4. ⚠️ **Este paso no se puede delegar ni compartir.** La verificación de identidad (SMS + documento) queda ligada a la persona dueña de la cuenta de Kaggle — compartir esas credenciales o pedirle a alguien más (incluida una IA) que la complete a nombre de otro viola los Términos de Servicio de Kaggle e involucra datos personales/documentos de identidad, con implicaciones legales. Cada persona que replique este entorno debe usar su propia cuenta de Kaggle y aceptar las reglas ella misma.
6. Descargar el dataset:
   ```bash
   kaggle competitions download -c home-credit-default-risk -f application_train.csv -p data/raw/
   ```
   Si da `403 Forbidden`, es porque el paso 5 no terminó de aprobarse todavía — reintentar después de confirmar que la página de reglas ya muestra "Joined".
7. Descomprimir y confirmar que quedó en la ruta esperada:
   ```bash
   unzip -o data/raw/application_train.csv.zip -d data/raw/
   rm data/raw/application_train.csv.zip
   ls -la data/raw/application_train.csv
   ```

## 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Con los valores por defecto alcanza para la PoC. Solo edita `.env` si la VM tiene menos de 8 GB de RAM disponibles para Docker (bajar `SPARK_LOCAL_CORES` a `1` y `SPARK_DRIVER_MEMORY` a `1g`).

## 5. Levantar todo con un solo comando

```bash
docker compose up -d
```

Esto: construye la imagen de Spark/Jupyter (jars de S3A y JDBC incluidos), levanta MinIO y PostgreSQL, crea los buckets `bronze/silver/gold` (`minio-init`), y corre automáticamente el pipeline Bronze→Silver→Gold (`pipeline-runner`) apenas la infraestructura está lista.

La primera vez tarda varios minutos (build de la imagen + descarga de jars). Corridas posteriores son casi inmediatas (todo queda cacheado).

---

## 6. Verificación paso a paso, servicio por servicio

### 6.1 Contenedores levantados

```bash
docker compose ps
```

Esperado — todos `running (healthy)` salvo los que terminan solos:

| Servicio | Estado esperado |
|---|---|
| `minio` | `running (healthy)` |
| `postgres` | `running (healthy)` |
| `adminer` | `running` |
| `metabase` | `running` (tarda ~30-60s en quedar listo la primera vez, ver 6.2b) |
| `spark-processing` | `running` (queda en espera, es el contenedor interactivo) |
| `jupyter` | `running` |
| `minio-init` | `exited (0)` — es normal, es un job de una sola corrida (crea los buckets) |
| `pipeline-runner` | `exited (0)` — es normal, corre el pipeline una vez y termina |

Si `pipeline-runner` sale con código distinto de 0, revisa sus logs (sección 6.5) — lo más común es que falte `data/raw/application_train.csv` (paso 3).

### 6.2 MinIO (Data Lake) — buckets y archivos Parquet

1. Abrir http://localhost:9001 (o `http://<ip-vm>:9001` si es remota).
2. Login con `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` de tu `.env`.
3. Deben existir 3 buckets: `bronze`, `silver`, `gold`.
4. Entrar a cada uno y confirmar que hay archivos `.parquet` bajo `home_credit/application` (Bronze y Silver) y `home_credit/credit_risk_features` (Gold).

Verificación rápida por consola, sin abrir el navegador:

```bash
docker compose exec spark-processing bash -c "
python - <<'PY'
from common.session import get_spark_session
spark = get_spark_session()
for bucket, path in [('bronze','home_credit/application'), ('silver','home_credit/application'), ('gold','home_credit/credit_risk_features')]:
    df = spark.read.parquet(f's3a://{bucket}/{path}')
    print(f'{bucket}: {df.count()} filas, {len(df.columns)} columnas')
PY
"
```

### 6.3 PostgreSQL (KPIs de Gold)

Por Adminer (http://localhost:9080): Sistema `PostgreSQL`, servidor `postgres`, usuario/clave/DB de tu `.env`. Buscar la tabla `gold_credit_risk_kpis`.

Por consola:

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT * FROM gold_credit_risk_kpis ORDER BY tasa_default_pct DESC;"
```

Debe devolver una fila por cada valor de `NAME_INCOME_TYPE`, con `total_clientes`, `clientes_en_default`, `tasa_default_pct`, `credito_promedio` y `ratio_credito_ingreso_promedio`.

### 6.4 Metabase (dashboard, Capa 6 · Consumo)

1. Abrir http://localhost:9030 — la primera vez tarda ~30-60s en quedar listo (arranca su base interna); si da error de conexión, esperar y refrescar.
2. Crear la cuenta de administrador local (solo la primera vez, queda guardada en el volumen `metabase-data`).
3. Al pedir la fuente de datos, agregar: Motor `PostgreSQL`, Host `postgres`, Puerto `5432`, Base de datos `credit_risk`, usuario/clave de tu `.env` (mismos datos que en Adminer, sección 6.3 — el host es `postgres`, no `db` ni `localhost`).
4. Una vez conectado, Metabase detecta sola la tabla `gold_credit_risk_kpis` — desde ahí se arman gráficos con clics (`+ New → Question`), sin escribir SQL.

Es la herramienta de dashboard de la Capa 6 · Consumo de esta arquitectura — open source, corre dentro del mismo Docker que todo lo demás (ver `docs/03` sección 1 y `docs/05-guia-componentes-defensa.md`).

### 6.5 Spark UI

Abrir http://localhost:9040 mientras el pipeline corre (o inmediatamente después de un `docker compose exec spark-processing python run_pipeline.py` manual) — muestra los jobs/stages de Spark. Si `pipeline-runner` ya terminó, esta UI puede no tener nada que mostrar (es normal, el contenedor de esa corrida ya no existe); usa `spark-processing` para correr el pipeline de nuevo manualmente si quieres verlo en vivo (ver 6.8).

### 6.6 Logs de cada servicio

```bash
docker compose logs minio-init          # debe terminar con "Buckets bronze/silver/gold listos"
docker compose logs pipeline-runner     # debe terminar con "Pipeline Bronze -> Silver -> Gold completado."
docker compose logs -f jupyter          # -f para seguir en vivo si algo no arranca
```

### 6.7 Jupyter Lab (exploración manual)

Abrir http://localhost:9888 (sin token, ya configurado). Desde una notebook nueva:

```python
from common.session import get_spark_session
spark = get_spark_session()
spark.read.parquet("s3a://gold/home_credit/credit_risk_features").show(5)
```

O abrir directamente `notebooks/dashboard_riesgo_crediticio.ipynb` (ya armado con gráficos, ver `docs/05-guia-componentes-defensa.md` sección 3).

### 6.8 Re-ejecutar el pipeline manualmente (opcional)

Útil para volver a correrlo tras cambiar código, sin reiniciar todo el compose:

```bash
docker compose run --rm pipeline-runner
```

Al ser idempotente (todas las escrituras son `overwrite`), correrlo varias veces no duplica datos — es seguro repetirlo. Para verlo en la Spark UI mientras corre (sección 6.5), usar en cambio `docker compose exec spark-processing python run_pipeline.py`.

### 6.9 Correr las pruebas unitarias

```bash
docker compose run --rm --no-deps spark-processing pytest -v
```

Deben pasar todas sin necesidad de que MinIO/PostgreSQL estén levantados (las pruebas usan una SparkSession local en memoria, sin tocar infraestructura real).

---

## 7. Apagar todo

```bash
docker compose down          # detiene y borra los contenedores, conserva los volúmenes (datos)
docker compose down -v       # además borra los volúmenes (reinicio completo desde cero)
```

---

## 8. Problemas conocidos y su causa

| Síntoma | Causa | Solución |
|---|---|---|
| `pipeline-runner` sale con código 1 y el log dice "No se encontró el dataset" | Falta `data/raw/application_train.csv` | Repetir el paso 3 |
| `docker compose up` tarda mucho la primera vez | Build de la imagen (PySpark ~300MB + jars de Hadoop/AWS/Postgres) | Normal, solo pasa una vez; corridas siguientes usan caché |
| Puertos ocupados (`address already in use`) | Otro servicio local ya usa 9000/9001/9040/9080/9432/9888 | Cambiar el puerto de host en `docker-compose.yml` (nunca usar 8080, ver `docs/03`) |
| En macOS: `Operation not permitted` al leer archivos montados | Permiso de Files & Folders / Full Disk Access de macOS no otorgado a Docker Desktop, o carpeta no incluida en Docker Desktop → Settings → Resources → File Sharing | No aplica en Linux; en macOS revisar ambos lugares y reiniciar Docker Desktop por completo |
| `kaggle competitions download` da `403 Forbidden` aunque el token sea válido | La cuenta no aceptó las reglas de la competencia `home-credit-default-risk` (paso 5 de la sección 3) — Kaggle lo exige por navegador, no hay forma de hacerlo por API | Aceptar las reglas en [kaggle.com/competitions/home-credit-default-risk/rules](https://www.kaggle.com/competitions/home-credit-default-risk/rules); si la cuenta no tiene teléfono verificado, Kaggle pide SMS y a veces foto de un documento de identidad — tener el celular a mano |

---
*Manual de verificación — PoC/MVP dockerizada · Complementa `docs/03-arquitectura-poc-mvp.md`*
