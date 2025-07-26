# MindTube MVP

**AI-Powered YouTube Video Summarizer**

Transform long YouTube videos into concise, actionable insights with timestamped summaries, key ideas, and takeaways.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- YouTube Data API key
- OpenAI API key (or other LLM provider)

### Development Setup

1. **Clone and setup environment**
```bash
git clone <repo-url>
cd mindtube
cp .env.example .env
# Edit .env with your API keys
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

3. **Frontend Setup**
```bash
cd frontend
npm install
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

### Running Tests
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd frontend && npm test
```

### Code Quality
```bash
# Backend linting
cd backend && black . && flake8 .

# Frontend linting
cd frontend && npm run lint
```

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