terraform {
  required_version = "~> 0.12.9"
}

provider "aws" {
  region  = "sa-east-1"
  version = "2.51"
}

resource "aws_s3_bucket" "public" {
  bucket = "fts-public-packages"
  policy = <<POLICY
{
      "Version": "2012-10-17",
      "Statement": [
          {
              "Sid": "AddPerm",
              "Effect": "Allow",
              "Principal": "*",
              "Action": [
                  "s3:GetObject"
              ],
              "Resource": [
                  "arn:aws:s3:::fts-public-packages/*"
              ]
          }
      ]
}
POLICY
}

resource "aws_s3_bucket_public_access_block" "public" {
  bucket = aws_s3_bucket.public.id
  block_public_acls   = false
  block_public_policy = false
}

output "bucket_url" {
  value = split(".", aws_s3_bucket.public.bucket_regional_domain_name)[0]
}
