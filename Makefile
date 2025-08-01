# MindTube - Makefile for development and deployment
# Requires: Python 3.8+, pip

.PHONY: help init install-deps install-dev-deps install-api-deps install-whisper-deps
.PHONY: test lint typecheck format clean
.PHONY: serve run-summarize run-analyze run-mindmap
.PHONY: build publish docker-build docker-run
.PHONY: docs docs-serve

# Default target
help: ## Show this help message
	@echo "MindTube - YouTube Learning Assistant"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Python and pip detection
PYTHON := $(shell command -v python3 2> /dev/null || command -v python 2> /dev/null)
PIP := $(shell command -v pip3 2> /dev/null || command -v pip 2> /dev/null)

# Verify Python installation
check-python:
	@if [ -z "$(PYTHON)" ]; then \
		echo "Error: Python not found. Please install Python 3.8+"; \
		exit 1; \
	fi
	@$(PYTHON) -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" || \
		(echo "Error: Python 3.8+ required. Found: $$($(PYTHON) --version)"; exit 1)

# Project initialization
init: check-python ## Initialize the project (create directories, virtual environment)
	@echo "🚀 Initializing MindTube project..."
	@if [ ! -d ".venv" ]; then \
		echo "📦 Creating virtual environment..."; \
		$(PYTHON) -m venv .venv; \
	fi
	@echo "📁 Creating cache and output directories..."
	@mkdir -p ~/.mindtube/cache
	@mkdir -p output
	@mkdir -p logs
	@if [ ! -f ".env" ]; then \
		echo "⚙️  Creating .env file from template..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your Azure OpenAI credentials"; \
	fi
	@echo "✅ Project initialized! Next steps:"
	@echo "   1. Activate virtual environment: source .venv/bin/activate"
	@echo "   2. Install dependencies: make install-deps"
	@echo "   3. Configure .env file with your credentials"

# Dependency installation
install-deps: check-python ## Install core dependencies
	@echo "📦 Installing core dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install \
		youtube-transcript-api \
		openai \
		typer[all] \
		pydantic \
		requests \
		python-dotenv \
		pyyaml \
		rich
	@echo "✅ Core dependencies installed"

install-dev-deps: install-deps ## Install development dependencies
	@echo "🛠️  Installing development dependencies..."
	@$(PIP) install \
		pytest \
		pytest-cov \
		pytest-asyncio \
		pytest-mock \
		ruff \
		mypy \
		black \
		isort \
		pre-commit
	@echo "✅ Development dependencies installed"

install-api-deps: install-deps ## Install FastAPI dependencies
	@echo "🌐 Installing API dependencies..."
	@$(PIP) install \
		fastapi \
		uvicorn[standard] \
		websockets \
		slowapi \
		python-multipart
	@echo "✅ API dependencies installed"

install-whisper-deps: install-deps ## Install Whisper ASR dependencies
	@echo "🎤 Installing Whisper dependencies..."
	@$(PIP) install \
		faster-whisper \
		yt-dlp
	@echo "✅ Whisper dependencies installed"

# Code quality and testing
test: ## Run all tests
	@echo "🧪 Running tests..."
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make init' first."; \
		exit 1; \
	fi
	@$(PYTHON) -m pytest tests/ -v --cov=mindtube --cov-report=term-missing
	@echo "✅ Tests completed"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@$(PYTHON) -m pytest tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@$(PYTHON) -m pytest tests/integration/ -v -m integration

test-e2e: ## Run end-to-end tests
	@echo "🧪 Running end-to-end tests..."
	@$(PYTHON) -m pytest tests/e2e/ -v -m "not slow"

test-performance: ## Run performance tests
	@echo "🧪 Running performance tests..."
	@$(PYTHON) -m pytest tests/performance/ -v -m slow

test-coverage: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	@$(PYTHON) -m pytest tests/ --cov=mindtube --cov-report=html --cov-report=xml --cov-report=term-missing --cov-fail-under=80

test-fast: ## Run fast tests only (excludes slow and external)
	@echo "🧪 Running fast tests..."
	@$(PYTHON) -m pytest tests/ -v -m "not slow and not external"

