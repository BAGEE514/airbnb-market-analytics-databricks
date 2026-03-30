.PHONY: infra transform test dashboard all

infra:
	cd terraform && terraform apply \
	  -var="databricks_host=$(DATABRICKS_HOST)" \
	  -var="databricks_token=$(DATABRICKS_TOKEN)"

transform:
	cd dbt && dbt run --project-dir airbnb_analytics --full-refresh

test:
	cd dbt && dbt test --project-dir airbnb_analytics

dashboard:
	cd dashboard && py -3.11 -m streamlit run app.py

all: transform test dashboard