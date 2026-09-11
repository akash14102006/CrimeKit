variable "project" {
  description = "Project name"
  type        = string
  default     = "crimekit"
}

variable "env" {
  description = "Deployment environment (dev|staging|prod)"
  type        = string
  default     = "prod"
}

variable "region" {
  description = "AWS Cloud region (default: ap-south-1 Mumbai)"
  type        = string
  default     = "ap-south-1"
}

variable "db_name" {
  description = "PostgreSQL Database Name"
  type        = string
  default     = "crimekit"
}

variable "db_username" {
  description = "PostgreSQL Master Username"
  type        = string
  default     = "crimekit_admin"
}

variable "db_password" {
  description = "PostgreSQL Master Password (injected via Secrets Manager in production)"
  type        = string
  sensitive   = true
  default     = "ChangeMe_In_Production_Secrets!"
}

variable "db_instance_class" {
  description = "RDS DB instance class"
  type        = string
  default     = "db.t4g.medium"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t4g.small"
}
