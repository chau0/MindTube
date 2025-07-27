# MindTube Backend - Test Commands Guide

This guide shows how to use `make` commands to run tests following the TDD guide patterns.

## 🚀 Quick Start

```bash
cd backend

# 1. Run basic tests (no dependencies required)
make test-tdd

# 2. Install test dependencies
make install-test

# 3. Run complete test suite
make test
```

## 📋 Available Test Commands

### Basic Testing
```bash
make test           # Run all tests with coverage
make test-unit      # Run unit tests only
make test-integration # Run integration tests only
make test-e2e       # Run end-to-end tests only
```

### Coverage & Analysis
```bash
make test-coverage  # Detailed coverage report (HTML + terminal)
make test-cov       # Alias for main test command
```

### Focused Testing
```bash
make test-azure     # Azure OpenAI integration tests
make test-api       # API endpoint tests
make test-fast      # Fast tests only (exclude slow)
make test-slow      # Slow tests only
```

### Development Workflow
```bash
make test-tdd       # TDD test runner (no external deps)
make test-watch     # Watch mode (re-run on file changes)
make test-parallel  # Parallel execution
make test-debug     # Debug mode with PDB
```

## 🔧 Setup Commands

### Install Dependencies
```bash
make install-test     # Install test deps with uv
make install-test-pip # Install test deps with pip (fallback)
make install-dev      # Install all dev dependencies
```

### Environment Setup
```bash
make setup           # Complete project setup
make setup-simple    # Simplified setup (no ML deps)
```

## 📊 Test Structure

The test suite follows TDD guide patterns:

```
tests/
├── conftest.py              # Pytest fixtures
├── unit/                    # Unit tests
│   ├── test_llm_client.py
│   └── test_summarization.py
├── integration/             # Integration tests
│   └── test_api_endpoints.py
└── e2e/                     # End-to-end tests
    └── test_full_pipeline.py
```

## 🧪 Test Categories

### Unit Tests (`make test-unit`)
- **LLM Client**: Token counting, summary generation
- **Summarization Service**: Chunking, parsing, timestamps
- **Schemas**: Pydantic model validation
- **Configuration**: Settings loading

### Integration Tests (`make test-integration`)
- **API Endpoints**: Ingest, status, results, health
- **Service Interactions**: Component integration
- **Error Handling**: Invalid inputs, missing resources

### End-to-End Tests (`make test-e2e`)
- **Complete Pipeline**: URL to results workflow
- **Performance**: Response time baselines
- **Concurrent Processing**: Multiple job handling
- **Error Scenarios**: Invalid URLs, cancellation

## 📈 Coverage Reports

### Terminal Coverage
```bash
make test           # Basic coverage in terminal
```

### HTML Coverage Report
```bash
make test-coverage  # Generates htmlcov/index.html
```

### Coverage Configuration
- **Target**: 80% minimum coverage
- **Excludes**: Tests, migrations, __pycache__
- **Reports**: Terminal + HTML + XML

## 🎯 Test Markers

Tests are organized with pytest markers:

```bash
# Run by marker
python -m pytest -m "unit"          # Unit tests
python -m pytest -m "integration"   # Integration tests
python -m pytest -m "e2e"          # End-to-end tests
python -m pytest -m "slow"         # Slow tests
python -m pytest -m "azure"        # Azure OpenAI tests
```

## 🔍 Debugging Tests

### Debug Mode
```bash
make test-debug     # Run with PDB debugger
```

### Verbose Output
```bash
python -m pytest tests/ -v -s      # Verbose with print statements
```

### Specific Test
```bash
python -m pytest tests/unit/test_llm_client.py::TestAzureOpenAIClient::test_token_counting -v
```

## ⚡ Performance Testing

### Fast Tests Only
```bash
make test-fast      # Exclude slow tests
```

### Parallel Execution
```bash
make test-parallel  # Run tests in parallel
```

### Watch Mode
```bash
make test-watch     # Re-run on file changes
```

## 🛠️ Development Workflow

### TDD Workflow
1. **Write failing test**: Add test case
2. **Run tests**: `make test-unit`
3. **Write minimal code**: Make test pass
4. **Refactor**: Improve code while keeping tests green
5. **Repeat**: Continue TDD cycle

### Pre-commit Workflow
```bash
make test-fast      # Quick validation
make lint           # Code quality
make format         # Code formatting
make test           # Full test suite
```

### CI/CD Integration
```bash
# Typical CI pipeline commands
make install-test
make test-coverage
make lint
```

## 🔧 Configuration Files

### pytest.ini
- Test discovery settings
- Markers definition
- Async test configuration
- Warning filters

### .coveragerc
- Coverage measurement settings
- Exclusion patterns
- Report formats

### conftest.py
- Shared fixtures
- Mock objects
- Test utilities

## 📝 Example Usage

### Daily Development
```bash
# Start development session
make test-tdd       # Quick validation
make test-unit      # Run unit tests
make test-watch     # Keep running in background

# Before committing
make test-fast      # Quick validation
make test           # Full test suite
```

### Feature Development
```bash
# Working on Azure OpenAI feature
make test-azure     # Run related tests
make test-unit      # Unit tests
make test-integration # Integration tests

# Final validation
make test-coverage  # Check coverage
```

### Debugging Issues
```bash
# Debug failing test
make test-debug

# Run specific test with verbose output
python -m pytest tests/unit/test_llm_client.py -v -s

# Check test structure
python -m pytest --collect-only
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   make install-test   # Install test dependencies
   ```

2. **Import Errors**
   ```bash
   make test-tdd       # Use TDD runner (no deps)
   ```

3. **Slow Tests**
   ```bash
   make test-fast      # Skip slow tests
   ```

4. **Coverage Issues**
   ```bash
   make test-coverage  # Detailed coverage report
   ```

### Environment Issues
```bash
# Check Python environment
python --version
which python

# Verify test setup
python -c "import pytest; print('pytest available')"
```

## 📚 Additional Resources

- **TDD Guide**: `docs/tdd_guide_be.md`
- **Test Plan**: `docs/test-plan.md`
- **Azure Setup**: `docs/azure-openai-setup.md`
- **UV Guide**: `backend/UV_INSTALLATION_GUIDE.md`

## 🎉 Success Criteria

A successful test run should show:
- ✅ All tests passing
- 📊 Coverage > 80%
- 🚀 Fast execution time
- 🔍 Clear error messages
- 📝 Comprehensive test coverage

Use `make test` as your primary command for complete validation!