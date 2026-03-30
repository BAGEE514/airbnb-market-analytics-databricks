# Databricks notebook source
import boto3
import pandas as pd
import gzip
from io import BytesIO
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, DateType, LongType

AWS_ACCESS_KEY = "*************" #Changed so access key is not shown
AWS_SECRET_KEY =  "*************" #Changed so access key is not shown
S3_BUCKET = dbutils.secrets.get(scope='airbnb-analytics-secrets', key='s3_bucket')
CITY = 'london'

s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name='us-east-1'
)

# Read gzipped CSV from S3
obj = s3.get_object(Bucket=S3_BUCKET, Key=f'bronze/{CITY}/listings/listings.csv.gz')
with gzip.GzipFile(fileobj=BytesIO(obj['Body'].read())) as f:
    df_pandas = pd.read_csv(f, low_memory=False)

print(f'Raw rows loaded: {len(df_pandas):,}')
print('Price sample:', df_pandas['price'].head(5).tolist())

# Clean price - remove $ and commas then convert to number
df_pandas['price'] = df_pandas['price'].astype(str).str.replace('[$,]', '', regex=True)
df_pandas['price'] = pd.to_numeric(df_pandas['price'], errors='coerce')
df_pandas = df_pandas[df_pandas['price'].notna() & (df_pandas['price'] > 0)]
print(f'Rows after price cleaning: {len(df_pandas):,}')

# Convert to Spark
df_raw = spark.createDataFrame(df_pandas.astype(str))

df_silver = (df_raw.select(
    F.col('id').cast(LongType()).alias('listing_id'),
    'name', 'host_id', 'host_name',
    F.col('neighbourhood_group_cleansed').alias('neighbourhood_group'),
    F.col('neighbourhood_cleansed').alias('neighbourhood'),
    F.col('latitude').cast(DoubleType()),
    F.col('longitude').cast(DoubleType()),
    'room_type',
    F.col('price').cast(DoubleType()).alias('price_usd'),
    F.col('minimum_nights').cast(IntegerType()),
    F.col('number_of_reviews').cast(IntegerType()),
    F.when(F.col('last_review') == 'nan', None)
     .otherwise(F.col('last_review'))
     .cast(DateType()).alias('last_review'),
    F.col('reviews_per_month').cast(DoubleType()),
    F.col('calculated_host_listings_count').cast(IntegerType()),
    F.col('availability_365').cast(IntegerType()),
)
.filter(F.col('price_usd').isNotNull() & (F.col('price_usd') > 0))
.filter(F.col('latitude').isNotNull())
.withColumn('price_bracket',
    F.when(F.col('price_usd') <  75,  'Budget (< $75)')
    .when(F.col('price_usd') < 150,   'Mid-range ($75-$150)')
    .when(F.col('price_usd') < 300,   'Premium ($150-$300)')
    .otherwise('Luxury ($300+)')
)
.withColumn('host_type',
    F.when(F.col('calculated_host_listings_count') == 1, 'Single listing')
    .when(F.col('calculated_host_listings_count') <= 3,  'Small host (2-3)')
    .otherwise('Multi-listing host (4+)')
)
)

spark.sql("CREATE DATABASE IF NOT EXISTS airbnb_silver")

(df_silver.write
    .format('delta')
    .mode('overwrite')
    .option('overwriteSchema', 'true')
    .partitionBy('neighbourhood_group', 'room_type')
    .saveAsTable('airbnb_silver.listings')
)

count = spark.table('airbnb_silver.listings').count()
print(f'Silver listings ready: {count:,} rows')
