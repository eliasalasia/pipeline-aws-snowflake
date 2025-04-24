import boto3
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

#inicializo glue y spark
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

#defino las rutas del bucket
bucket_name = "pipeline-zip-to-snowflake"
s3_input_path = f"s3://{bucket_name}/curated/"
s3_output_path = f"s3://{bucket_name}/Published/"

#se cargan los csv de 'curated' a 'published'
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(s3_input_path)

#se procesan los datos (se formatean en minúsculas y sin espacios)
df = df.toDF(*[col.lower().replace(" ", "_") for col in df.columns])

#lo guardo como Parquet en 'Published'
df.write.mode("overwrite").parquet(s3_output_path)

print(f"Archivos Parquet guardados en {s3_output_path}")