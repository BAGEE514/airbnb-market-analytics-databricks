resource "random_id" "suffix" { byte_length = 4 }

resource "aws_s3_bucket" "lake" {
  bucket = "${var.project_name}-lake-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "lake" {
  bucket                  = aws_s3_bucket.lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "bronze_listings" {
  bucket  = aws_s3_bucket.lake.id
  key     = "bronze/${var.city}/listings/"
  content = ""
}

resource "aws_s3_object" "bronze_reviews" {
  bucket  = aws_s3_bucket.lake.id
  key     = "bronze/${var.city}/reviews/"
  content = ""
}

resource "aws_s3_object" "silver" {
  bucket  = aws_s3_bucket.lake.id
  key     = "silver/"
  content = ""
}

resource "aws_s3_object" "gold" {
  bucket  = aws_s3_bucket.lake.id
  key     = "gold/"
  content = ""
}