# MindTube Project File Mapping
**Generated:** 2025-01-27  
**Total Files:** 383 (excluding .git directory)

## Project Overview
MindTube is a YouTube video transcript processing and summarization tool that extracts captions/transcripts from YouTube videos, processes them through LLM-based map-reduce pipelines, and generates structured summaries, notes, and mindmaps. The project follows a modular architecture with CLI, API, and web frontend components.

## Directory Structure & File Mapping

### 📁 Root Documentation (`docs/`)
Core project documentation and design specifications.

| File | Purpose | Category | Dependencies |
|------|---------|----------|--------------|
| `docs/README.md` | Main documentation index and quick start guide | Documentation | Links to all other docs |
| `docs/design.md` | Comprehensive system architecture and design document | Architecture | Core design reference |
| `docs/roadmap.md` | Development phases and timeline (CLI → API → Frontend) | Planning | References design.md |
| `docs/wbs.md` | Work Breakdown Structure with detailed tasks and DoD | Planning | References roadmap.md |
| `docs/tdd-playbook.md` | Test-driven development guidelines and practices | Development | Referenced by WBS |

### 📁 Agent Documentation (`agen_docs/`)
AI agent-specific documentation and contracts for development assistance.

#### Core Agent Files
| File | Purpose | Category | Dependencies |
|------|---------|----------|--------------|
| `agen_docs/P0_P1_manifest.json` | Manifest listing all agent documentation files | Configuration | Lists all agen_docs files |
| `agen_docs/openapi.yaml` | Complete API specification for MindTube API | API Contract | Referenced by API_README.md |

#### Agent Documentation (`agen_docs/docs/`)
| File | Purpose | Category | Dependencies |
|------|---------|----------|--------------|
| `agen_docs/docs/AGENT_GUIDE.md` | Rules and conventions for AI agent contributors | Guidelines | References other docs |
| `agen_docs/docs/API_README.md` | API contract overview and endpoint documentation | API Documentation | References openapi.yaml |
| `agen_docs/docs/CONTRIBUTING.md` | Contribution guidelines for developers | Development | - |
| `agen_docs/docs/COST_POLICY.md` | Token budgets and cost management policies | Operations | Referenced by AGENT_GUIDE.md |
| `agen_docs/docs/DATA_MODEL.md` | Database schema and data structure definitions | Architecture | References ddl.sql |
| `agen_docs/docs/ERRORS.md` | Error taxonomy and handling specifications | Development | Referenced by API_README.md |
| `agen_docs/docs/LOCAL_HISTORY.md` | Local development and history management | Development | - |
| `agen_docs/docs/OBSERVABILITY.md` | Logging, metrics, and monitoring specifications | Operations | Referenced by AGENT_GUIDE.md |
| `agen_docs/docs/PROMPTS.md` | LLM prompt templates and versioning | AI/ML | Referenced by design.md |
| `agen_docs/docs/QA_PLAN.md` | Quality assurance and testing strategy | Testing | - |
| `agen_docs/docs/RUNBOOK.md` | Operational procedures and troubleshooting | Operations | - |
| `agen_docs/docs/SECURITY.md` | Security guidelines and best practices | Security | - |
| `agen_docs/docs/TRANSCRIPT_POLICY.md` | YouTube ToS compliance and transcript handling | Compliance | Referenced by AGENT_GUIDE.md |

#### Data Schemas (`agen_docs/schemas/`)
| File | Purpose | Category | Dependencies |
|------|---------|----------|--------------|
| `agen_docs/schemas/map_schema.json` | JSON schema for map stage output validation | Data Schema | Used by pipeline.py |
| `agen_docs/schemas/reduce_schema.json` | JSON schema for reduce stage output validation | Data Schema | Used by pipeline.py |
| `agen_docs/schemas/validation_schema.json` | General validation schema definitions | Data Schema | Used across pipeline |

#### Database Schema (`agen_docs/sql/`)
| File | Purpose | Category | Dependencies |
|------|---------|----------|--------------|
| `agen_docs/sql/ddl.sql` | SQLite database schema for videos, runs, artifacts, metrics | Database | Referenced by cache.py |

### 📁 Work Breakdown Structure (`todo/`)
Detailed milestone-based task breakdowns for project phases.