test-external: ## Run external service tests
	@echo "🧪 Running external service tests..."
	@$(PYTHON) -m pytest tests/ -v -m external

lint: ## Run code linting
	@echo "🔍 Running linter..."
	@$(PYTHON) -m ruff check mindtube/ tests/
	@echo "✅ Linting completed"

lint-fix: ## Run linter with auto-fix
	@echo "🔧 Running linter with auto-fix..."
	@$(PYTHON) -m ruff check --fix mindtube/ tests/

typecheck: ## Run type checking
	@echo "🔍 Running type checker..."
	@$(PYTHON) -m mypy mindtube/
	@echo "✅ Type checking completed"

format: ## Format code
	@echo "🎨 Formatting code..."
	@$(PYTHON) -m black mindtube/ tests/
	@$(PYTHON) -m isort mindtube/ tests/
	@echo "✅ Code formatted"

format-check: ## Check code formatting
	@echo "🎨 Checking code formatting..."
	@$(PYTHON) -m black --check mindtube/ tests/
	@$(PYTHON) -m isort --check-only mindtube/ tests/

# Development server
serve: ## Start development API server
	@echo "🚀 Starting development server..."
	@if [ ! -f ".env" ]; then \
		echo "❌ .env file not found. Run 'make init' first."; \
		exit 1; \
	fi
	@$(PYTHON) -m uvicorn mindtube.api.app:create_app --reload --host 0.0.0.0 --port 8000

# CLI commands with parameters
run-summarize: ## Run summarize command (usage: make run-summarize URL=https://youtu.be/ID)
	@if [ -z "$(URL)" ]; then \
		echo "❌ URL parameter required. Usage: make run-summarize URL=https://youtu.be/VIDEO_ID"; \
		exit 1; \
	fi
	@echo "📝 Summarizing video: $(URL)"
	@$(PYTHON) -m mindtube.cli.main summarize "$(URL)" $(ARGS)

run-analyze: ## Run analyze command (usage: make run-analyze URL=https://youtu.be/ID ARGS="--llm azure")
	@if [ -z "$(URL)" ]; then \
		echo "❌ URL parameter required. Usage: make run-analyze URL=https://youtu.be/VIDEO_ID"; \
		exit 1; \
	fi
	@echo "🔍 Analyzing video: $(URL)"
	@$(PYTHON) -m mindtube.cli.main analyze "$(URL)" $(ARGS)

run-mindmap: ## Run mindmap command (usage: make run-mindmap URL=https://youtu.be/ID ARGS="--save")
	@if [ -z "$(URL)" ]; then \
		echo "❌ URL parameter required. Usage: make run-mindmap URL=https://youtu.be/VIDEO_ID"; \
		exit 1; \
	fi
	@echo "🗺️  Creating mindmap for video: $(URL)"
	@$(PYTHON) -m mindtube.cli.main mindmap "$(URL)" $(ARGS)

run-transcript: ## Run transcript command (usage: make run-transcript URL=https://youtu.be/ID)
	@if [ -z "$(URL)" ]; then \
		echo "❌ URL parameter required. Usage: make run-transcript URL=https://youtu.be/VIDEO_ID"; \
		exit 1; \
	fi
	@echo "📄 Extracting transcript for video: $(URL)"
	@$(PYTHON) -m mindtube.cli.main transcript "$(URL)" $(ARGS)

# Build and distribution
build: clean ## Build distribution packages
	@echo "📦 Building distribution packages..."
	@$(PYTHON) -m pip install --upgrade build
	@$(PYTHON) -m build
	@echo "✅ Build completed. Check dist/ directory"

