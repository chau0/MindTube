# MindTube Backend Makefile

.PHONY: help setup install install-dev build run test test-cov lint format clean update check-deps

# Default target
help:
	@echo "MindTube Backend Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup          - Initial project setup (install uv, create venv, install deps)"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run            - Run the FastAPI development server"
	@echo "  build          - Build the application (validate imports)"
	@echo "  test           - Run tests"
	@echo "  test-cov       - Run tests with coverage report"
	@echo "  lint           - Run linting (flake8, mypy)"
	@echo "  format         - Format code (black, isort)"
	@echo "  check-deps     - Check for dependency vulnerabilities"
	@echo ""
	@echo "Maintenance:"
	@echo "  update         - Update dependencies"
	@echo "  clean          - Clean cache and temporary files"
	@echo ""

# Variables
PYTHON_VERSION := 3.9
VENV_NAME := .venv
PYTHON := $(VENV_NAME)/bin/python
PIP := $(VENV_NAME)/bin/pip
UV := $(VENV_NAME)/bin/uv

# Check if uv is installed
check-uv:
	@which uv > /dev/null || (echo "uv not found. Installing..." && curl -LsSf https://astral.sh/uv/install.sh | sh)

# Initial setup
setup: check-uv
	@echo "🚀 Setting up MindTube Backend..."
	@echo "📦 Creating virtual environment with Python $(PYTHON_VERSION)..."
	uv venv $(VENV_NAME) --python $(PYTHON_VERSION)
	@echo "📥 Installing dependencies..."
	$(MAKE) install-dev
	@echo "📁 Creating data directories..."
	mkdir -p data/{artifacts,cache,logs}
	@echo "📄 Copying environment file..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "⚠️  Please edit .env file with your API keys"; fi
	@echo "✅ Setup complete! Run 'make run' to start the server."

# Install production dependencies
install:
	@echo "📥 Installing production dependencies..."
	uv pip install -e .

# Install development dependencies
install-dev:
	@echo "📥 Installing development dependencies..."
	uv pip install -e ".[dev]"

# Build/validate the application
build:
	@echo "🔨 Building application..."
	@echo "🔍 Validating imports..."
	$(PYTHON) -c "import app.main; print('✅ Import validation successful')"
	@echo "🔍 Checking configuration..."
	$(PYTHON) -c "from app.core.config import settings; print('✅ Configuration validation successful')"

# Run the development server
run:
	@echo "🚀 Starting FastAPI development server..."
	@if [ ! -f .env ]; then echo "⚠️  .env file not found. Run 'make setup' first."; exit 1; fi
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	$(PYTHON) -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# Lint code
lint:
	@echo "🔍 Running linting..."
	@echo "📝 Checking with flake8..."
	$(PYTHON) -m flake8 app/ tests/
	@echo "🔍 Type checking with mypy..."
	$(PYTHON) -m mypy app/
	@echo "🔒 Security check with bandit..."
	$(PYTHON) -m bandit -r app/ -f json -o bandit-report.json || true

# Format code
format:
	@echo "🎨 Formatting code..."
	@echo "📝 Sorting imports with isort..."
	$(PYTHON) -m isort app/ tests/
	@echo "🖤 Formatting with black..."
	$(PYTHON) -m black app/ tests/
	@echo "✅ Code formatting complete!"

# Update dependencies
update:
	@echo "📦 Updating dependencies..."
	uv pip install --upgrade -e ".[dev]"
	@echo "📄 Generating new lock file..."
	uv pip freeze > requirements-lock.txt
	@echo "✅ Dependencies updated!"

# Check for dependency vulnerabilities
check-deps:
	@echo "🔒 Checking dependencies for vulnerabilities..."
	$(PYTHON) -m pip check
	@echo "✅ Dependency check complete!"

# Clean cache and temporary files
clean:
	@echo "🧹 Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ .coverage htmlcov/ .mypy_cache/ dist/ build/
	rm -f bandit-report.json
	@echo "✅ Cleanup complete!"

# Development workflow shortcuts
dev-setup: setup
	@echo "🔧 Development environment ready!"

dev-check: format lint test
	@echo "✅ All development checks passed!"

# Production build
prod-build: clean install build test
	@echo "🚀 Production build complete!"

# Show current environment info
info:
	@echo "📊 Environment Information:"
	@echo "Python: $(shell $(PYTHON) --version 2>&1)"
	@echo "Virtual Environment: $(VENV_NAME)"
	@echo "Dependencies installed: $(shell $(PIP) list | wc -l) packages"
	@echo "Project root: $(shell pwd)"
	@if [ -f .env ]; then echo "Environment file: ✅ Found"; else echo "Environment file: ❌ Missing"; fi