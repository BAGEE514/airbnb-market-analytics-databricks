# airbnb-market-analytics-databricks
End-to-end data pipeline using the Inside Airbnb NYC dataset. Raw CSVs land in AWS S3 (Bronze), cleaned into Delta Lake tables via Databricks + Spark (Silver), aggregated with dbt (Gold), and visualised in a Streamlit dashboard with pricing trends, neighbourhood breakdowns, and an interactive map.
