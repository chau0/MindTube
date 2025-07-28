# TASK-033: User Documentation

## Task Information
- **ID**: TASK-033
- **Phase**: 7 - Documentation & Deployment
- **Estimate**: 90 minutes
- **Dependencies**: TASK-023
- **Status**: 🔴 Backlog

## Description
Create comprehensive user documentation including installation guides, CLI usage examples, API tutorials, and troubleshooting guides. This ensures users can easily get started with MindTube and effectively use all its features.

## Acceptance Criteria
- [ ] Complete installation guide for multiple platforms
- [ ] CLI command reference with examples
- [ ] API usage tutorials with code samples
- [ ] Configuration guide
- [ ] Troubleshooting and FAQ section
- [ ] Video tutorials or demos
- [ ] Contributing guidelines

## Implementation Details

### Documentation Structure
```
docs/
├── README.md                 # Main project overview
├── installation/
│   ├── quick-start.md       # Quick installation guide
│   ├── detailed-setup.md    # Detailed setup instructions
│   ├── docker.md            # Docker installation
│   └── troubleshooting.md   # Installation troubleshooting
├── cli/
│   ├── overview.md          # CLI overview
│   ├── commands.md          # Command reference
│   ├── examples.md          # Usage examples
│   └── configuration.md     # CLI configuration
├── api/
│   ├── getting-started.md   # API quick start
│   ├── authentication.md    # API authentication
│   ├── endpoints.md         # Endpoint documentation
│   ├── examples/            # Code examples
│   └── rate-limits.md       # Rate limiting guide
├── guides/
│   ├── youtube-setup.md     # YouTube API setup
│   ├── azure-setup.md       # Azure OpenAI setup
│   ├── configuration.md     # Configuration guide
│   └── best-practices.md    # Best practices
└── contributing/
    ├── development.md       # Development setup
    ├── testing.md          # Testing guidelines
    └── code-style.md       # Code style guide
```

### Main README.md
```markdown
# MindTube - YouTube Learning Assistant

[![CI/CD](https://github.com/yourusername/mindtube/workflows/CI/badge.svg)](https://github.com/yourusername/mindtube/actions)
[![Coverage](https://codecov.io/gh/yourusername/mindtube/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/mindtube)
[![PyPI version](https://badge.fury.io/py/mindtube.svg)](https://badge.fury.io/py/mindtube)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A powerful CLI tool and REST API for extracting transcripts, summaries, key ideas, and mindmaps from YouTube videos using AI.

## ✨ Features

- 🎥 **YouTube Transcript Extraction** - Get accurate transcripts from any YouTube video
- 📝 **AI-Powered Summaries** - Generate concise summaries using Azure OpenAI
- 💡 **Key Ideas Extraction** - Identify and extract the most important concepts
- 🧠 **Interactive Mindmaps** - Create visual mindmaps in Mermaid format
- ⚡ **Fast CLI Interface** - Simple commands for quick analysis
- 🌐 **REST API** - Integrate with your applications
- 🔄 **Real-time Processing** - WebSocket support for live updates
- 📊 **Multiple Output Formats** - JSON, Markdown, HTML, and more

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install mindtube

# Or install from source
git clone https://github.com/yourusername/mindtube.git
cd mindtube
make install
```

### Basic Usage

```bash
# Analyze a YouTube video
mindtube analyze "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Generate summary only
mindtube summarize "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Create mindmap
mindtube mindmap "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output mindmap.md

# Start API server
mindtube serve --port 8000
```

### Configuration

```bash
# Set up Azure OpenAI
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_API_KEY="your-key"

# Or use configuration file
mindtube config set azure.endpoint "your-endpoint"
mindtube config set azure.api_key "your-key"
```

## 📖 Documentation

- [📥 Installation Guide](docs/installation/quick-start.md)
- [💻 CLI Reference](docs/cli/commands.md)
- [🌐 API Documentation](docs/api/getting-started.md)
- [⚙️ Configuration](docs/guides/configuration.md)
- [🤝 Contributing](docs/contributing/development.md)

## 🛠️ Development

```bash
# Clone and setup development environment
git clone https://github.com/yourusername/mindtube.git
cd mindtube
make init
make install-dev-deps

# Run tests
make test

# Start development server
make serve
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/contributing/development.md) for details.

## 📞 Support

- 📚 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/mindtube/issues)
- 💬 [Discussions](https://github.com/yourusername/mindtube/discussions)
```

