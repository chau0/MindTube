# MindTube Backend

FastAPI backend for AI-powered YouTube video summarization.

## Quick Start

### Option 1: Simplified Setup (Recommended for quick start)
If you don't have build tools installed or want to get started quickly:

```bash
make setup-simple
make run
```

This installs core dependencies without ML packages that require compilation (spaCy, Whisper).

### Option 2: Full Setup (Complete ML features)
For full functionality including NLP and speech-to-text features:

```bash
# Install build tools first (Ubuntu/Debian)
sudo apt update && sudo apt install build-essential

# Or for CentOS/RHEL/Fedora
sudo dnf groupinstall "Development Tools"

# Or for macOS
xcode-select --install

# Then run full setup
make setup
make run
```

## Setup Options

| Command | Description | Requirements | Features |
|---------|-------------|--------------|----------|
| `make setup-simple` | Quick setup without ML dependencies | None | Core API, database, HTTP clients |
| `make setup` | Full setup with all features | Build tools (gcc, g++, make) | Complete ML pipeline, spaCy, Whisper |

## Development

### Running the Server
```bash
make run
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Other Commands
```bash
make help           # Show all available commands
make test           # Run tests
make lint           # Run code linting
make format         # Format code
make clean          # Clean cache files
```

## Troubleshooting

### Build Errors (blis/spaCy compilation issues)
If you encounter compilation errors like "gcc not found" or "Failed to build blis":

1. **Quick fix**: Use `make setup-simple` to skip ML dependencies
2. **Complete fix**: Install build tools:
   ```bash
   # Ubuntu/Debian
   sudo apt install build-essential
   
   # CentOS/RHEL/Fedora
   sudo dnf groupinstall "Development Tools"
   
   # macOS
   xcode-select --install
   ```

### Upgrading from Simple to Full Setup
```bash
# Install build tools (see above)
make install-dev    # Install full dependencies
```

## Environment Configuration

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required for full functionality:
- `YOUTUBE_API_KEY`: YouTube Data API v3 key
- `OPENAI_API_KEY`: OpenAI API key for LLM processing

## Architecture

- **Framework**: FastAPI with async support
- **Database**: SQLite (development) / PostgreSQL (production)
- **ML Stack**: spaCy (NLP), Whisper (ASR), OpenAI GPT (summarization)
- **Task Queue**: Redis + ARQ for background processing
- **Package Manager**: uv for fast dependency management