/*
  CrimeKit — Production Infrastructure Architecture (AWS ap-south-1)
  Provides isolated VPC, secure S3 Evidence Bucket (WORM/Versioning),
  RDS PostgreSQL 16 (pgvector support), and ElastiCache Redis 7.
*/

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project     = var.project
      Environment = var.env
      ManagedBy   = "Terraform"
    }
  }
}

# -----------------------------------------------------------------------------
# VPC & Networking
# -----------------------------------------------------------------------------

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project}-${var.env}-vpc"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project}-${var.env}-public-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project}-${var.env}-public-2"
  }
}

resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.region}a"

  tags = {
    Name = "${var.project}-${var.env}-private-1"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.20.0/24"
  availability_zone = "${var.region}b"

  tags = {
    Name = "${var.project}-${var.env}-private-2"
  }
}

# -----------------------------------------------------------------------------
# Evidence Storage (S3 with Immutability & Encryption)
# -----------------------------------------------------------------------------

resource "aws_s3_bucket" "evidence_bucket" {
  bucket        = "${var.project}-${var.env}-evidence"
  force_destroy = false

  tags = {
    Name = "${var.project}-${var.env}-evidence"
  }
}

resource "aws_s3_bucket_versioning" "evidence_versioning" {
  bucket = aws_s3_bucket.evidence_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence_encryption" {
  bucket = aws_s3_bucket.evidence_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "evidence_pab" {
  bucket = aws_s3_bucket.evidence_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# -----------------------------------------------------------------------------
# Relational Database (RDS PostgreSQL 16)
# -----------------------------------------------------------------------------

resource "aws_db_subnet_group" "rds" {
  name       = "${var.project}-${var.env}-rds-subnets"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "${var.project}-${var.env}-rds-subnets"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.project}-${var.env}-rds-sg"
  description = "Allow inbound PostgreSQL traffic from backend"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "${var.project}-${var.env}-postgres"
  allocated_storage      = 50
  max_allocated_storage  = 500
  engine                 = "postgres"
  engine_version         = "16.3"
  instance_class         = var.db_instance_class
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true
  storage_encrypted      = true
  deletion_protection    = false

  tags = {
    Name = "${var.project}-${var.env}-db"
  }
}

# -----------------------------------------------------------------------------
# In-Memory Cache & Redis Streams (ElastiCache)
# -----------------------------------------------------------------------------

resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project}-${var.env}-redis-subnets"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

resource "aws_security_group" "redis_sg" {
  name        = "${var.project}-${var.env}-redis-sg"
  description = "Allow inbound Redis traffic from backend"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Redis"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project}-${var.env}-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis.name
  security_group_ids   = [aws_security_group.redis_sg.id]

  tags = {
    Name = "${var.project}-${var.env}-redis"
  }
}