| File | Purpose | Category | Dependencies |
|------|---------|----------|--------------|
| `todo/WBS_M0.md` | M0: Repository scaffold & quality gates | Planning | References tooling setup |
| `todo/WBS_M1.md` | M1: Core pipeline implementation | Planning | Depends on M0 |
| `todo/WBS_M2.md` | M2: LLM integration and processing | Planning | Depends on M1 |
| `todo/WBS_M3.md` | M3: Export and caching systems | Planning | Depends on M2 |
| `todo/WBS_M4.md` | M4: API development | Planning | Depends on M3 |
| `todo/WBS_M5.md` | M5: Frontend development | Planning | Depends on M4 |
| `todo/WBS_M6.md` | M6: Testing and hardening | Planning | Cross-milestone |
| `todo/WBS_M7.md` | M7: Deployment and operations | Planning | Final milestone |

### 📁 Development Notes (`notes/`)
Development best practices and workflow documentation.

| File | Purpose | Category | Dependencies |
|------|---------|----------|--------------|
| `notes/best_practice.md` | AI-assisted development best practices and tips | Development | - |
| `notes/workflow.md` | High-level development workflow outline | Development | - |

### 📁 External Documentation (`external_docs/`)
Third-party API documentation and integration guides.

| File | Purpose | Category | Dependencies |
|------|---------|----------|--------------|
| `external_docs/azure-ai.md` | OpenAI Python API library documentation for Azure integration | Integration | Referenced by llm/azure.py |
| `external_docs/youtube_api.md` | YouTube Transcript API documentation and usage examples | Integration | Referenced by yt.py |

## Planned Architecture (from design.md)

### 📁 Core Package Structure (Future)
```
packages/core/mindtube/
├── __init__.py          # Package initialization
├── config.py            # Configuration management
├── yt.py               # YouTube transcript fetching
├── asr.py              # ASR fallback processing
├── chunk.py            # Token-aware text chunking
├── llm/                # LLM provider abstractions
│   ├── __init__.py
│   ├── base.py         # Base LLM interface
│   ├── azure.py        # Azure OpenAI implementation
│   ├── openai.py       # OpenAI implementation
│   └── local.py        # Local model implementation
├── pipeline.py         # Main orchestration pipeline
├── prompts.py          # Prompt templates and versioning
├── export.py           # Output format exporters
├── cache.py            # SQLite caching and history
└── utils.py            # Utility functions
```

### 📁 Applications Structure (Future)
```
apps/
├── cli/                # Command-line interface
│   ├── mindtube_cli/
│   │   ├── __init__.py
│   │   └── main.py
│   └── pyproject.toml
├── api/                # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── models.py
│   │   ├── runners.py
│   │   ├── auth.py
│   │   ├── settings.py
│   │   └── static/
│   ├── pyproject.toml
│   └── Dockerfile
└── web/                # Next.js frontend
    ├── package.json
    ├── app/
    │   ├── page.tsx
    │   ├── runs/[id]/page.tsx
    │   ├── components/
    │   └── lib/api.ts
```

## File Relationships & Dependencies

### Documentation Flow
```
docs/README.md → docs/design.md → docs/roadmap.md → docs/wbs.md
                      ↓
                 todo/WBS_M*.md (milestone breakdowns)
```

### Agent Documentation Flow
```
agen_docs/P0_P1_manifest.json → lists all agen_docs files
agen_docs/docs/AGENT_GUIDE.md → references multiple policy docs
agen_docs/openapi.yaml → defines API contract
agen_docs/schemas/*.json → validate data structures
```

### Development Workflow
```
notes/workflow.md → high-level process
notes/best_practice.md → detailed guidelines
docs/tdd-playbook.md → testing approach
```

## Key Integration Points

### LLM Integration
- **Azure OpenAI**: Primary provider (external_docs/azure-ai.md)
- **Schemas**: map_schema.json, reduce_schema.json for output validation
- **Prompts**: Defined in agen_docs/docs/PROMPTS.md

### YouTube Integration
- **API**: youtube-transcript-api (external_docs/youtube_api.md)
- **Compliance**: Transcript policy (agen_docs/docs/TRANSCRIPT_POLICY.md)
- **Fallback**: ASR processing for missing captions

### Data Flow
```
YouTube URL → yt.py → transcript.jsonl → chunk.py → 
LLM (map/reduce) → export.py → artifacts → cache.py
```

## Development Status
- **Current Phase**: Planning and documentation
- **Next Phase**: M0 - Repository scaffold & tooling setup
- **Architecture**: Modular design with reusable core package
- **Testing**: TDD approach with pytest and golden fixtures

## File Categories Summary
- **Documentation**: 13 files (design, guides, policies)
- **Planning**: 8 files (WBS milestones)
- **Schemas**: 4 files (JSON schemas + SQL DDL)
- **External Docs**: 2 files (API documentation)
- **Notes**: 2 files (best practices, workflow)
- **Configuration**: 2 files (manifest, OpenAPI spec)

This mapping provides a comprehensive overview of the current project structure and planned architecture for the MindTube YouTube transcript processing system.