# MindTube Development Makefile
.PHONY: help setup install install-dev clean lint format type-check test test-unit test-integration test-e2e test-cov dev build docker-build docker-up docker-down docs

# Default target
help: ## Show this help message
	@echo "MindTube Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup and Installation
setup: ## Initial project setup (install dev dependencies, pre-commit hooks)
	python3 -m pip install --upgrade pip
	python3 -m pip install -e ".[dev]"
	python3 -m pre_commit install
	@echo "✅ Setup complete! Run 'make test' to verify everything works."

install: ## Install package in production mode
	python3 -m pip install -e .

install-dev: ## Install package with development dependencies
	python3 -m pip install -e ".[dev]"

clean: ## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Code Quality
lint: ## Run all linting checks (ruff + mypy)
	ruff check .
	mypy .

format: ## Format code with ruff and black
	ruff format .
	ruff check --fix .

type-check: ## Run type checking with mypy
	mypy .

# Testing
test: ## Run all tests (unit + integration, skip e2e)
	pytest -m "not e2e" --tb=short

test-unit: ## Run only unit tests (fast)
	pytest -m "unit" --tb=short

test-integration: ## Run integration tests
	pytest -m "integration" --tb=short

test-e2e: ## Run end-to-end tests (requires real services)
	pytest -m "e2e" --tb=short

test-cov: ## Run tests with coverage report
	pytest -m "not e2e" --cov --cov-report=html --cov-report=term

test-all: ## Run ALL tests including e2e (slow)
	pytest --tb=short

# Development
dev: ## Start development environment
	@echo "🚀 Starting MindTube development environment..."
	@echo "📁 Project structure:"
	@echo "  packages/core/mindtube/  - Core Python package"
	@echo "  apps/cli/               - CLI application"
	@echo "  apps/api/               - FastAPI backend"
	@echo "  apps/web/               - Next.js frontend"
	@echo ""
	@echo "🔧 Available commands:"
	@echo "  make test              - Run tests"
	@echo "  make lint              - Check code quality"
	@echo "  make format            - Format code"
	@echo "  make docker-up         - Start services"
	@echo ""
	@echo "📝 Copy .env.example to .env and configure your settings"

# Build
build: ## Build package for distribution
	python -m build

# Docker
docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start all services with Docker Compose
	docker compose up -d

docker-down: ## Stop all Docker services
	docker compose down

docker-logs: ## Show Docker service logs
	docker compose logs -f

# Documentation
docs: ## Generate documentation (placeholder)
	@echo "📚 Documentation generation not yet implemented"
	@echo "See documents/ directory for current documentation"

# CI/CD helpers
ci-setup: ## Setup for CI environment
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

ci-test: ## Run CI test suite
	pytest -m "not e2e" --cov --cov-report=xml --cov-report=term

ci-lint: ## Run CI linting
	ruff check .
	mypy .

# Project structure helpers
scaffold: ## Create basic project structure
	@echo "📁 Creating project structure..."
	mkdir -p packages/core/mindtube
	mkdir -p packages/core/tests
	mkdir -p apps/cli/mindtube_cli
	mkdir -p apps/api/app
	mkdir -p apps/web
	mkdir -p tests/unit
	mkdir -p tests/integration
	mkdir -p tests/e2e
	mkdir -p docs
	@echo "✅ Project structure created"

# Utility commands
check: lint test-unit ## Quick check (lint + unit tests)

pre-commit: ## Run pre-commit hooks manually
	pre-commit run --all-files

update-deps: ## Update development dependencies
	pip install --upgrade pip
	pip install --upgrade -e ".[dev]"

# Version management
version: ## Show current version
	python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

# Environment info
info: ## Show development environment info
	@echo "🔍 Environment Information:"
	@echo "Python: $(shell python --version)"
	@echo "Pip: $(shell pip --version)"
	@echo "Project: $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])")"
	@echo "Version: $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")"
	@echo "Working Directory: $(shell pwd)"