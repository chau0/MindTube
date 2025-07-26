# MindTube MVP

**AI-Powered YouTube Video Summarizer**

Transform long YouTube videos into concise, actionable insights with timestamped summaries, key ideas, and takeaways.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- YouTube Data API key
- OpenAI API key (or other LLM provider)

### Development Setup

1. **Clone and setup environment**
```bash
git clone <repo-url>
cd mindtube
```

2. **Automated Setup (Recommended)**
```bash
# This will setup both backend and frontend automatically
./scripts/dev.sh
```

3. **Manual Setup**

**Backend Setup:**
```bash
cd backend
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment and dependencies
make setup

# Edit environment file with your API keys
cp .env.example .env
# Edit .env with your API keys

# Start backend server
make run
```

**Frontend Setup:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
mindtube/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Core business logic
│   │   ├── models/    # Data models
│   │   └── services/  # External services
│   ├── tests/
│   └── requirements.txt
├── frontend/          # Next.js frontend
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/# React components
│   │   ├── lib/       # Utilities
│   │   └── types/     # TypeScript types
│   ├── public/
│   └── package.json
├── docs/              # Documentation
└── scripts/           # Development scripts
```

## 🎯 MVP Features

- ✅ YouTube URL ingestion and validation
- ✅ Automatic transcript extraction (captions + ASR fallback)
- ✅ AI-powered summarization (short + detailed)
- ✅ Key ideas and actionable takeaways extraction
- ✅ Timestamped bullets with YouTube links
- ✅ Markdown export functionality
- ✅ Local processing history
- ✅ Progress tracking and error handling

## 🛠 Development

### Backend Development Commands

The backend uses a Makefile for common development tasks:

```bash
cd backend

# Setup and installation
make setup          # Initial setup with uv
make install        # Install production dependencies
make install-dev    # Install development dependencies

# Development
make run            # Start development server
make build          # Validate application build
make test           # Run tests
make test-cov       # Run tests with coverage
make lint           # Run linting (flake8, mypy, bandit)
make format         # Format code (black, isort)

# Maintenance
make update         # Update dependencies
make clean          # Clean cache and temporary files
make info           # Show environment information
```

### Frontend Development Commands

```bash
cd frontend

# Development
npm run dev         # Start development server
npm run build       # Build for production
npm run start       # Start production server

# Testing and Quality
npm test            # Run tests
npm run lint        # Run ESLint
npm run type-check  # TypeScript type checking
```

### Environment Files

The project now uses separate environment files:
- `backend/.env` - Backend configuration (API keys, database, etc.)
- `frontend/.env` - Frontend configuration (API endpoints, feature flags, etc.)

## 📊 Success Metrics (MVP)
- **Latency**: ≤15s for first summary (≤10min video with captions)
- **Completion Rate**: ≥95% jobs complete without retry
- **Quality**: ≥4/5 average on coverage/correctness/actionability
- **Cost**: ≤¥2-¥10 per 10-min video

## 🚦 Status

**Current Phase**: Phase 0 - Project Setup ✅  
**Next**: Phase 1 - UX Prototype & Flow  
**Target MVP Launch**: August 3, 2025

See [docs/mindtube_roadmap.md](docs/mindtube_roadmap.md) for detailed timeline.

## 📄 License

MIT License - see LICENSE file for details.