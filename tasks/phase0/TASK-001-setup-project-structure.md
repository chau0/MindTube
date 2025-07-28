# TASK-001: Project Structure Setup

## Task Information
- **ID**: TASK-001
- **Phase**: 0 - Project Foundation
- **Estimate**: 30 minutes
- **Dependencies**: None
- **Status**: 🔴 Backlog

## Description
Create the basic project directory structure and configuration files according to the design document specifications. This establishes the foundation for all subsequent development work.

## Acceptance Criteria
- [ ] Create directory structure as per design document
- [ ] Initialize pyproject.toml with basic metadata
- [ ] Create .gitignore file
- [ ] Create README.md skeleton
- [ ] Verify structure matches design document

## Directory Structure to Create
```
mindtube/
├── mindtube/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── video.py
│   │   ├── transcript.py
│   │   ├── analysis.py
│   │   └── errors.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── youtube.py
│   │   ├── azure_openai.py
│   │   ├── cache.py
│   │   └── storage.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── validation.py
│   │   ├── transcript.py
│   │   ├── analysis.py
│   │   └── output.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── commands.py
│   │   └── utils.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── endpoints.py
│   │   ├── websocket.py
│   │   └── middleware.py
│   └── cache/
│       ├── __init__.py
│       ├── manager.py
│       ├── filesystem.py
│       └── memory.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_core.py
│   │   ├── test_models.py
│   │   ├── test_adapters.py
│   │   ├── test_pipeline.py
│   │   ├── test_cli.py
│   │   └── test_api.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_youtube_integration.py
│   │   ├── test_azure_integration.py
│   │   ├── test_pipeline_integration.py
│   │   └── test_api_integration.py
│   ├── e2e/
│   │   ├── __init__.py
│   │   └── test_workflows.py
│   ├── performance/
│   │   ├── __init__.py
│   │   └── test_load.py
│   └── fixtures/
│       ├── __init__.py
│       ├── sample_transcripts.json
│       ├── sample_responses.json
│       └── test_videos.json
├── docs/
│   ├── api/
│   ├── cli/
│   └── examples/
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── Makefile
├── .gitignore
├── .env.example
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## Implementation Steps

### Step 1: Create Root Directory Structure
```bash
mkdir -p mindtube
cd mindtube
mkdir -p mindtube/{core,models,adapters,pipeline,cli,api,cache}
mkdir -p tests/{unit,integration,e2e,performance,fixtures}
mkdir -p docs/{api,cli,examples}
mkdir -p scripts
mkdir -p .github/workflows
```

### Step 2: Create __init__.py Files
Create empty `__init__.py` files in all Python package directories:
```bash
touch mindtube/__init__.py
touch mindtube/{core,models,adapters,pipeline,cli,api,cache}/__init__.py
touch tests/__init__.py
touch tests/{unit,integration,e2e,performance,fixtures}/__init__.py
```

### Step 3: Create pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mindtube"
version = "0.1.0"
description = "YouTube Learning Assistant - Extract transcripts, summaries, and mindmaps from YouTube videos"
readme = "README.md"
license = "MIT"
authors = [
    {name = "MindTube Team", email = "team@mindtube.dev"},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Education",
    "Topic :: Multimedia :: Video",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
keywords = ["youtube", "transcript", "summary", "mindmap", "ai", "learning"]
requires-python = ">=3.8"

dependencies = [
    # Core dependencies - will be populated in TASK-003
]

[project.optional-dependencies]
dev = [
    # Development dependencies - will be populated in TASK-003
]
api = [
    # API dependencies - will be populated in TASK-003
]
whisper = [
    # Whisper ASR dependencies - will be populated in TASK-003
]

[project.urls]
Homepage = "https://github.com/mindtube/mindtube"
Documentation = "https://mindtube.readthedocs.io"
Repository = "https://github.com/mindtube/mindtube"
"Bug Tracker" = "https://github.com/mindtube/mindtube/issues"

[project.scripts]
mindtube = "mindtube.cli.main:app"

[tool.hatch.build.targets.wheel]
packages = ["mindtube"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=mindtube",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "performance: Performance tests",
    "slow: Slow running tests",
]

[tool.coverage.run]
source = ["mindtube"]
omit = [
    "tests/*",
    "mindtube/__main__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

[tool.ruff]
target-version = "py38"
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*" = ["B011"]

[tool.mypy]
python_version = "3.8"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
strict_equality = true
```

