# Environment Variables Reference

## Application
| Variable | Default | Description |
|----------|---------|-------------|
| APP_NAME | CrimeKit | Application name |
| APP_ENV | development | Environment (development/production) |
| APP_DEBUG | true | Debug mode |
| APP_SECRET_KEY | - | Secret key for sessions |
| APP_LOG_LEVEL | info | Logging level |

## Database (PostgreSQL)
| Variable | Default | Description |
|----------|---------|-------------|
| POSTGRES_HOST | postgres | Database host |
| POSTGRES_PORT | 5432 | Database port |
| POSTGRES_DB | crimekit | Database name |
| POSTGRES_USER | crimekit_app | Database user |
| POSTGRES_PASSWORD | - | Database password |
| DATABASE_URL | - | Full connection URL |

## Redis
| Variable | Default | Description |
|----------|---------|-------------|
| REDIS_HOST | redis | Redis host |
| REDIS_PORT | 6379 | Redis port |
| REDIS_PASSWORD | - | Redis password |
| REDIS_DB | 0 | Redis database |
| REDIS_URL | - | Full connection URL |

## Neo4j
| Variable | Default | Description |
|----------|---------|-------------|
| NEO4J_URI | bolt://neo4j:7687 | Neo4j bolt URI |
| NEO4J_USER | neo4j | Neo4j username |
| NEO4J_PASSWORD | - | Neo4j password |

## MinIO
| Variable | Default | Description |
|----------|---------|-------------|
| MINIO_ENDPOINT | minio:9000 | MinIO endpoint |
| MINIO_ACCESS_KEY | - | MinIO access key |
| MINIO_SECRET_KEY | - | MinIO secret key |
| MINIO_BUCKET_EVIDENCE | crimekit-evidence | Evidence bucket |

## JWT
| Variable | Default | Description |
|----------|---------|-------------|
| JWT_SECRET_KEY | - | JWT signing key |
| JWT_ALGORITHM | HS256 | JWT algorithm |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Access token TTL |
