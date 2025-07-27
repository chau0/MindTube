# MindTube Backend Makefile

.PHONY: help setup install install-dev build run test test-cov test-unit test-integration test-e2e test-coverage test-watch test-tdd test-fast test-slow test-azure test-api test-parallel test-debug lint format clean update check-deps

# Default target
help:
	@echo "MindTube Backend Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup          - Initial project setup (install uv, create venv, install deps)"
	@echo "  setup-simple   - Simplified setup without ML dependencies (no compilation needed)"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  install-simple - Install simplified dependencies (no spacy/whisper)"
	@echo ""
	@echo "Development:"
	@echo "  run            - Run the FastAPI development server"
	@echo "  build          - Build the application (validate imports)"
	@echo "  lint           - Run linting (flake8, mypy)"
	@echo "  format         - Format code (black, isort)"
	@echo "  check-deps     - Check for dependency vulnerabilities"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests with coverage"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e       - Run end-to-end tests only"
	@echo "  test-coverage  - Run tests with detailed coverage"
	@echo "  test-tdd       - Run TDD test runner (no deps)"
	@echo "  test-fast      - Run fast tests only"
	@echo "  test-azure     - Run Azure OpenAI tests"
	@echo "  test-api       - Run API tests"
	@echo "  test-watch     - Run tests in watch mode"
	@echo "  test-parallel  - Run tests in parallel"
	@echo "  test-debug     - Run tests with debugging"
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

# Simplified setup (without ML dependencies that require compilation)
setup-simple: check-uv
	@echo "🚀 Setting up MindTube Backend (Simplified)..."
	@echo "📦 Creating virtual environment with Python $(PYTHON_VERSION)..."
	uv venv $(VENV_NAME) --python $(PYTHON_VERSION)
	@echo "📥 Installing simplified dependencies..."
	$(MAKE) install-simple
	@echo "📁 Creating data directories..."
	mkdir -p data/{artifacts,cache,logs}
	@echo "📄 Copying environment file..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "⚠️  Please edit .env file with your API keys"; fi
	@echo "✅ Simplified setup complete! Note: ML features (spacy, whisper) not available."
	@echo "💡 To install full dependencies, run 'sudo apt install build-essential' then 'make install-dev'"

# Install production dependencies
install:
	@echo "📥 Installing production dependencies..."
	uv pip install -e .

# Install development dependencies
install-dev:
	@echo "📥 Installing development dependencies..."
	uv pip install -e ".[dev]"

# Install test dependencies
install-test:
	@echo "🧪 Installing test dependencies..."
	uv pip install pytest pytest-asyncio pytest-cov pytest-watch pytest-xdist httpx

# Install test dependencies with pip (fallback)
install-test-pip:
	@echo "🧪 Installing test dependencies with pip..."
	$(PIP) install pytest pytest-asyncio pytest-cov pytest-watch pytest-xdist httpx

# Install simplified dependencies (without heavy ML packages)
install-simple:
	@echo "📥 Installing simplified dependencies..."
	uv pip install -r requirements-simple.txt

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

# Run all tests (unit + integration + e2e)
test:
	@echo "🧪 Running complete test suite..."
	$(PYTHON) -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

# Run tests with coverage (alias for test)
test-cov: test

# Run unit tests only
test-unit:
	@echo "🔬 Running unit tests..."
	$(PYTHON) -m pytest tests/unit/ -v --tb=short

# Run integration tests only
test-integration:
	@echo "🔗 Running integration tests..."
	$(PYTHON) -m pytest tests/integration/ -v --tb=short

# Run end-to-end tests only
test-e2e:
	@echo "🎯 Running end-to-end tests..."
	$(PYTHON) -m pytest tests/e2e/ -v --tb=short

# Run tests with detailed coverage report
test-coverage:
	@echo "📊 Running tests with coverage analysis..."
	$(PYTHON) -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80

# Run tests in watch mode (re-run on file changes)
test-watch:
	@echo "👀 Running tests in watch mode..."
	$(PYTHON) -m pytest-watch tests/ -- -v --tb=short

# Run TDD test runner (no external dependencies)
test-tdd:
	@echo "🚀 Running TDD test runner..."
	$(PYTHON) run_tdd_tests.py

# Run fast tests only (exclude slow/e2e tests)
test-fast:
	@echo "⚡ Running fast tests..."
	$(PYTHON) -m pytest tests/unit/ tests/integration/ -v --tb=short -m "not slow"

# Run slow tests only
test-slow:
	@echo "🐌 Running slow tests..."
	$(PYTHON) -m pytest tests/ -v --tb=short -m "slow"

# Run Azure OpenAI integration tests
test-azure:
	@echo "☁️  Running Azure OpenAI integration tests..."
	$(PYTHON) -m pytest tests/ -v --tb=short -k "azure or llm or summarization"

# Run API-specific tests
test-api:
	@echo "🌐 Running API tests..."
	$(PYTHON) -m pytest tests/integration/test_api_endpoints.py tests/e2e/ -v --tb=short

# Run tests in parallel (requires pytest-xdist)
test-parallel:
	@echo "⚡ Running tests in parallel..."
	$(PYTHON) -m pytest tests/ -v --tb=short -n auto

# Run tests with debugging enabled
test-debug:
	@echo "🐛 Running tests with debugging..."
	$(PYTHON) -m pytest tests/ -v -s --tb=long --pdb-trace

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