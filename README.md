# Proyecto: Pipeline de Datos en AWS con Snowflake

##  Descripción
Este proyecto implementa un pipeline de datos automatizado utilizando AWS y Snowflake. El objetivo es procesar archivos ZIP cargados en Amazon S3, extraer archivos CSV, transformarlos en formato Parquet y almacenarlos en Snowflake para análisis.

##  Tecnologías Utilizadas
- **AWS S3**: Almacenamiento de archivos en diferentes etapas del pipeline.
- **AWS Lambda**: Procesamiento event-driven para extracción y notificación.
- **AWS Glue**: Transformación de datos de CSV a Parquet.
- **AWS EventBridge**: Automatizacion del Workflow de Glue
- **AWS SQS**: Comunicación entre AWS y Snowflake.
- **Snowflake**: Almacenamiento de datos transformados con Snowpipe.
- **Python & Boto3**: Desarrollo de scripts en AWS Lambda.

##  Estructura del Proyecto
```
├── README.md
├── Scripts/
	├── unzip-function.py
	├── notify-sqs-on-parquet.py
	├── parquetJob.py
├── Imagenes/
	├── S3Bucket.png
	├── unzip-function.png
	├── notify-sqs-on-parquet.png
	├── parquetJob.png
	├── SQSQueue.png
	├── Snowflake.png
	├── trigger-parquet-job.png
```

##  Flujo de Trabajo
1. **Recepcion de Archivos:** Se reciben archivos ZIP a `s3://pipeline-zip-to-snowflake/landing/`.
2. **Extracción:** AWS Lambda extrae los archivos CSV y los mueve a `s3://pipeline-zip-to-snowflake/curated/`.
3. **Conversión automatica a Parquet:** Un AWS Glue Job convierte los CSV a Parquet y los guarda en `s3://pipeline-zip-to-snowflake/Published/`.
4. **Notificación a SQS:** AWS Lambda envía un mensaje a una cola SQS cuando hay nuevos archivos Parquet.
5. **Ingesta automatica en Snowflake:** Snowpipe detecta nuevos archivos y los carga en la base de datos de Snowflake.

##  Implementación
### 1️ Configuración en AWS
####   **S3 - Bucket y Estructura**
```sh
aws s3 mb s3://pipeline-zip-to-snowflake
aws s3 cp --bucket pipeline-zip-to-snowflake/landing/
aws s3 cp --bucket pipeline-zip-to-snowflake/curated/
aws s3 cp --bucket pipeline-zip-to-snowflake/Published/
```

#### **Unzip Function** (Descompresion)
- **IAM Role:** Con permisos al bucket pipeline-zip-to-snowflake.
- **Trigger:** Evento de S3 en `/landing/`.
- **Código:** Ver `unzip-function.py`

#### **Glue Job** (Conversión de CSV a Parquet)
- **Fuente:** `s3://pipeline-zip-to-snowflake/curated/`
- **Destino:** `s3://pipeline-zip-to-snowflake/Published/`
- **Código:** Ver `parquetJob.py`

#### **notify-sqs-on-parquet** (Notificacion)
- **IAM Role:** Con permisos al bucket pipeline-zip-to-snowflake y a la cola de SQS.
- **Trigger:** Evento de S3 en `/Published/`.
- **Código:** Ver `notify-sqs-on-parquet.py`

#### **SQS - Creación de Cola**
```sh
aws sqs create-queue --queue-name parquet-notifications
```

#### **Amazon EventBridge - Trigger para automatizar el Job**
- **Regla de eventbridge** La cree para que dispare el job `parquetJob` cada vez que se crea un archivo en la carpeta `/curated/`
- **Detalles** Ver en `trigger-parquet-job.img`

### 2️ Configuración en Snowflake
#### **Base de Datos y Tabla**
```sql
CREATE DATABASE SNOWFLAKE_PIPELINE;
USE DATABASE SNOWFLAKE_PIPELINE;
CREATE TABLE PUBLISHED_DATA (
    ID INT AUTOINCREMENT,
    NAME STRING,
	AGE INT
);
```

#### **Integración con AWS S3**
```sql
CREATE STORAGE INTEGRATION my_s3_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::888577034559:role/snowflake_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://pipeline-zip-to-snowflake/Published/');
```

####  **Creación de Snowpipe**
```sql
CREATE PIPE my_snowpipe
AUTO_INGEST = TRUE
AS
COPY INTO snowflake_pipeline.public.published_data
FROM @my_s3_stage
FILE_FORMAT = (TYPE = PARQUET)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

```

##  Resultados obtenidos
- Automatizacion completa del flujo de datos.
- Transformacion escalable con AWS Glue.
- Integracion fluida entre AWS y Snowflake.
- Posibilidad de realizar consultas en tiempo real sobre los datos procesados.