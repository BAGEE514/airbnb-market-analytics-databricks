variable "aws_region"   { default = "us-east-1" }
variable "project_name" { default = "airbnb-analytics" }
variable "city" {
  description = "City slug used to organise S3 paths"
  default     = "london"
}
variable "databricks_host" {
  description = "Workspace URL e.g. https://abc123.cloud.databricks.com"
}
variable "databricks_token" {
  description = "Databricks personal access token"
  sensitive   = true
}