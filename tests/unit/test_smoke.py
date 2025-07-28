"""Smoke tests to verify basic functionality."""

import pytest
from pathlib import Path
from mindtube.core.config import MindTubeConfig


def test_import_mindtube():
    """Test that mindtube package can be imported."""
    import mindtube
    assert mindtube is not None


def test_import_core_modules():
    """Test that core modules can be imported."""
    from mindtube.core import config
    assert config is not None
    
    # Test that MindTubeConfig can be imported
    from mindtube.core.config import MindTubeConfig, get_config
    assert MindTubeConfig is not None
    assert get_config is not None


def test_config_creation(mock_config):
    """Test that configuration can be created."""
    assert isinstance(mock_config, MindTubeConfig)
    assert mock_config.azure_openai_endpoint == "https://test.openai.azure.com/"
    assert mock_config.azure_openai_api_key == "test-key"
    assert mock_config.cache_enabled is False  # Set in mock_config fixture
    assert mock_config.log_level == "DEBUG"


def test_project_structure():
    """Test that expected project structure exists."""
    project_root = Path(__file__).parent.parent.parent
    
    # Check main package structure
    assert (project_root / "mindtube" / "__init__.py").exists()
    assert (project_root / "mindtube" / "core" / "__init__.py").exists()
    assert (project_root / "mindtube" / "core" / "config.py").exists()
    assert (project_root / "mindtube" / "models" / "__init__.py").exists()
    assert (project_root / "mindtube" / "adapters" / "__init__.py").exists()
    assert (project_root / "mindtube" / "pipeline" / "__init__.py").exists()
    assert (project_root / "mindtube" / "cli" / "__init__.py").exists()
    assert (project_root / "mindtube" / "api" / "__init__.py").exists()
    assert (project_root / "mindtube" / "cache" / "__init__.py").exists()
    
    # Check configuration files
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "Makefile").exists()
    assert (project_root / ".env.example").exists()
    assert (project_root / ".gitignore").exists()


def test_test_structure():
    """Test that test structure is properly set up."""
    test_root = Path(__file__).parent.parent
    
    # Check test directories
    assert (test_root / "__init__.py").exists()
    assert (test_root / "conftest.py").exists()
    assert (test_root / "unit" / "__init__.py").exists()
    assert (test_root / "integration" / "__init__.py").exists()
    assert (test_root / "e2e" / "__init__.py").exists()
    assert (test_root / "fixtures" / "__init__.py").exists()
    assert (test_root / "utils" / "__init__.py").exists()
    
    # Check test fixtures
    assert (test_root / "fixtures" / "sample_transcript.json").exists()
    assert (test_root / "fixtures" / "sample_video_metadata.json").exists()
    assert (test_root / "fixtures" / "sample_analysis.json").exists()
    
    # Check test utilities
    assert (test_root / "utils" / "test_helpers.py").exists()


@pytest.mark.unit
def test_basic_functionality():
    """Test basic functionality works."""
    # Test basic Python operations
    assert 1 + 1 == 2
    assert "hello" + " world" == "hello world"
    
    # Test Path operations
    path = Path("/tmp/test")
    assert str(path) == "/tmp/test"


@pytest.mark.unit
def test_fixtures_loading():
    """Test that test fixtures can be loaded."""
    from tests.utils.test_helpers import load_test_fixture
    
    # Test loading sample transcript
    transcript = load_test_fixture("sample_transcript.json")
    assert isinstance(transcript, dict)
    assert "video_id" in transcript
    assert "segments" in transcript
    assert isinstance(transcript["segments"], list)
    
    # Test loading sample metadata
    metadata = load_test_fixture("sample_video_metadata.json")
    assert isinstance(metadata, dict)
    assert "video_id" in metadata
    assert "title" in metadata
    
    # Test loading sample analysis
    analysis = load_test_fixture("sample_analysis.json")
    assert isinstance(analysis, dict)
    assert "summary" in analysis
    assert "key_ideas" in analysis


@pytest.mark.unit
def test_test_helpers():
    """Test that test helper functions work."""
    from tests.utils.test_helpers import (
        create_mock_transcript_response,
        create_sample_transcript_segments,
        MockResponse
    )
    
    # Test create_mock_transcript_response
    segments = [{"text": "test", "start": 0.0, "duration": 1.0}]
    response = create_mock_transcript_response(segments)
    assert isinstance(response, dict)
    assert response["video_id"] == "test_video_id"
    assert response["segments"] == segments
    
    # Test create_sample_transcript_segments
    sample_segments = create_sample_transcript_segments(3)
    assert isinstance(sample_segments, list)
    assert len(sample_segments) == 3
    assert all("text" in seg for seg in sample_segments)
    assert all("start" in seg for seg in sample_segments)
    assert all("duration" in seg for seg in sample_segments)
    
    # Test MockResponse
    mock_resp = MockResponse({"test": "data"}, 200)
    assert mock_resp.status_code == 200
    assert mock_resp.json() == {"test": "data"}
    assert mock_resp.ok is True


@pytest.mark.unit
def test_path_utilities(temp_dir):
    """Test path utilities work with temporary directories."""
    # Test that temp_dir fixture works
    assert isinstance(temp_dir, Path)
    assert temp_dir.exists()
    assert temp_dir.is_dir()
    
    # Test creating files in temp directory
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
    assert test_file.read_text() == "test content"


@pytest.mark.integration
def test_integration_placeholder():
    """Placeholder for integration tests."""
    pytest.skip("Integration tests not yet implemented")


@pytest.mark.slow  
def test_slow_placeholder():
    """Placeholder for slow tests."""
    pytest.skip("Slow tests not yet implemented")


@pytest.mark.external
def test_external_placeholder():
    """Placeholder for external service tests."""
    pytest.skip("External service tests not yet implemented")