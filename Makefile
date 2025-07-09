.PHONY: help build start stop logs clean test dev setup

# Default target
help:
	@echo "pgpfinlitbot - Student Financial Literacy Chatbot"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup    - Initial project setup"
	@echo "  make start    - Start all services"
	@echo "  make dev      - Start in development mode"
	@echo "  make stop     - Stop all services"
	@echo "  make build    - Build all containers"
	@echo "  make logs     - View service logs"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up containers and volumes"
	@echo "  make ingest   - Run content ingestion"
	@echo "  make models   - Download required models"

# Initial project setup
setup:
	@echo "Setting up pgpfinlitbot..."
	cp .env.example .env || true
	docker compose pull
	@echo "Setup complete! Edit .env if needed, then run 'make start'"

# Build all containers
build:
	docker compose build

# Start all services
start:
	docker compose up -d
	@echo "Services started! Check status with 'make logs'"
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:8080/docs"

# Development mode (with hot reload)
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Stop all services
stop:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Run tests
test:
	docker compose exec api pytest tests/
	cd frontend && npm test

# Run benchmark evaluation  
bench:
	python scripts/bench.py --url http://localhost:8080

# Run load testing (requires k6)
loadtest:
	k6 run scripts/loadtest.js

# Download required models
models:
	docker compose exec ollama ollama pull mistral:7b-instruct-q4_K_M
	docker compose exec ollama ollama pull nomic-embed-text-v1
	docker compose exec ollama ollama list

# Run content ingestion
ingest:
	docker compose exec api python scripts/ingest.py

# Clean up everything
clean:
	docker compose down -v
	docker system prune -f
	docker volume prune -f

# Health checks
health:
	@echo "Checking service health..."
	curl -f http://localhost:8080/health || echo "API unhealthy"
	curl -f http://localhost:11434/api/version || echo "Ollama unhealthy"
	curl -f http://localhost:8000/api/v1/heartbeat || echo "ChromaDB unhealthy"

# Production deployment
deploy:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Backup data
backup:
	docker compose exec chromadb tar czf /tmp/chroma-backup.tar.gz /chroma/chroma
	docker cp pgpbot-chromadb:/tmp/chroma-backup.tar.gz ./backups/chroma-$(shell date +%Y%m%d-%H%M%S).tar.gz

# Restore data
restore:
	@read -p "Enter backup file path: " backup && \
	docker cp $$backup pgpbot-chromadb:/tmp/restore.tar.gz && \
	docker compose exec chromadb tar xzf /tmp/restore.tar.gz -C /chroma/ 