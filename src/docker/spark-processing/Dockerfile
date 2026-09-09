FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/lib/jvm/java-17-openjdk-* /usr/lib/jvm/java-17-openjdk

# Symlink agnóstico de arquitectura arriba: la ruta real del JDK depende de si la imagen se
# construye en amd64 o arm64 (p.ej. VM Linux en ARM), y el nombre del paquete difiere en cada caso.
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Jars que la SparkSession (common/session.py) necesita para leer/escribir en MinIO (S3A) y
# PostgreSQL (JDBC). Se descargan en el build para no depender de Maven Central en tiempo de
# ejecución (spark.jars.packages sería más lento y frágil en redes restringidas).
RUN mkdir -p /opt/spark-jars && \
    curl -fsSL -o /opt/spark-jars/hadoop-aws-3.3.4.jar \
        https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -fsSL -o /opt/spark-jars/aws-java-sdk-bundle-1.12.262.jar \
        https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    curl -fsSL -o /opt/spark-jars/postgresql-42.7.3.jar \
        https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fuera de /opt/app a propósito: docker-compose.yml monta el host ahí encima (bind mount para
# desarrollo en caliente), lo que ocultaría cualquier archivo horneado dentro de esa ruta.
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONPATH=/opt/app

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
