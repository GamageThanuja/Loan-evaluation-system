# Makefile for Home Credit Loan Approval System

.PHONY: help install setup start stop clean build test

help: ## Show this help message
	@echo "Home Credit Loan Approval System - Commands"
	@echo "============================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	npm install
	cd frontend && npm install
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

setup: install ## Complete setup (install + configure)
	@echo "⚙️ Setting up environment..."
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "Created backend/.env - Please configure!"; fi
	@if [ ! -f frontend/.env.local ]; then cp frontend/.env.local.example frontend/.env.local 2>/dev/null || true; fi
	@echo "✅ Setup complete!"

start: ## Start all services (development mode)
	@echo "🚀 Starting all services..."
	@chmod +x start.sh
	./start.sh

stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	@chmod +x stop.sh
	./stop.sh

dev: start ## Alias for start

clean: ## Clean all build artifacts and caches
	@echo "🧹 Cleaning..."
	rm -rf frontend/.next
	rm -rf frontend/node_modules
	rm -rf backend/venv
	rm -rf backend/__pycache__
	rm -rf logs/*.log
	@echo "✅ Cleaned!"

build: ## Build frontend for production
	@echo "🏗️ Building frontend..."
	cd frontend && npm run build

test: ## Run all tests
	@echo "🧪 Running tests..."
	cd backend && source venv/bin/activate && pytest || true
	cd frontend && npm test || true

docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up: ## Start services with Docker
	@echo "🐳 Starting services with Docker..."
	docker-compose up -d

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

logs: ## View application logs
	@echo "📝 Viewing logs..."
	tail -f logs/*.log

status: ## Check service status
	@echo "📊 Service Status:"
	@lsof -i :3000 >/dev/null 2>&1 && echo "✅ Frontend running on port 3000" || echo "❌ Frontend not running"
	@lsof -i :8000 >/dev/null 2>&1 && echo "✅ Backend running on port 8000" || echo "❌ Backend not running"

.DEFAULT_GOAL := help
