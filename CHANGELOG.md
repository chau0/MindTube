# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete project restructure from MindTube to ytnote
- Comprehensive CLI interface with typer and rich
- Configuration management with pydantic-settings and .env support
- Modular package structure: cli, core, io, llm, models, qa modules
- CLI commands: fetch, summarize, ideas, takeaways, process, config
- Environment-based configuration with validation
- Proxy support for YouTube and API access
- Development tooling improvements with additional Makefile targets
- Data directory structure for video artifacts

### Changed
- Project name changed from MindTube to ytnote
- Package structure reorganized following planned architecture
- Dependencies updated to include typer, rich, pydantic-settings, youtube-transcript-api
- Makefile enhanced with lint, format, setup, and run targets

### Removed
- Old mindtube package structure
- Placeholder foo.py module

## [0.0.1] - 2025-01-30

### Added
- Initial project setup with uv dependency management
- Basic Python package structure
- Testing framework with pytest
- Code quality tools: ruff, mypy, pre-commit
- CI/CD configuration
- Documentation structure
