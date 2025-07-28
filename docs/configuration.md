# Configuration Guide

MindTube uses environment variables and configuration files to manage settings across different environments.

## Configuration Options

### Required Configuration

These environment variables are required for MindTube to function:

```bash
# Azure OpenAI Configuration (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
```

### Optional Configuration

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_VERSION=2024-02-15-preview  # Default: 2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo    # Default: gpt-35-turbo

# Cache Configuration
MINDTUBE_CACHE_ENABLED=true                  # Default: true
MINDTUBE_CACHE_DIR=~/.mindtube/cache         # Default: ~/.mindtube/cache
MINDTUBE_CACHE_TTL_HOURS=24                  # Default: 24

# Storage Configuration
MINDTUBE_OUTPUT_DIR=./output                 # Default: ./output
MINDTUBE_OUTPUT_FORMAT=json                  # Default: json (json|markdown|html)

# Processing Configuration
MINDTUBE_MAX_TRANSCRIPT_LENGTH=50000         # Default: 50000
MINDTUBE_REQUEST_TIMEOUT=30                  # Default: 30 (seconds)
MINDTUBE_MAX_RETRIES=3                       # Default: 3

# Logging Configuration
MINDTUBE_LOG_LEVEL=INFO                      # Default: INFO (DEBUG|INFO|WARNING|ERROR|CRITICAL)
MINDTUBE_LOG_FILE=./logs/mindtube.log        # Default: None (console only)
```

## Configuration Methods

### 1. Environment Variables

Set environment variables directly:

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key"
export MINDTUBE_LOG_LEVEL="DEBUG"
```

### 2. .env File

Create a `.env` file in your project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env
```

### 3. Environment-Specific Files

For different environments, you can use:

- `.env.local` - Local development overrides
- `.env.production` - Production settings
- `.env.test` - Test environment settings

## Usage Examples

### Basic Usage

```python
from mindtube.core.config import get_config

# Load configuration
config = get_config()

# Access configuration values
print(f"Endpoint: {config.azure_openai_endpoint}")
print(f"Cache enabled: {config.cache_enabled}")
print(f"Output directory: {config.output_dir}")
```

### Development Environment

```bash
# .env.development
AZURE_OPENAI_ENDPOINT=https://dev-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=dev-api-key
MINDTUBE_LOG_LEVEL=DEBUG
MINDTUBE_CACHE_ENABLED=false
MINDTUBE_OUTPUT_DIR=./dev-output
```

### Production Environment

```bash
# .env.production
AZURE_OPENAI_ENDPOINT=https://prod-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=prod-api-key
MINDTUBE_LOG_LEVEL=INFO
MINDTUBE_CACHE_TTL_HOURS=168  # 7 days
MINDTUBE_OUTPUT_DIR=/var/mindtube/output
MINDTUBE_LOG_FILE=/var/log/mindtube/app.log
```

## Validation

Configuration values are automatically validated:

- **Log Level**: Must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output Format**: Must be one of json, markdown, html
- **Positive Integers**: Cache TTL, max transcript length, timeout, and retries must be positive
- **Paths**: Automatically converted to Path objects with home directory expansion

## Common Issues

### Missing Required Variables

```
ValueError: AZURE_OPENAI_ENDPOINT environment variable is required
```

**Solution**: Ensure required environment variables are set.

### Invalid Values

```
ValueError: log_level must be one of ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
```

**Solution**: Use valid values as specified in the configuration options.

### Path Issues

```
Error: Cannot create cache directory
```

**Solution**: Ensure the user has write permissions for the specified directories.

## Security Best Practices

1. **Never commit .env files** - They contain sensitive credentials
2. **Use different API keys** for different environments
3. **Set appropriate file permissions** on configuration files:
   ```bash
   chmod 600 .env
   ```
4. **Use environment-specific configurations** rather than hardcoding values
5. **Regularly rotate API keys** and update configurations accordingly