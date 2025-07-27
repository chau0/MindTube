# MindTube Project File Mapping (Updated)
**Generated:** 2025-01-27  
**Total Files:** 37 (excluding .git directory and temporary files)

## Project Overview
MindTube is a YouTube video transcript processing and summarization tool that extracts captions/transcripts from YouTube videos, processes them through LLM-based map-reduce pipelines, and generates structured summaries, notes, and mindmaps. The project is currently in the planning and documentation phase.

## Current Directory Structure & File Mapping

### 📁 Root Files
| File | Purpose | Category | Size (lines) |
|------|---------|----------|--------------|
| `PROJECT_FILE_MAPPING.md` | Comprehensive project file mapping | Documentation | 196 |

### 📁 Planning Documentation (`documents/plan/`)
Core project documentation and design specifications.

| File | Purpose | Category | Size (lines) | Dependencies |
|------|---------|----------|--------------|--------------|
| `documents/plan/README.md` | Main documentation index and quick start guide | Documentation | 13 | Links to all other plan docs |
| `documents/plan/design.md` | Comprehensive system architecture and design document | Architecture | 125 | Core design reference |
| `documents/plan/roadmap.md` | Development phases and timeline (CLI → API → Frontend) | Planning | 32 | References design.md |
| `documents/plan/wbs.md` | Work Breakdown Structure with detailed tasks and DoD | Planning | 63 | References roadmap.md |
| `documents/plan/tdd-playbook.md` | Test-driven development guidelines and practices | Development | 49 | Referenced by WBS |

### 📁 Current Work (`documents/doing/`)
Active milestone work in progress.

| File | Purpose | Category | Size (lines) | Status |
|------|---------|----------|--------------|--------|
| `documents/doing/WBS_M0.md` | M0: Repository scaffold & quality gates | Active Planning | 8 | In Progress |

### 📁 Future Milestones (`documents/todo/`)
Detailed milestone-based task breakdowns for project phases.

| File | Purpose | Category | Size (lines) | Dependencies |
|------|---------|----------|--------------|--------------|
| `documents/todo/WBS_M1.md` | M1: Core pipeline implementation | Planning | 8 | Depends on M0 |
| `documents/todo/WBS_M2.md` | M2: LLM integration and processing | Planning | 8 | Depends on M1 |
| `documents/todo/WBS_M3.md` | M3: Export and caching systems | Planning | 11 | Depends on M2 |
| `documents/todo/WBS_M4.md` | M4: API development | Planning | 9 | Depends on M3 |
| `documents/todo/WBS_M5.md` | M5: Frontend development | Planning | 8 | Depends on M4 |
| `documents/todo/WBS_M6.md` | M6: Testing and hardening | Planning | 7 | Cross-milestone |
| `documents/todo/WBS_M7.md` | M7: Deployment and operations | Planning | 7 | Final milestone |

### 📁 Agent Documentation (`documents/agen_docs/`)
AI agent-specific documentation and contracts for development assistance.

#### Core Agent Files
| File | Purpose | Category | Size (lines) | Dependencies |
|------|---------|----------|--------------|--------------|
| `documents/agen_docs/P0_P1_manifest.json` | Manifest listing all agent documentation files | Configuration | 22 | Lists all agen_docs files |
| `documents/agen_docs/openapi.yaml` | Complete API specification for MindTube API | API Contract | 147 | Referenced by API_README.md |

#### Agent Documentation (`documents/agen_docs/docs/`)
| File | Purpose | Category | Size (lines) | Dependencies |
|------|---------|----------|--------------|--------------|
| `documents/agen_docs/docs/AGENT_GUIDE.md` | Rules and conventions for AI agent contributors | Guidelines | 33 | References other docs |
| `documents/agen_docs/docs/API_README.md` | API contract overview and endpoint documentation | API Documentation | 14 | References openapi.yaml |
| `documents/agen_docs/docs/CONTRIBUTING.md` | Contribution guidelines for developers | Development | 10 | - |
| `documents/agen_docs/docs/COST_POLICY.md` | Token budgets and cost management policies | Operations | 17 | Referenced by AGENT_GUIDE.md |
| `documents/agen_docs/docs/DATA_MODEL.md` | Database schema and data structure definitions | Architecture | 42 | References ddl.sql |
| `documents/agen_docs/docs/ERRORS.md` | Error taxonomy and handling specifications | Development | 12 | Referenced by API_README.md |
| `documents/agen_docs/docs/LOCAL_HISTORY.md` | Local development and history management | Development | 8 | - |
| `documents/agen_docs/docs/OBSERVABILITY.md` | Logging, metrics, and monitoring specifications | Operations | 13 | Referenced by AGENT_GUIDE.md |
| `documents/agen_docs/docs/PROMPTS.md` | LLM prompt templates and versioning | AI/ML | 21 | Referenced by design.md |
| `documents/agen_docs/docs/QA_PLAN.md` | Quality assurance and testing strategy | Testing | 19 | - |
| `documents/agen_docs/docs/RUNBOOK.md` | Operational procedures and troubleshooting | Operations | 17 | - |
| `documents/agen_docs/docs/SECURITY.md` | Security guidelines and best practices | Security | 7 | - |
| `documents/agen_docs/docs/TRANSCRIPT_POLICY.md` | YouTube ToS compliance and transcript handling | Compliance | 14 | Referenced by AGENT_GUIDE.md |

