output "vpc_id" {
  description = "ID of the CrimeKit VPC"
  value       = aws_vpc.main.id
}

output "s3_evidence_bucket" {
  description = "Name of the CrimeKit S3 Evidence Bucket"
  value       = aws_s3_bucket.evidence_bucket.bucket
}

output "rds_endpoint" {
  description = "PostgreSQL RDS connection endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}