publish: build ## Publish to PyPI (requires credentials)
	@echo "🚀 Publishing to PyPI..."
	@$(PYTHON) -m pip install --upgrade twine
	@$(PYTHON) -m twine upload dist/*

publish-test: build ## Publish to Test PyPI
	@echo "🧪 Publishing to Test PyPI..."
	@$(PYTHON) -m pip install --upgrade twine
	@$(PYTHON) -m twine upload --repository testpypi dist/*

# Docker operations
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	@docker build -t mindtube:latest .
	@echo "✅ Docker image built: mindtube:latest"

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	@docker run -p 8000:8000 --env-file .env mindtube:latest

docker-dev: ## Run Docker container in development mode
	@echo "🐳 Running Docker container in development mode..."
	@docker run -p 8000:8000 -v $(PWD):/app --env-file .env mindtube:latest

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@$(PYTHON) -m pip install mkdocs mkdocs-material
	@mkdocs build
	@echo "✅ Documentation generated in site/"

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@$(PYTHON) -m pip install mkdocs mkdocs-material
	@mkdocs serve

# Cleanup
clean: ## Clean build artifacts and cache
	@echo "🧹 Cleaning up..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup completed"

clean-cache: ## Clean MindTube cache
	@echo "🧹 Cleaning MindTube cache..."
	@rm -rf ~/.mindtube/cache/*
	@rm -rf output/*
	@rm -rf logs/*
	@echo "✅ Cache cleaned"

# Development workflow helpers
dev-setup: init install-dev-deps install-api-deps ## Complete development setup
	@echo "🎉 Development environment ready!"
	@echo "Next steps:"
	@echo "  1. Activate virtual environment: source .venv/bin/activate"
	@echo "  2. Configure .env file"
	@echo "  3. Run tests: make test"
	@echo "  4. Start development: make serve"

check: lint typecheck test ## Run all quality checks
	@echo "✅ All quality checks passed!"

# CI/CD helpers
ci-test: ## Run tests in CI environment
	@echo "🤖 Running CI tests..."
	@$(PYTHON) -m pytest tests/ --cov=mindtube --cov-report=xml --cov-report=term

ci-quality: ## Run quality checks in CI environment
	@echo "🤖 Running CI quality checks..."
	@$(PYTHON) -m ruff check mindtube/ tests/
	@$(PYTHON) -m mypy mindtube/
	@$(PYTHON) -m black --check mindtube/ tests/
	@$(PYTHON) -m isort --check-only mindtube/ tests/

# Security
security-scan: ## Run security scan
	@echo "🔒 Running security scan..."
	@$(PIP) install safety bandit
	@safety check
	@bandit -r mindtube/

# Performance profiling
profile: ## Run performance profiling
	@echo "📊 Running performance profiling..."
	@$(PYTHON) -m pip install py-spy
	@echo "Use: py-spy top --pid <process_id> for live profiling"

# Database operations (if needed later)
db-init: ## Initialize database
	@echo "🗄️  Initializing database..."
	@echo "Database operations not implemented yet"

db-migrate: ## Run database migrations
	@echo "🗄️  Running database migrations..."
	@echo "Database operations not implemented yet"

# Monitoring and health checks
health-check: ## Check system health
	@echo "🏥 Running health checks..."
	@$(PYTHON) -c "import mindtube; print('✅ MindTube imports successfully')" 2>/dev/null || echo "❌ MindTube import failed"
	@$(PYTHON) -c "import youtube_transcript_api; print('✅ YouTube Transcript API available')" 2>/dev/null || echo "❌ YouTube Transcript API not available"
	@$(PYTHON) -c "import openai; print('✅ OpenAI library available')" 2>/dev/null || echo "❌ OpenAI library not available"
	@if [ -f ".env" ]; then echo "✅ .env file exists"; else echo "❌ .env file missing"; fi

# Version management
version: ## Show current version
	@$(PYTHON) -c "import mindtube; print(f'MindTube version: {mindtube.__version__}')" 2>/dev/null || echo "Version not available"

bump-version: ## Bump version (usage: make bump-version VERSION=0.2.0)
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ VERSION parameter required. Usage: make bump-version VERSION=0.2.0"; \
		exit 1; \
	fi
	@echo "📈 Bumping version to $(VERSION)..."
	@sed -i '/^\[project\]/,/^\[/ s/version = "[^"]*"/version = "$(VERSION)"/' pyproject.toml
	@echo "✅ Version bumped to $(VERSION)"