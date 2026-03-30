# Databricks notebook source
import boto3
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, IntegerType, DateType

# AWS credentials
AWS_ACCESS_KEY = "*************" #Changed so access key is not shown
AWS_SECRET_KEY =  "*************" #Changed so access key is not shown

S3_BUCKET = dbutils.secrets.get(scope='airbnb-analytics-secrets', key='s3_bucket')
CITY = 'london'

# using boto3
s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name='us-east-1'
)

import gzip
from io import BytesIO

obj = s3.get_object(Bucket=S3_BUCKET, Key=f'bronze/{CITY}/reviews/reviews.csv.gz')
with gzip.GzipFile(fileobj=BytesIO(obj['Body'].read())) as f:
    df_pandas = pd.read_csv(f, low_memory=False)
print(f'Raw rows loaded: {len(df_pandas):,}')

# Spark DataFrame
df_raw = spark.createDataFrame(df_pandas.astype(str))

# Clean columns
df_silver = (df_raw.select(
    F.col('listing_id').cast(LongType()),
    F.col('id').cast(LongType()).alias('review_id'),
    # Handle 'nan' values 
    F.when(F.col('date') == 'nan', None)
     .otherwise(F.col('date'))
     .cast(DateType()).alias('review_date'),
    F.col('reviewer_id').cast(LongType()),
    'reviewer_name',
)
.filter(F.col('review_date').isNotNull())
.withColumn('review_year',    F.year('review_date'))
.withColumn('review_month',   F.month('review_date'))
.withColumn('review_quarter', F.quarter('review_date'))
.withColumn('month_start',    F.date_trunc('month', F.col('review_date')))
)

print(f'Clean rows after filtering: {df_silver.count():,}')

# Create database
spark.sql("CREATE DATABASE IF NOT EXISTS airbnb_silver")

(df_silver.write
    .format('delta')
    .mode('overwrite')
    .option('overwriteSchema', 'true')
    .partitionBy('review_year')
    .saveAsTable('airbnb_silver.reviews')
)

count = spark.table('airbnb_silver.reviews').count()
print(f'Silver reviews ready: {count:,} rows')