# TASK-003: Core Dependencies Configuration

## Task Information
- **ID**: TASK-003
- **Phase**: 0 - Project Foundation
- **Estimate**: 30 minutes
- **Dependencies**: TASK-002
- **Status**: 🟢 Done

## Description
Configure all required dependencies in pyproject.toml with proper version constraints and optional dependency groups. This ensures consistent and reliable dependency management across different environments.

## Acceptance Criteria
- [x] Add youtube-transcript-api dependency
- [x] Add openai dependency for Azure OpenAI
- [x] Add typer[all] for CLI
- [x] Add pydantic for data validation
- [x] Add pytest, ruff, mypy for development
- [x] Add fastapi, uvicorn for API
- [x] Verify all dependencies install correctly
- [x] Add proper version constraints
- [x] Configure optional dependency groups

## Dependencies Configuration

### Step 1: Update pyproject.toml Dependencies Section

Replace the empty dependencies section in `pyproject.toml` with:

```toml
dependencies = [
    # Core dependencies
    "youtube-transcript-api>=0.6.0,<1.0.0",
    "openai>=1.0.0,<2.0.0",
    "typer[all]>=0.9.0,<1.0.0",
    "pydantic>=2.0.0,<3.0.0",
    "requests>=2.28.0,<3.0.0",
    "python-dotenv>=1.0.0,<2.0.0",
    "pyyaml>=6.0.0,<7.0.0",
    "rich>=13.0.0,<14.0.0",
    "aiofiles>=23.0.0,<24.0.0",
    "httpx>=0.24.0,<1.0.0",
]

[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.4.0,<8.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-asyncio>=0.21.0,<1.0.0",
    "pytest-mock>=3.11.0,<4.0.0",
    "pytest-xdist>=3.3.0,<4.0.0",
    
    # Code quality
    "ruff>=0.1.0,<1.0.0",
    "mypy>=1.5.0,<2.0.0",
    "black>=23.7.0,<24.0.0",
    "isort>=5.12.0,<6.0.0",
    
    # Development tools
    "pre-commit>=3.3.0,<4.0.0",
    "ipython>=8.14.0,<9.0.0",
    "ipdb>=0.13.0,<1.0.0",
    
    # Security
    "safety>=2.3.0,<3.0.0",
    "bandit>=1.7.0,<2.0.0",
]

api = [
    # Web framework
    "fastapi>=0.103.0,<1.0.0",
    "uvicorn[standard]>=0.23.0,<1.0.0",
    
    # WebSocket support
    "websockets>=11.0.0,<12.0.0",
    
    # Rate limiting
    "slowapi>=0.1.9,<1.0.0",
    
    # File uploads
    "python-multipart>=0.0.6,<1.0.0",
    
    # CORS
    "python-cors>=1.7.0,<2.0.0",
]

whisper = [
    # ASR capabilities
    "faster-whisper>=0.9.0,<1.0.0",
    "yt-dlp>=2023.7.6",
    
    # Audio processing
    "librosa>=0.10.0,<1.0.0",
    "soundfile>=0.12.0,<1.0.0",
]

docs = [
    # Documentation generation
    "mkdocs>=1.5.0,<2.0.0",
    "mkdocs-material>=9.2.0,<10.0.0",
    "mkdocs-mermaid2-plugin>=1.1.0,<2.0.0",
    
    # API documentation
    "mkdocs-swagger-ui-tag>=0.6.0,<1.0.0",
]

performance = [
    # Profiling and monitoring
    "py-spy>=0.3.14,<1.0.0",
    "memory-profiler>=0.61.0,<1.0.0",
    "line-profiler>=4.1.0,<5.0.0",
    
    # Async improvements
    "uvloop>=0.17.0,<1.0.0; sys_platform != 'win32'",
]

all = [
    # Include all optional dependencies
    "mindtube[dev,api,whisper,docs,performance]",
]
```

### Step 2: Add Type Checking Configuration

Add mypy configuration to pyproject.toml:

