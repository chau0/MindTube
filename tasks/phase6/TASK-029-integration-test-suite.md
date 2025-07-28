# TASK-029: Integration Test Suite

## Task Information
- **ID**: TASK-029
- **Phase**: 6 - Testing & Quality Assurance
- **Estimate**: 90 minutes
- **Dependencies**: TASK-028
- **Status**: 🔴 Backlog

## Description
Create comprehensive integration tests that verify end-to-end functionality with real external services and complete workflows. These tests ensure that all components work together correctly in realistic scenarios.

## Acceptance Criteria
- [ ] Test YouTube transcript extraction with real videos
- [ ] Test Azure OpenAI integration with actual API calls
- [ ] Test end-to-end CLI workflows
- [ ] Test API endpoints with full request/response cycles
- [ ] Add test data management and cleanup
- [ ] Create CI/CD test pipeline configuration
- [ ] Implement test environment isolation

## Implementation Details

### Test Categories

#### 1. External Service Integration
```python
# tests/integration/test_youtube_integration.py
@pytest.mark.integration
@pytest.mark.slow
def test_real_youtube_transcript_extraction():
    """Test with actual YouTube video (use stable, public video)"""
    video_id = "dQw4w9WgXcQ"  # Rick Roll - stable public video
    adapter = YouTubeAdapter()
    transcript = adapter.get_transcript(video_id)
    
    assert transcript is not None
    assert len(transcript.segments) > 0
    assert all(segment.text.strip() for segment in transcript.segments)
```

#### 2. Azure OpenAI Integration
```python
# tests/integration/test_azure_openai_integration.py
@pytest.mark.integration
@pytest.mark.requires_api_key
def test_azure_openai_summarization():
    """Test actual Azure OpenAI API integration"""
    if not os.getenv('AZURE_OPENAI_API_KEY'):
        pytest.skip("Azure OpenAI API key not configured")
    
    adapter = AzureOpenAIAdapter()
    sample_text = load_fixture('sample_transcript.txt')
    summary = adapter.summarize(sample_text)
    
    assert summary is not None
    assert len(summary) < len(sample_text)
    assert isinstance(summary, str)
```

#### 3. End-to-End CLI Workflows
```python
# tests/integration/test_cli_e2e.py
from typer.testing import CliRunner
from mindtube.cli.main import app

@pytest.mark.integration
def test_cli_analyze_command_e2e():
    """Test complete analyze command workflow"""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        result = runner.invoke(app, [
            'analyze', 
            'https://youtu.be/dQw4w9WgXcQ',
            '--save',
            '--format', 'markdown'
        ])
        
        assert result.exit_code == 0
        assert 'Summary:' in result.stdout
        assert 'Key Ideas:' in result.stdout
        
        # Check that files were created
        assert Path('artifacts').exists()
        markdown_files = list(Path('artifacts').glob('*.md'))
        assert len(markdown_files) > 0
```

#### 4. API Integration Tests
```python
# tests/integration/test_api_e2e.py
import httpx
import pytest
from fastapi.testclient import TestClient
from mindtube.api.app import app

@pytest.mark.integration
def test_api_analyze_endpoint_e2e():
    """Test complete API workflow"""
    client = TestClient(app)
    
    response = client.post('/analyze', json={
        'url': 'https://youtu.be/dQw4w9WgXcQ',
        'options': {
            'include_summary': True,
            'include_mindmap': True,
            'format': 'markdown'
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert 'summary' in data
    assert 'mindmap' in data
    assert data['status'] == 'completed'
```

### Test Environment Configuration

#### Environment Variables
```bash
# .env.test
YOUTUBE_API_KEY=test_key_or_real_key
AZURE_OPENAI_API_KEY=test_key_or_real_key
AZURE_OPENAI_ENDPOINT=https://test.openai.azure.com/
TEST_CACHE_DIR=/tmp/mindtube_test_cache
TEST_ARTIFACTS_DIR=/tmp/mindtube_test_artifacts
```

#### Test Markers
```python
# pytest.ini
[tool:pytest]
markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
    slow: marks tests as slow (deselect with '-m "not slow"')
    requires_api_key: marks tests that require API keys
    requires_network: marks tests that require network access
```

### Test Data Management

#### Fixture Data
```python
# tests/integration/fixtures/
├── stable_videos.json          # List of stable YouTube videos for testing
├── sample_transcripts/         # Pre-downloaded transcript samples
├── expected_outputs/           # Golden files for comparison
└── test_configurations/        # Various config scenarios
```

#### Data Cleanup
```python
# tests/integration/conftest.py
@pytest.fixture(autouse=True)
def cleanup_test_artifacts():
    """Automatically clean up test artifacts after each test"""
    yield
    # Cleanup logic
    if Path(TEST_ARTIFACTS_DIR).exists():
        shutil.rmtree(TEST_ARTIFACTS_DIR)
    if Path(TEST_CACHE_DIR).exists():
        shutil.rmtree(TEST_CACHE_DIR)
```

### CI/CD Integration

#### GitHub Actions Workflow
```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        make install-deps
        make install-dev-deps
    
    - name: Run integration tests (without API keys)
      run: |
        pytest tests/integration -m "not requires_api_key" -v
    
    - name: Run API integration tests
      if: github.event_name == 'push' && github.ref == 'refs/heads/main'
      env:
        AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
        AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
      run: |
        pytest tests/integration -m "requires_api_key" -v
```

### Test Scenarios

#### Happy Path Scenarios
1. **Complete Video Analysis**
   - Valid YouTube URL → Transcript → Summary → Mindmap → Save
2. **CLI Command Chain**
   - Multiple commands in sequence with shared cache
3. **API Workflow**
   - Authentication → Request → Processing → Response

#### Error Scenarios
1. **Network Issues**
   - Timeout handling
   - Connection failures
   - Rate limiting responses
2. **Invalid Inputs**
   - Malformed URLs
   - Private videos
   - Non-existent videos
3. **Service Failures**
   - YouTube API errors
   - Azure OpenAI failures
   - File system issues

#### Performance Scenarios
1. **Large Transcript Processing**
   - Videos with >1 hour content
   - Memory usage monitoring
2. **Concurrent Requests**
   - Multiple API calls simultaneously
   - Cache contention handling

## Test Execution Strategy

### Local Development
```bash
# Run all integration tests
make test-integration

# Run only fast integration tests
pytest tests/integration -m "not slow"

# Run with API keys (if available)
pytest tests/integration -m "requires_api_key"
```

### CI Environment
- Run basic integration tests on every PR
- Run full integration tests (with API keys) on main branch
- Generate test reports and coverage
- Store test artifacts for debugging

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Integration tests cover all major workflows
- [ ] Tests pass consistently in CI environment
- [ ] Test data management implemented
- [ ] Error scenarios properly tested
- [ ] Performance baselines established
- [ ] Documentation updated with test procedures