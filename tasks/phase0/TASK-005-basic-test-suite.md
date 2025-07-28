# TASK-005: Basic Test Suite

## Task Information
- **ID**: TASK-005
- **Phase**: 0 - Project Foundation
- **Estimate**: 60 minutes
- **Dependencies**: TASK-004
- **Status**: 🔴 Backlog

## Description
Set up the testing infrastructure with pytest, create basic smoke tests, and establish testing patterns for the project. This ensures code quality and provides a foundation for test-driven development.

## Acceptance Criteria
- [ ] Configure pytest with proper settings
- [ ] Create test directory structure
- [ ] Implement basic smoke tests
- [ ] Add test fixtures and utilities
- [ ] Configure test coverage reporting
- [ ] Add CI-friendly test configuration
- [ ] Create testing documentation
- [ ] Verify all tests pass with `make test`

## Test Infrastructure Setup

### Step 1: Create pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=mindtube
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests that may be skipped in CI
    external: Tests that require external services
```

### Step 2: Create Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── test_config.py
│   └── core/
│       └── __init__.py
├── integration/
│   ├── __init__.py
│   └── adapters/
│       └── __init__.py
├── fixtures/
│   ├── __init__.py
│   ├── sample_transcript.json
│   └── sample_video_metadata.json
└── utils/
    ├── __init__.py
    └── test_helpers.py
```

### Step 3: Create tests/conftest.py

```python
"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from mindtube.core.config import MindTubeConfig

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key",
        "MINDTUBE_CACHE_ENABLED": "false",
        "MINDTUBE_LOG_LEVEL": "DEBUG"
    }):
        yield MindTubeConfig()

@pytest.fixture
def sample_youtube_url():
    """Sample YouTube URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

@pytest.fixture
def sample_video_id():
    """Sample YouTube video ID for testing."""
    return "dQw4w9WgXcQ"

@pytest.fixture
def mock_youtube_transcript():
    """Mock YouTube transcript data."""
    return [
        {"text": "Hello everyone", "start": 0.0, "duration": 2.5},
        {"text": "Welcome to this video", "start": 2.5, "duration": 3.0},
        {"text": "Today we'll learn about", "start": 5.5, "duration": 2.8},
        {"text": "artificial intelligence", "start": 8.3, "duration": 3.2}
    ]

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [{
            "message": {
                "content": "This is a test summary of the video content."
            }
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
```

### Step 4: Create tests/utils/test_helpers.py

```python
"""Test helper utilities."""

import json
from pathlib import Path
from typing import Dict, Any

def load_test_fixture(filename: str) -> Dict[str, Any]:
    """Load a test fixture from the fixtures directory."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / filename
    with open(fixture_path, 'r') as f:
        return json.load(f)

def create_mock_transcript_response(segments: list) -> dict:
    """Create a mock transcript response for testing."""
    return {
        "video_id": "test_video_id",
        "language": "en",
        "segments": segments
    }

def assert_valid_json_output(output_path: Path):
    """Assert that a file contains valid JSON."""
    assert output_path.exists(), f"Output file {output_path} does not exist"
    
    with open(output_path, 'r') as f:
        data = json.load(f)  # This will raise if invalid JSON
    
    assert isinstance(data, dict), "Output should be a JSON object"
    return data

class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, json_data: dict, status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")
```

### Step 5: Create tests/fixtures/sample_transcript.json

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Sample Video Title",
  "language": "en",
  "segments": [
    {
      "text": "Hello everyone and welcome to this tutorial",
      "start": 0.0,
      "duration": 3.5
    },
    {
      "text": "Today we're going to learn about machine learning",
      "start": 3.5,
      "duration": 4.2
    },
    {
      "text": "Machine learning is a subset of artificial intelligence",
      "start": 7.7,
      "duration": 4.8
    },
    {
      "text": "It allows computers to learn without being explicitly programmed",
      "start": 12.5,
      "duration": 5.1
    }
  ]
}
```

### Step 6: Create tests/unit/test_smoke.py

```python
"""Smoke tests to verify basic functionality."""

import pytest
from mindtube.core.config import MindTubeConfig

def test_import_mindtube():
    """Test that mindtube package can be imported."""
    import mindtube
    assert mindtube is not None

def test_config_creation(mock_config):
    """Test that configuration can be created."""
    assert isinstance(mock_config, MindTubeConfig)
    assert mock_config.azure_openai_endpoint == "https://test.openai.azure.com/"

def test_project_structure():
    """Test that expected project structure exists."""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    
    # Check main package structure
    assert (project_root / "mindtube" / "__init__.py").exists()
    assert (project_root / "mindtube" / "core" / "__init__.py").exists()
    assert (project_root / "mindtube" / "models" / "__init__.py").exists()
    assert (project_root / "mindtube" / "adapters" / "__init__.py").exists()
    
    # Check configuration files
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "Makefile").exists()

@pytest.mark.unit
def test_basic_functionality():
    """Test basic functionality works."""
    # This is a placeholder for actual functionality tests
    assert 1 + 1 == 2

@pytest.mark.integration
def test_integration_placeholder():
    """Placeholder for integration tests."""
    pytest.skip("Integration tests not yet implemented")
```

### Step 7: Update Makefile Test Target

Ensure the Makefile has proper test targets:

```makefile
test: ## Run all tests
	python -m pytest

test-unit: ## Run unit tests only
	python -m pytest tests/unit/ -m "not slow"

test-integration: ## Run integration tests
	python -m pytest tests/integration/

test-coverage: ## Run tests with coverage report
	python -m pytest --cov=mindtube --cov-report=html

test-fast: ## Run fast tests only (skip slow and external)
	python -m pytest -m "not slow and not external"
```

## Implementation Steps

### Step 1: Install Test Dependencies
Update pyproject.toml with test dependencies:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "coverage>=7.0.0",
]
```

### Step 2: Create Test Structure
Set up the complete test directory structure with proper __init__.py files.

### Step 3: Configure pytest
Create pytest.ini with appropriate settings for the project.

### Step 4: Add Test Fixtures
Create reusable test fixtures and utilities.

### Step 5: Implement Smoke Tests
Create basic tests to verify the project structure and imports work.

### Step 6: Verify Test Execution
Run tests to ensure everything is working:
```bash
make install-dev-deps
make test
```

## Testing

### Run All Tests
```bash
make test
```

### Run Specific Test Categories
```bash
make test-unit
make test-integration
make test-fast
```

### Generate Coverage Report
```bash
make test-coverage
open htmlcov/index.html  # View coverage report
```

## Common Issues

### Issue 1: Import Errors
**Problem**: Tests fail due to import errors
**Solution**: Ensure PYTHONPATH includes project root, or install package in development mode

### Issue 2: Configuration Errors in Tests
**Problem**: Tests fail due to missing environment variables
**Solution**: Use mock_config fixture and proper environment setup

### Issue 3: Slow Test Execution
**Problem**: Tests take too long to run
**Solution**: Use test markers to categorize and skip slow tests during development