#### Data Schemas (`documents/agen_docs/schemas/`)
| File | Purpose | Category | Size (lines) | Dependencies |
|------|---------|----------|--------------|--------------|
| `documents/agen_docs/schemas/map_schema.json` | JSON schema for map stage output validation | Data Schema | 46 | Used by pipeline.py |
| `documents/agen_docs/schemas/reduce_schema.json` | JSON schema for reduce stage output validation | Data Schema | 52 | Used by pipeline.py |
| `documents/agen_docs/schemas/validation_schema.json` | General validation schema definitions | Data Schema | 30 | Used across pipeline |

#### Database Schema (`documents/agen_docs/sql/`)
| File | Purpose | Category | Size (lines) | Dependencies |
|------|---------|----------|--------------|--------------|
| `documents/agen_docs/sql/ddl.sql` | SQLite database schema for videos, runs, artifacts, metrics | Database | 47 | Referenced by cache.py |

### 📁 Development Notes (`documents/notes/`)
Development best practices and workflow documentation.

| File | Purpose | Category | Size (lines) | Dependencies |
|------|---------|----------|--------------|--------------|
| `documents/notes/best_practice.md` | AI-assisted development best practices and tips | Development | 46 | - |
| `documents/notes/workflow.md` | High-level development workflow outline | Development | 7 | - |

### 📁 External Documentation (`documents/external_docs/`)
Third-party API documentation and integration guides.

| File | Purpose | Category | Size (lines) | Dependencies |
|------|---------|----------|--------------|--------------|
| `documents/external_docs/azure-ai.md` | OpenAI Python API library documentation for Azure integration | Integration | 858 | Referenced by llm/azure.py |
| `documents/external_docs/youtube_api.md` | YouTube Transcript API documentation and usage examples | Integration | 587 | Referenced by yt.py |

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
documents/plan/README.md → documents/plan/design.md → documents/plan/roadmap.md → documents/plan/wbs.md
                                    ↓
                           documents/todo/WBS_M*.md (milestone breakdowns)
```

### Agent Documentation Flow
```
documents/agen_docs/P0_P1_manifest.json → lists all agen_docs files
documents/agen_docs/docs/AGENT_GUIDE.md → references multiple policy docs
documents/agen_docs/openapi.yaml → defines API contract
documents/agen_docs/schemas/*.json → validate data structures
```

### Development Workflow
```
documents/notes/workflow.md → high-level process
documents/notes/best_practice.md → detailed guidelines
documents/plan/tdd-playbook.md → testing approach
```

## Key Integration Points

### LLM Integration
- **Azure OpenAI**: Primary provider (documents/external_docs/azure-ai.md)
- **Schemas**: map_schema.json, reduce_schema.json for output validation
- **Prompts**: Defined in documents/agen_docs/docs/PROMPTS.md

### YouTube Integration
- **API**: youtube-transcript-api (documents/external_docs/youtube_api.md)
- **Compliance**: Transcript policy (documents/agen_docs/docs/TRANSCRIPT_POLICY.md)
- **Fallback**: ASR processing for missing captions

### Data Flow
```
YouTube URL → yt.py → transcript.jsonl → chunk.py → 
LLM (map/reduce) → export.py → artifacts → cache.py
```

## Project Status Analysis

### Current Phase
- **Status**: Planning and documentation phase
- **Active Work**: M0 - Repository scaffold & quality gates (documents/doing/WBS_M0.md)
- **Next Phase**: Implementation of core pipeline (M1)

### File Organization
The project follows a clear documentation-first approach with:
- **Planning docs** in `documents/plan/` - high-level architecture and roadmap
- **Active work** in `documents/doing/` - current milestone tasks
- **Future work** in `documents/todo/` - upcoming milestone breakdowns
- **Agent support** in `documents/agen_docs/` - AI development assistance
- **Reference materials** in `documents/external_docs/` - third-party API docs

### Key Insights
1. **Well-structured documentation**: Comprehensive planning with clear dependencies
2. **Agent-assisted development**: Extensive AI agent documentation for development support
3. **Modular architecture**: Planned separation of CLI, API, and web frontend
4. **Quality focus**: TDD approach with comprehensive testing strategy
5. **Cost-conscious**: Budget constraints and token management policies

## Development Status
- **Current Phase**: Planning and documentation
- **Next Phase**: M0 - Repository scaffold & tooling setup
- **Architecture**: Modular design with reusable core package
- **Testing**: TDD approach with pytest and golden fixtures

## File Categories Summary
- **Planning & Design**: 5 files (design, roadmap, WBS, TDD playbook)
- **Active Work**: 1 file (current milestone)
- **Future Milestones**: 7 files (M1-M7 breakdowns)
- **Agent Documentation**: 15 files (guides, policies, schemas, SQL)
- **External References**: 2 files (API documentation)
- **Development Notes**: 2 files (best practices, workflow)
- **Configuration**: 2 files (manifest, OpenAPI spec)
- **Root Documentation**: 1 file (project mapping)

**Total: 37 files** organized in a clear hierarchical structure supporting documentation-driven development with AI assistance.