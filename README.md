# MindTube - YouTube Learning Assistant

A CLI tool and API for extracting transcripts, summaries, key ideas, and mindmaps from YouTube videos.

## Features

- 📝 **Transcript Extraction**: Automatic retrieval of video transcripts
- 📄 **Content Summarization**: AI-powered summarization of video content  
- 💡 **Key Ideas Extraction**: Identification of main concepts and takeaways
- 🗺️ **Mindmap Generation**: Visual representation in Mermaid format
- 🔧 **Multiple Interfaces**: CLI tool and REST API
- 💾 **Smart Caching**: Efficient storage and retrieval of processed content

## Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install mindtube

# Or install from source
git clone https://github.com/mindtube/mindtube.git
cd mindtube
make install-deps
```

### Configuration

```bash
# Set up Azure OpenAI credentials
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key"

# Or create config file
mindtube config init
```

### Usage

```bash
# Analyze a YouTube video
mindtube analyze https://youtu.be/VIDEO_ID

# Generate summary only
mindtube summarize https://youtu.be/VIDEO_ID

# Create mindmap
mindtube mindmap https://youtu.be/VIDEO_ID --save mindmap.md
```

## Development

### Setup

```bash
make init
make install-deps
make install-dev-deps
```

### Testing

```bash
make test
make lint
make typecheck
```

### API Server

```bash
make serve
```

## Documentation

- [CLI Guide](docs/cli/)
- [API Reference](docs/api/)
- [Configuration](docs/configuration.md)
- [Examples](docs/examples/)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for transcript extraction
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) for AI capabilities
- [Typer](https://typer.tiangolo.com/) for the CLI framework
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework