# MindTube

> YouTube video transcript processing and summarization tool with LLM-powered analysis

[![CI](https://github.com/mindtube/mindtube/workflows/CI/badge.svg)](https://github.com/mindtube/mindtube/actions)
[![codecov](https://codecov.io/gh/mindtube/mindtube/branch/main/graph/badge.svg)](https://codecov.io/gh/mindtube/mindtube)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MindTube extracts captions/transcripts from YouTube videos, processes them through LLM-based map-reduce pipelines, and generates structured summaries, notes, and mindmaps.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Azure OpenAI API access
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/mindtube/mindtube.git
cd mindtube

# Set up development environment
make setup

# Copy and configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Run tests to verify setup
make test
```

### Basic Usage

```bash
# Process a YouTube video (CLI - coming in M1)
mindtube process "https://www.youtube.com/watch?v=VIDEO_ID"

# Start the API server (coming in M4)
make docker-up
```

## 📁 Project Structure

```
mindtube/
├── packages/core/mindtube/    # Core Python package
├── apps/cli/                  # Command-line interface
├── apps/api/                  # FastAPI backend
├── apps/web/                  # Next.js frontend
├── documents/                 # Project documentation
├── tests/                     # Test suites
└── data/                      # Local data storage
```

## 🛠️ Development

### Environment Setup

```bash
# Using VS Code Dev Containers (recommended)
# 1. Install Docker and VS Code with Dev Containers extension
# 2. Open project in VS Code
# 3. Click "Reopen in Container" when prompted

# Or manual setup
make setup
make dev
```

### Available Commands

```bash
make help          # Show all available commands
make test          # Run test suite
make lint          # Check code quality
make format        # Format code
make docker-up     # Start services
```

### Development Workflow

1. **Planning**: See `documents/plan/` for architecture and roadmap
2. **Current Work**: Check `documents/doing/` for active milestones
3. **Testing**: Follow TDD approach outlined in `documents/plan/tdd-playbook.md`
4. **Contributing**: Read `documents/agen_docs/docs/CONTRIBUTING.md`

## 🏗️ Architecture

MindTube follows a modular architecture:

- **Core Package**: Reusable transcript processing logic
- **CLI App**: Command-line interface for local use
- **API App**: FastAPI backend for web integration
- **Web App**: Next.js frontend for browser access

### Data Flow

```
YouTube URL → Transcript Extraction → Text Chunking → 
LLM Processing (Map/Reduce) → Export Generation → Caching
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit          # Fast unit tests
make test-integration   # Integration tests
make test-e2e          # End-to-end tests (requires real services)

# Coverage report
make test-cov
```

## 📊 Current Status

**Phase**: Planning and Repository Setup (M0)

### Milestones

- [x] **M0**: Repository scaffold & quality gates
- [ ] **M1**: Core pipeline implementation
- [ ] **M2**: LLM integration and processing
- [ ] **M3**: Export and caching systems
- [ ] **M4**: API development
- [ ] **M5**: Frontend development
- [ ] **M6**: Testing and hardening
- [ ] **M7**: Deployment and operations

See `documents/plan/roadmap.md` for detailed timeline.

## 🔧 Configuration

Key environment variables (see `.env.example`):

```bash
# Azure OpenAI (required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Database
DATABASE_URL=sqlite:///./data/mindtube.db

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0
```

## 📚 Documentation

- **[Design Document](documents/plan/design.md)**: System architecture
- **[Roadmap](documents/plan/roadmap.md)**: Development timeline
- **[TDD Playbook](documents/plan/tdd-playbook.md)**: Testing approach
- **[API Documentation](documents/agen_docs/docs/API_README.md)**: API contracts
- **[Agent Guide](documents/agen_docs/docs/AGENT_GUIDE.md)**: AI development assistance

## 🤝 Contributing

1. Read the [Contributing Guide](documents/agen_docs/docs/CONTRIBUTING.md)
2. Check current milestone in `documents/doing/`
3. Follow the TDD approach
4. Keep PRs small and focused (<150 LOC)
5. Ensure all tests pass and coverage ≥85%

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- YouTube Transcript API for transcript extraction
- Azure OpenAI for LLM processing
- The open-source community for excellent tools and libraries

---

**Status**: 🚧 Under Development | **Version**: 0.1.0 | **Python**: 3.12+