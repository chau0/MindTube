# TASK-002: Makefile Implementation

## Task Information
- **ID**: TASK-002
- **Phase**: 0 - Project Foundation
- **Estimate**: 45 minutes
- **Dependencies**: TASK-001
- **Status**: 🔴 Backlog

## Description
Implement all Makefile targets referenced in the roadmap document. This provides a consistent interface for development, testing, and deployment operations across different environments.

## Acceptance Criteria
- [ ] `make init` - Initialize project
- [ ] `make install-deps` - Install core dependencies
- [ ] `make install-dev-deps` - Install development dependencies
- [ ] `make install-api-deps` - Install FastAPI dependencies
- [ ] `make install-whisper-deps` - Install Whisper dependencies
- [ ] `make test` - Run tests
- [ ] `make lint` - Run linting
- [ ] `make typecheck` - Run type checking
- [ ] `make serve` - Start development server
- [ ] `make run-summarize`, `make run-analyze`, `make run-mindmap` - CLI commands
- [ ] All targets work correctly and provide helpful output
- [ ] Error handling for missing dependencies

## Makefile Implementation

```makefile
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
	@$(PYTHON) -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@$(PYTHON) -m pytest tests/integration/ -v -m "not slow"

test-e2e: ## Run end-to-end tests
	@echo "🧪 Running end-to-end tests..."
	@$(PYTHON) -m pytest tests/e2e/ -v

test-performance: ## Run performance tests
	@echo "🧪 Running performance tests..."
	@$(PYTHON) -m pytest tests/performance/ -v

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
	@sed -i 's/version = "[^"]*"/version = "$(VERSION)"/' pyproject.toml
	@echo "✅ Version bumped to $(VERSION)"
```

## Implementation Steps

### Step 1: Create the Makefile
Create the file `Makefile` in the project root with the content above.

### Step 2: Test Basic Targets
```bash
# Test help target
make help

# Test Python detection
make check-python

# Test initialization
make init
```

### Step 3: Test Dependency Installation
```bash
# Test core dependencies
make install-deps

# Test development dependencies  
make install-dev-deps
```

### Step 4: Test Quality Targets
```bash
# Test linting (will fail initially, that's expected)
make lint

# Test type checking (will fail initially, that's expected)
make typecheck

# Test formatting
make format
```

### Step 5: Test CLI Targets
```bash
# Test CLI commands (will fail until implementation, that's expected)
make run-summarize URL=https://youtu.be/dQw4w9WgXcQ
```

## Verification Steps

### Step 1: Verify Makefile Syntax
```bash
make -n help
```
Should show the commands that would be executed without errors.

### Step 2: Test Help Target
```bash
make help
```
Should display a nicely formatted help message with all available targets.

### Step 3: Test Python Detection
```bash
make check-python
```
Should pass if Python 3.8+ is installed, fail with helpful message otherwise.

### Step 4: Test Project Initialization
```bash
make init
```
Should create virtual environment, directories, and .env file.

### Step 5: Test Dependency Installation
```bash
source .venv/bin/activate  # Activate virtual environment
make install-deps
```
Should install all core dependencies without errors.

## Success Criteria Checklist

- [ ] Makefile created with all required targets
- [ ] `make help` shows formatted help message
- [ ] `make init` creates project structure and virtual environment
- [ ] `make install-deps` installs core dependencies successfully
- [ ] `make install-dev-deps` installs development dependencies
- [ ] `make install-api-deps` installs FastAPI dependencies
- [ ] `make install-whisper-deps` installs Whisper dependencies
- [ ] `make test` target exists (will fail until tests implemented)
- [ ] `make lint` target exists (will fail until code implemented)
- [ ] `make typecheck` target exists (will fail until code implemented)
- [ ] `make serve` target exists (will fail until API implemented)
- [ ] CLI targets (`run-summarize`, `run-analyze`, `run-mindmap`) exist
- [ ] Error handling for missing parameters works correctly
- [ ] All targets provide helpful output and error messages

## Error Handling Examples

### Missing URL Parameter
```bash
$ make run-summarize
❌ URL parameter required. Usage: make run-summarize URL=https://youtu.be/VIDEO_ID
```

### Missing Python
```bash
$ make check-python
Error: Python not found. Please install Python 3.8+
```

### Missing Virtual Environment
```bash
$ make test
❌ Virtual environment not found. Run 'make init' first.
```

## Next Steps

After completing this task:
1. Move to **TASK-003: Core Dependencies Configuration**
2. Update task status to 🟢 Done
3. Test the Makefile with actual dependency installation

## Notes

- The Makefile uses PHONY targets to avoid conflicts with files
- Error messages are user-friendly and provide guidance
- All targets include helpful descriptions for the help system
- The Makefile supports both development and CI/CD workflows
- Virtual environment detection ensures consistent Python environment
- Parameter validation prevents common usage errors

## Troubleshooting

**Issue**: `make: command not found`
**Solution**: Install make utility (usually pre-installed on Unix systems)

**Issue**: Python version errors
**Solution**: Ensure Python 3.8+ is installed and accessible

**Issue**: Permission errors during init
**Solution**: Ensure write permissions in project directory

**Issue**: Virtual environment activation fails
**Solution**: Check Python venv module is available