```toml
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
show_error_codes = true

# Per-module options
[[tool.mypy.overrides]]
module = [
    "youtube_transcript_api.*",
    "yt_dlp.*",
    "faster_whisper.*",
    "librosa.*",
    "soundfile.*",
]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### Step 3: Update Ruff Configuration

Enhance the ruff configuration in pyproject.toml:

```toml
[tool.ruff]
target-version = "py38"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "N",   # pep8-naming
    "S",   # flake8-bandit
    "T20", # flake8-print
    "SIM", # flake8-simplify
    "ARG", # flake8-unused-arguments
    "PTH", # flake8-use-pathlib
    "ERA", # eradicate
    "PL",  # pylint
    "RUF", # ruff-specific rules
]
ignore = [
    "E501",   # line too long, handled by black
    "B008",   # do not perform function calls in argument defaults
    "C901",   # too complex
    "S101",   # use of assert
    "S603",   # subprocess call: check for execution of untrusted input
    "S607",   # starting a process with a partial executable path
    "PLR0913", # too many arguments to function call
    "PLR0912", # too many branches
    "PLR0915", # too many statements
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401", "F403"]
"tests/**/*" = ["B011", "S101", "ARG001", "ARG002"]
"scripts/**/*" = ["T20"]

[tool.ruff.isort]
known-first-party = ["mindtube"]
force-sort-within-sections = true
```

### Step 4: Update Black Configuration

Add black configuration to pyproject.toml:

```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### Step 5: Update isort Configuration

Add isort configuration to pyproject.toml:

```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["mindtube"]
known_third_party = [
    "youtube_transcript_api",
    "openai",
    "typer",
    "pydantic",
    "fastapi",
    "uvicorn",
    "pytest",
    "rich",
]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

### Step 6: Update Coverage Configuration

Enhance coverage configuration in pyproject.toml:

```toml
[tool.coverage.run]
source = ["mindtube"]
omit = [
    "tests/*",
    "mindtube/__main__.py",
    "*/migrations/*",
    "*/venv/*",
    "*/.venv/*",
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "def __str__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
show_missing = true
precision = 2
skip_covered = false
skip_empty = false

[tool.coverage.html]
directory = "htmlcov"

[tool.coverage.xml]
output = "coverage.xml"
```

### Step 7: Add Bandit Security Configuration

Add bandit configuration to pyproject.toml:

```toml
[tool.bandit]
exclude_dirs = ["tests", "build", "dist"]
skips = ["B101", "B601"]  # Skip assert_used and shell_injection_process_args
```

## Implementation Steps

### Step 1: Backup Current pyproject.toml
```bash
cp pyproject.toml pyproject.toml.backup
```

### Step 2: Update pyproject.toml
Replace the dependencies and tool configurations with the enhanced versions above.

### Step 3: Test Core Dependencies Installation
```bash
# Activate virtual environment
source .venv/bin/activate

# Install core dependencies
make install-deps

# Verify installation
python -c "import youtube_transcript_api; print('✅ YouTube Transcript API')"
python -c "import openai; print('✅ OpenAI')"
python -c "import typer; print('✅ Typer')"
python -c "import pydantic; print('✅ Pydantic')"
```

### Step 4: Test Development Dependencies
```bash
# Install development dependencies
make install-dev-deps

# Verify installation
python -c "import pytest; print('✅ Pytest')"
python -c "import ruff; print('✅ Ruff')"
python -c "import mypy; print('✅ MyPy')"
```

### Step 5: Test Optional Dependencies
```bash
# Install API dependencies
make install-api-deps

# Verify installation
python -c "import fastapi; print('✅ FastAPI')"
python -c "import uvicorn; print('✅ Uvicorn')"

# Install Whisper dependencies (optional)
make install-whisper-deps

# Verify installation
python -c "import faster_whisper; print('✅ Faster Whisper')"
```

## Verification Steps

### Step 1: Validate pyproject.toml Syntax
```bash
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
```

### Step 2: Check Dependency Resolution
```bash
pip check
```

### Step 3: Test Tool Configurations
```bash
# Test ruff configuration
python -m ruff check --config pyproject.toml .

# Test mypy configuration  
python -m mypy --config-file pyproject.toml mindtube/ || true

# Test black configuration
python -m black --check --config pyproject.toml mindtube/ || true
```

### Step 4: Verify Version Constraints
```bash
pip list | grep -E "(youtube-transcript-api|openai|typer|pydantic|fastapi)"
```

## Success Criteria Checklist

- [x] All core dependencies added with proper version constraints
- [x] Development dependencies configured correctly
- [x] Optional dependency groups (api, whisper, docs, performance) defined
- [x] Tool configurations (mypy, ruff, black, isort) updated
- [x] Coverage and security configurations added
- [x] `make install-deps` installs core dependencies without conflicts
- [x] `make install-dev-deps` installs development tools successfully
- [x] `make install-api-deps` installs FastAPI stack correctly
- [x] `make install-whisper-deps` installs ASR dependencies
- [x] `pip check` passes without dependency conflicts
- [x] All tool configurations are valid and functional

## Dependency Rationale

### Core Dependencies
- **youtube-transcript-api**: Primary transcript extraction
- **openai**: Azure OpenAI integration
- **typer**: Modern CLI framework with rich features
- **pydantic**: Data validation and serialization
- **requests/httpx**: HTTP client libraries
- **python-dotenv**: Environment variable management
- **rich**: Enhanced terminal output

### Development Dependencies
- **pytest**: Testing framework with async support
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checking
- **black**: Code formatting
- **isort**: Import sorting
- **pre-commit**: Git hooks for quality checks

### API Dependencies
- **fastapi**: Modern web framework
- **uvicorn**: ASGI server
- **websockets**: Real-time communication
- **slowapi**: Rate limiting

### Whisper Dependencies
- **faster-whisper**: Efficient ASR implementation
- **yt-dlp**: YouTube audio extraction
- **librosa**: Audio processing

## Version Constraints Strategy

- **Major version pinning**: Prevent breaking changes (e.g., `<2.0.0`)
- **Minor version flexibility**: Allow feature updates (e.g., `>=1.5.0`)
- **Security updates**: Ensure latest patches within constraints
- **Compatibility**: Maintain Python 3.8+ support

## Next Steps

After completing this task:
1. Move to **TASK-004: Configuration System**
2. Update task status to 🟢 Done
3. Commit the updated pyproject.toml
4. Test dependency installation in clean environment

## Notes

- Version constraints balance stability and security
- Optional dependencies allow minimal installations
- Tool configurations enforce consistent code quality
- All dependencies are actively maintained and secure

## Troubleshooting

**Issue**: Dependency conflicts during installation
**Solution**: Check version constraints and update conflicting packages

**Issue**: Tool configuration errors
**Solution**: Validate TOML syntax and tool-specific settings

**Issue**: Missing system dependencies for some packages
**Solution**: Install system-level dependencies (e.g., for audio processing)

**Issue**: Slow dependency installation
**Solution**: Use pip cache and consider using uv for faster installs