### Step 4: Create .gitignore
```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/

# VS Code
.vscode/

# MindTube specific
.mindtube/
mindtube_cache/
*.mindtube
output/
logs/

# Temporary files
tmp_*
temp_*
*.tmp
*.temp

# OS specific
.DS_Store
Thumbs.db

# Docker
.dockerignore
```

### Step 5: Create README.md Skeleton
```markdown
# MindTube - YouTube Learning Assistant

A CLI tool and API for extracting transcripts, summaries, key ideas, and mindmaps from YouTube videos.

## Features

- 📝 **Transcript Extraction**: Automatic retrieval of video transcripts
- 📄 **Content Summarization**: AI-powered summarization of video content  
- 💡 **Key Ideas Extraction**: Identification of main concepts and takeaways
- 🗺️ **Mindmap Generation**: Visual representation in Mermaid format
- 🔧 **Multiple Interfaces**: CLI tool and REST API
- 💾 **Smart Caching**: Efficient storage and retrieval of processed content

## Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install mindtube

# Or install from source
git clone https://github.com/mindtube/mindtube.git
cd mindtube
make install-deps
```

### Configuration

```bash
# Set up Azure OpenAI credentials
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key"

# Or create config file
mindtube config init
```

### Usage

```bash
# Analyze a YouTube video
mindtube analyze https://youtu.be/VIDEO_ID

# Generate summary only
mindtube summarize https://youtu.be/VIDEO_ID

# Create mindmap
mindtube mindmap https://youtu.be/VIDEO_ID --save mindmap.md
```

## Development

### Setup

```bash
make init
make install-deps
make install-dev-deps
```

### Testing

```bash
make test
make lint
make typecheck
```

### API Server

```bash
make serve
```

## Documentation

- [CLI Guide](docs/cli/)
- [API Reference](docs/api/)
- [Configuration](docs/configuration.md)
- [Examples](docs/examples/)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for transcript extraction
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) for AI capabilities
- [Typer](https://typer.tiangolo.com/) for the CLI framework
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
```

### Step 6: Create .env.example
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo

# MindTube Configuration
MINDTUBE_CACHE_DIR=~/.mindtube/cache
MINDTUBE_LOG_LEVEL=INFO
MINDTUBE_MAX_WORKERS=4

# API Configuration (optional)
MINDTUBE_API_HOST=0.0.0.0
MINDTUBE_API_PORT=8000
MINDTUBE_API_RELOAD=false
```

## Verification Steps

### Step 1: Verify Directory Structure
```bash
find . -type d | sort
```
Expected output should match the directory structure above.

### Step 2: Verify Python Package Structure
```bash
find . -name "__init__.py" | sort
```
Should show all package `__init__.py` files.

### Step 3: Verify Configuration Files
```bash
ls -la | grep -E "\.(toml|md|gitignore|env)"
```
Should show: `pyproject.toml`, `README.md`, `.gitignore`, `.env.example`

### Step 4: Test pyproject.toml Syntax
```bash
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
```
Should run without errors (Python 3.11+) or use `pip install tomli` for older versions.

## Success Criteria Checklist

- [ ] All directories created according to design document
- [ ] All `__init__.py` files in place
- [ ] `pyproject.toml` created with proper metadata and tool configuration
- [ ] `.gitignore` covers all relevant file types
- [ ] `README.md` provides clear project overview and setup instructions
- [ ] `.env.example` shows required environment variables
- [ ] Directory structure verified with commands above
- [ ] No syntax errors in configuration files

## Next Steps

After completing this task:
1. Move to **TASK-002: Makefile Implementation**
2. Update task status to 🟢 Done
3. Commit initial project structure to version control

## Notes

- This structure follows Python packaging best practices
- All paths are relative to project root
- Configuration supports both development and production environments
- Test structure supports multiple testing strategies (unit, integration, e2e, performance)
- Documentation structure supports comprehensive project documentation

## Troubleshooting

**Issue**: Permission denied when creating directories
**Solution**: Ensure you have write permissions in the target directory

**Issue**: Python import errors
**Solution**: Ensure all `__init__.py` files are created

**Issue**: pyproject.toml syntax errors  
**Solution**: Validate TOML syntax using online validator or Python tomllib