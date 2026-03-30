# 🏠 Airbnb Market Analytics Dashboard

End-to-end data pipeline using the Inside Airbnb London dataset.

## Problem Description
Understanding London's Airbnb market requires analysing thousands of listings 
across neighbourhoods, room types, price ranges, and seasons. This project 
builds an automated pipeline that processes Inside Airbnb data using the 
Medallion Architecture on Databricks, transforms it with dbt, and presents 
insights in a Streamlit dashboard.

Key questions answered:
- Which London neighbourhoods have the most listings and highest prices?
- How has Airbnb activity changed over time month by month?
- What is the price distribution across room types?
- Where are the best-value listings geographically?

## Architecture
```
Inside Airbnb CSV → AWS S3 (Bronze)
                  → Databricks Spark Notebooks → Delta Lake (Silver, partitioned)
                  → Databricks Workflows (monthly schedule)
                  → dbt models → Gold mart tables
                  → Streamlit Dashboard
```

## Tech Stack
| Component | Tool |
|---|---|
| Cloud | AWS S3 |
| IaC | Terraform |
| Compute | Databricks + Apache Spark |
| Orchestration | Databricks Workflows |
| Data Lake | Delta Lake on S3 |
| Transformations | dbt-databricks |
| Dashboard | Streamlit + Plotly + Folium |
| Tests | dbt tests |
| CI/CD | GitHub Actions |

## Partitioning Strategy
Silver listings table is partitioned by `neighbourhood` and `room_type`.
Silver reviews table is partitioned by `review_year`.
Dashboard queries always filter on these columns so Databricks uses partition 
pruning to skip irrelevant S3 folders, making queries significantly faster.

## Dashboard
![Dashboard](./assets/dashboard.png)

## How to Reproduce
1. Clone this repo
2. Create Databricks free trial + AWS free tier accounts
3. Download London dataset from insideairbnb.com/get-the-data
4. `cd terraform && terraform apply`
5. Upload CSVs to S3: `aws s3 cp listings.csv.gz s3://BUCKET/bronze/london/listings/`
6. Upload notebooks to Databricks Workspace and run the Workflow
7. `cd dbt/airbnb_analytics && dbt run && dbt test`
8. `cd dashboard && py -3.11 -m streamlit run app.py`

## Dataset
Inside Airbnb — insideairbnb.com/get-the-data (public domain)
City: London, England | Pipeline type: Batch (monthly)
