provider "aws" {
  region = "us-east-1"
}

variable "project_name" {
  default = "product-vector-search"
}

# 1. S3 Bucket for Data
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "${var.project_name}-data-${random_id.bucket_suffix.hex}"
  
  tags = {
    Name = "Vector Search Data"
  }
}

# 2. IAM Role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "serverless_vector_search_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 3. Security Group for RDS
resource "aws_security_group" "rds_sg" {
  name        = "vector_rds_sg"
  description = "Allow inbound traffic from Lambda"
  
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # NOTE: For demo purposes only. Restrict to VPC/Lambda SG in production.
  }
}

# 4. RDS Instance (MySQL)
# Using Free Tier eligible settings
resource "aws_db_instance" "default" {
  allocated_storage      = 20
  db_name                = "vector_search_db"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  username               = "admin"
  password               = "password123Secure!" # In prod, use Secrets Manager / Variables
  parameter_group_name   = "default.mysql8.0"
  skip_final_snapshot    = true
  publicly_accessible    = true # For local helper script access
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
}

# 5. Lambda Function
# Note: Python dependencies (sentence-transformers) are LARGE. 
# This simple zip deployment assumes you have packaged dependencies into the zip 
# or are using a Layer. For "Advanced" production, use `package_type = Image`.
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/lambda_handler.py"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "search_lambda" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "product_search_function"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60 
  memory_size   = 1024 # ML inference needs more memory

  environment {
    variables = {
      DB_HOST     = aws_db_instance.default.address
      DB_NAME     = "vector_search_db"
      DB_USER     = "admin"
      DB_PASSWORD = "password123Secure!"
    }
  }

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

output "rds_endpoint" {
  value = aws_db_instance.default.address
}

output "s3_bucket_name" {
  value = aws_s3_bucket.data_bucket.id
}
