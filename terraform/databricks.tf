data "databricks_current_user" "me" {}

resource "databricks_secret_scope" "main" {
  name = "${var.project_name}-secrets"
}

resource "databricks_secret" "s3_bucket" {
  scope        = databricks_secret_scope.main.name
  key          = "s3_bucket"
  string_value = aws_s3_bucket.lake.id
}

resource "databricks_secret" "city" {
  scope        = databricks_secret_scope.main.name
  key          = "city"
  string_value = var.city
}