### CLI Documentation
```markdown
# docs/cli/commands.md

# CLI Command Reference

## Global Options

All commands support these global options:

- `--config PATH` - Path to configuration file
- `--verbose, -v` - Enable verbose output
- `--quiet, -q` - Suppress output except errors
- `--output-format FORMAT` - Output format (json, yaml, markdown)
- `--help` - Show help message

## Commands

### analyze

Perform complete analysis of a YouTube video including transcript, summary, key ideas, and mindmap.

```bash
mindtube analyze [OPTIONS] VIDEO_URL
```

**Options:**
- `--output PATH` - Output file path
- `--format FORMAT` - Output format (json, markdown, html)
- `--include TEXT` - Include specific sections (summary, ideas, mindmap, transcript)
- `--exclude TEXT` - Exclude specific sections
- `--language CODE` - Preferred transcript language
- `--model TEXT` - AI model to use

**Examples:**
```bash
# Basic analysis
mindtube analyze "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Save to file
mindtube analyze "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output analysis.md

# Only summary and ideas
mindtube analyze "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --include summary,ideas

# Specific language
mindtube analyze "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --language es
```

### summarize

Generate a summary of a YouTube video.

```bash
mindtube summarize [OPTIONS] VIDEO_URL
```

**Options:**
- `--length TEXT` - Summary length (short, medium, long)
- `--style TEXT` - Summary style (bullet, paragraph, outline)
- `--output PATH` - Output file path

**Examples:**
```bash
# Quick summary
mindtube summarize "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Detailed summary
mindtube summarize "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --length long --style outline
```

### mindmap

Generate a mindmap from a YouTube video.

```bash
mindtube mindmap [OPTIONS] VIDEO_URL
```

**Options:**
- `--format TEXT` - Mindmap format (mermaid, text, json)
- `--depth INTEGER` - Maximum depth of mindmap
- `--output PATH` - Output file path

**Examples:**
```bash
# Generate mindmap
mindtube mindmap "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Save as Mermaid diagram
mindtube mindmap "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --format mermaid --output mindmap.md
```

### transcript

Extract transcript from a YouTube video.

```bash
mindtube transcript [OPTIONS] VIDEO_URL
```

**Options:**
- `--language CODE` - Preferred language
- `--format TEXT` - Output format (text, srt, vtt, json)
- `--timestamps` - Include timestamps

**Examples:**
```bash
# Get transcript
mindtube transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# With timestamps
mindtube transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --timestamps

# As SRT file
mindtube transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --format srt --output subtitles.srt
```

### config

Manage configuration settings.

```bash
mindtube config [COMMAND] [OPTIONS]
```

**Commands:**
- `get KEY` - Get configuration value
- `set KEY VALUE` - Set configuration value
- `list` - List all configuration
- `reset` - Reset to defaults

**Examples:**
```bash
# Set Azure OpenAI endpoint
mindtube config set azure.endpoint "https://your-resource.openai.azure.com/"

# Get current model
mindtube config get azure.model

# List all settings
mindtube config list
```

### serve

Start the REST API server.

```bash
mindtube serve [OPTIONS]
```

**Options:**
- `--host TEXT` - Host to bind to (default: localhost)
- `--port INTEGER` - Port to bind to (default: 8000)
- `--reload` - Enable auto-reload for development
- `--workers INTEGER` - Number of worker processes

**Examples:**
```bash
# Start server
mindtube serve

# Development mode
mindtube serve --reload --port 8080

# Production mode
mindtube serve --host 0.0.0.0 --workers 4
```
```

### API Documentation
```markdown
# docs/api/getting-started.md

# API Getting Started Guide

The MindTube API provides RESTful endpoints for analyzing YouTube videos programmatically.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API uses API key authentication:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/health
```

## Quick Start

### 1. Start the Server

```bash
mindtube serve --port 8000
```

### 2. Test Connection

```bash
curl http://localhost:8000/api/v1/health
```

### 3. Analyze a Video

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "include_sections": ["summary", "ideas"]
  }'
```

## Python SDK Example

```python
import requests

# Initialize client
base_url = "http://localhost:8000/api/v1"
headers = {"X-API-Key": "your-api-key"}

# Analyze video
response = requests.post(
    f"{base_url}/analyze",
    json={
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "include_sections": ["summary", "ideas", "mindmap"]
    },
    headers=headers
)

result = response.json()
print(result["summary"])
```

## WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws');

ws.onopen = function() {
    ws.send(JSON.stringify({
        action: 'analyze',
        video_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Progress:', data);
};
```

## Rate Limits

- Analysis endpoints: 10 requests per minute
- Transcript endpoints: 30 requests per minute
- Status endpoints: 100 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp
```

## Verification Steps
1. [ ] All documentation files created
2. [ ] README.md provides clear overview
3. [ ] Installation instructions are accurate
4. [ ] CLI examples work correctly
5. [ ] API documentation is complete
6. [ ] Code samples are tested
7. [ ] Links and references are valid
8. [ ] Documentation is well-organized

## Dependencies
- TASK-023 (CLI config commands) for CLI documentation
- All implementation tasks for accurate examples
- API endpoints for API documentation

## Notes
- Keep documentation synchronized with code changes
- Include troubleshooting for common issues
- Provide examples for different use cases
- Consider adding video tutorials for complex features