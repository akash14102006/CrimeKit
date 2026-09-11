# CrimeKit Makefile
# Common operations for development and deployment

.PHONY: help dev prod down logs health test backup restore

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==================== Development ====================

dev: ## Start development environment
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile dev-tools up -d
	@echo "Development environment started"
	@echo "Backend: http://localhost:8000"
	@echo "pgAdmin: http://localhost:5050"
	@echo "Redis Commander: http://localhost:6380"
	@echo "MinIO Console: http://localhost:9001"

dev-build: ## Rebuild and start development environment
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile dev-tools up -d --build

# ==================== Production ====================

prod: ## Start production environment
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production environment started"

prod-monitoring: ## Start production with monitoring
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile monitoring up -d

# ==================== Common ====================

down: ## Stop all services
	docker compose down

down-clean: ## Stop all services and remove volumes (DELETES DATA)
	docker compose down -v

logs: ## View logs (all services)
	docker compose logs -f

logs-backend: ## View backend logs
	docker compose logs -f backend

logs-postgres: ## View postgres logs
	docker compose logs -f postgres

health: ## Run health checks
	@./infrastructure/scripts/health-check.sh --verbose

health-api: ## Check API health
	@curl -s http://localhost:8000/health/detailed | python -m json.tool

# ==================== Database ====================

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U crimekit_app -d crimekit

db-backup: ## Backup PostgreSQL
	@./infrastructure/scripts/backup.sh

db-restore: ## Restore PostgreSQL (set BACKUP_FILE=path)
	@./infrastructure/scripts/restore.sh --component postgres --backup-file $(BACKUP_FILE)

# ==================== Testing ====================

test: ## Run backend tests
	cd backend && python -m pytest tests/ -v

test-coverage: ## Run tests with coverage
	cd backend && python -m pytest tests/ --cov=app --cov-report=html

# ==================== Build ====================

build: ## Build all Docker images
	docker compose build

build-backend: ## Build backend image
	docker build -t crimekit-backend -f backend/Dockerfile backend/

build-backend-dev: ## Build backend dev image
	docker build -t crimekit-backend-dev -f backend/Dockerfile.dev backend/

# ==================== Monitoring ====================

monitoring: ## Start monitoring stack
	docker compose --profile monitoring up -d prometheus grafana

grafana: ## Open Grafana
	@echo "Grafana: http://localhost:3000"
	@echo "Default login: admin / ${GRAFANA_ADMIN_PASSWORD:-admin}"

prometheus: ## Open Prometheus
	@echo "Prometheus: http://localhost:9090"

# ==================== Cleanup ====================

clean: ## Remove unused Docker resources
	docker image prune -a
	docker volume prune
	docker network prune

clean-all: ## Remove all Docker resources (DELETES EVERYTHING)
	docker system prune -a --volumes
