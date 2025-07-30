# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MindTube is a Python tool for downloading YouTube captions and generating summaries. The project is built using modern Python tooling with `uv` for dependency management and package building.

## Development Commands

### Environment Setup
```bash
make install  # Install virtual environment and pre-commit hooks
```

### Code Quality and Testing
```bash
make check    # Run all code quality checks (linting, type checking)
make test     # Run pytest with coverage and doctests
uv run pre-commit run -a  # Run pre-commit hooks manually
uv run mypy   # Run type checking only
```

### Building
```bash
make build    # Build wheel file (cleans artifacts first)
```

## Project Structure

- **Source code**: Located in `src/mindtube/`
- **Tests**: Located in `tests/` directory
- **Package management**: Uses `uv` with `pyproject.toml` configuration
- **Build system**: Uses `hatchling` backend

## Development Environment

- **Python versions**: Supports 3.9 to 3.13
- **Dependency manager**: `uv` (not pip/poetry)
- **Linting**: Ruff with extensive rule set (120 char line length)
- **Type checking**: mypy with strict configuration
- **Testing**: pytest with doctest modules and coverage
- **Pre-commit**: Configured with hooks for code quality

## Testing

- Run single test file: `uv run python -m pytest tests/test_specific.py`
- Run with coverage: `uv run python -m pytest --cov`
- Tests include both unit tests and doctests from modules

## Configuration Notes

- Ruff is configured with strict linting rules and 120 character line limit
- mypy enforces strict type checking (disallow_untyped_defs, etc.)
- Pre-commit hooks automatically format and check code
- Tox is configured for multi-version Python testing (3.9-3.13)
